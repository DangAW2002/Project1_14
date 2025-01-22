import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import Levenshtein
from collections import Counter
from utils import load_data, data_path, similar
import unicodedata
from collections import Counter
import math
import json
from app_logging import error_logger
def cosine_similar_notfidf(string1, string2):
    # Tách các từ trong chuỗi
    words1 = string1.split()
    words2 = string2.split()
    
    # Đếm tần suất xuất hiện của từng từ
    freq1 = Counter(words1)
    freq2 = Counter(words2)
    
    # Tập hợp tất cả các từ duy nhất trong hai chuỗi
    all_words = set(freq1.keys()).union(set(freq2.keys()))
    
    # Tạo vector đặc trưng cho mỗi chuỗi
    vec1 = [freq1[word] for word in all_words]
    vec2 = [freq2[word] for word in all_words]
    
    # Tính tích vô hướng của hai vector
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    
    # Tính độ dài (magnitude) của từng vector
    magnitude1 = math.sqrt(sum(a ** 2 for a in vec1))
    magnitude2 = math.sqrt(sum(b ** 2 for b in vec2))
    
    # Tính độ tương đồng cosine
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0  # Nếu một trong hai vector là rỗng, trả về 0
    cosine_similarity = dot_product / (magnitude1 * magnitude2)
    return cosine_similarity

def similar_subsequence(a, b):
    return similar(a, b)

def similar_levenshtein(a, b):
    return 1 - (Levenshtein.distance(a, b) / max(len(a), len(b)))

# 1. Tính Cosine Similarity
def cosine_similarity_search(query, corpus):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([query] + corpus)
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
    return cosine_sim.flatten()

# 2. Tính Subsequence (sử dụng subsequence chung dài nhất)
def subsequence_search(query, corpus):
    return [similar(query, doc) for doc in corpus]

# 4. Tính Levenshtein Distance
def levenshtein_search(query, corpus):
    levenshtein_sim_normalized = []
    for doc in corpus:
        levenshtein_sim_normalized.append(similar_levenshtein(query, doc))
    return levenshtein_sim_normalized



def remove_diacritics(text):
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    return text.replace('đ', 'd').replace('Đ', 'D')

def fix_word(word, sentence):
    max_score = 0
    new_word = ""
    words = sentence.split()
    for w in words:
        score = similar_levenshtein(w, word)
        if score > max_score:
            max_score = score
            new_word = w
    # print(sentence)
    # print(f"Word: {word} - New Word: {new_word} - Score: {max_score}")
    return (new_word, max_score) if max_score >= 0.6 else (word, 0)

def fix_sentence(query, sentence):
    words = query.split()
    new_sentence = ""
    total_score = 0
    for word in words:
        new_word, score = fix_word(word, sentence)
        new_sentence += new_word + " "
        total_score += score
    # print(new_sentence)
    return new_sentence.strip(), total_score / len(words)

def search_data(query, arg_name, threshold_factor=0.2, Scaling_factor_recommend=0.5):
    data = load_data(data_path)
        # Ánh xạ arg_name
        
    arg_name_mapping = {
        'dev_id': 'devID',
        'dev_name': 'Name'
    }
    try:
        mapped_arg_name = arg_name_mapping.get(arg_name, arg_name)

        original_names = [entry[mapped_arg_name] for entry in data.values()]
        list_name_remove_diacritics = [remove_diacritics(name.lower()) for name in original_names]
        
        query_normalized = remove_diacritics(query.lower())

        print(f"Query normalized: {query_normalized}")
        cosine_sim = cosine_similarity_search(query_normalized, list_name_remove_diacritics)
        levenshtein_dist = levenshtein_search(query_normalized, list_name_remove_diacritics)

        # lấy top 20 từ cosine similarity và levenshtein distance
        scores = []
        for i in range(len(cosine_sim)):
            scores.append((cosine_sim[i] * 0.5 + levenshtein_dist[i] * 1.0)/1.5)
        list_name_and_scores = [(original_names[i], scores[i]) for i in range(len(scores))]
        list_name_and_scores_top20 = sorted(list_name_and_scores, key=lambda x: (-x[1], x[0]))[:20]
        
        # sửa lại câu query theo từng từ bằng levenshtein và tính toán lại top 20
        for i in range(len(list_name_and_scores_top20)):
            
            sentence, score = list_name_and_scores_top20[i]
            sentence_remove_diacritics = remove_diacritics(sentence.lower())
            new_sentence, score_fix = fix_sentence(query_normalized, sentence_remove_diacritics)
            score_cosine = cosine_similar_notfidf(new_sentence, sentence_remove_diacritics)
            score_levenshtein = similar_levenshtein(new_sentence, sentence_remove_diacritics)

            # Tính điểm mới dựa trên các phương pháp
            if mapped_arg_name == 'Name':
                new_score = ((score_cosine * 1.2 + score_levenshtein * 0.1 + score_fix * 0.2)/1.5)
            elif mapped_arg_name == 'devID':
                new_score = ((score_cosine * 0.0 + score_levenshtein * 0.0 + score_fix * 1.5)/1.5)
            # print(f"Old score: {score} - New score: {new_score}")
            list_name_and_scores_top20[i] = (sentence, new_score)

        # Tìm kiếm top1 
        list_name_and_scores_top20 = sorted(list_name_and_scores_top20, key=lambda x: (-x[1], x[0]))
        name_top1, score_top1 = list_name_and_scores_top20[0]
        name_top2, score_top2 = list_name_and_scores_top20[1]
        relative_superiority = (score_top1 - score_top2) / score_top2 if score_top2 != 0 else float('inf')
        print(f"Query: {query}")
        print(f"Arg name: {arg_name}")
        print(f"mapped_arg_name: {mapped_arg_name}")
        print(f"Top 1: {name_top1} - Score: {score_top1}")
        print(f"Top 2: {name_top2} - Score: {score_top2}")
        print(f"Relative Superiority: {relative_superiority}")

        most_similar = {}
        recommend = []
        # Tìm most similar và recommend
        if (score_top1 >= 0.4 and relative_superiority >= threshold_factor) or score_top1 >= 0.9:
            print(f"Most similar string: {name_top1}")
            most_similar = {'data': name_top1, 'score': score_top1}
        for i in range(len(list_name_and_scores_top20)):
            name, score = list_name_and_scores_top20[i]
            scaling_factor = score_top1 / (Scaling_factor_recommend + 1)
            if score >= scaling_factor:
                recommend.append({'data': name, 'score': score})
        if most_similar:
            recommend = [item for item in recommend if item['data'] != most_similar['data']]
        print("Recommend:")
        for item in recommend:
            print(f"{item['data']} - Score: {item['score']}")
    except Exception as e:
        error_logger.error(f"Error loading data: {e}")
        return json.dumps({"error": "Failed to load data"}, ensure_ascii=False)
    return most_similar, recommend

# Tìm kiếm dữ liệu
# search_data("fz 98503","dev_id", threshold_factor=0.2, threshold_recommend=0.3)
# a = "zxcvbnm"
# b = "zx                                             vbnm"
# most_similar, recommend = search_data("Lê Duẩn Y Wang","dev_name", threshold_factor=0.2, threshold_recommend=0.3)
# print(subsequence_search(a, [b]))
# print(most_similar)