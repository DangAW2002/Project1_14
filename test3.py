import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import Levenshtein
from collections import Counter

# 1. Tính Cosine Similarity
def cosine_similarity_search(query, corpus):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([query] + corpus)
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
    return cosine_sim.flatten()

# 2. Tính Subsequence (sử dụng subsequence chung dài nhất)
def subsequence_search(query, corpus):
    def longest_common_subsequence(str1, str2):
        # Hàm tìm subsequence chung dài nhất giữa hai chuỗi
        m, n = len(str1), len(str2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m):
            for j in range(n):
                if str1[i] == str2[j]:
                    dp[i + 1][j + 1] = dp[i][j] + 1
                else:
                    dp[i + 1][j + 1] = max(dp[i + 1][j], dp[i][j + 1])
        return dp[m][n]

    return [longest_common_subsequence(query, doc) for doc in corpus]

# 3. Tính Jaccard Similarity
def jaccard_similarity_search(query, corpus):
    def jaccard(set1, set2):
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union != 0 else 0.0

    query_set = set(query.split())
    return [jaccard(query_set, set(doc.split())) for doc in corpus]

# 4. Tính Levenshtein Distance
def levenshtein_search(query, corpus):
    return [Levenshtein.distance(query, doc) for doc in corpus]

# Chuẩn hóa điểm số
def normalize_scores(cosine_sim, subsequence_sim, jaccard_sim, levenshtein_dist, query, corpus):
    # Cosine similarity đã trong phạm vi [0, 1]
    # Subsequence: chia cho độ dài chuỗi lớn nhất
    subsequence_max_length = max([len(query)] + [len(doc) for doc in corpus])
    subsequence_sim_normalized = [score / subsequence_max_length for score in subsequence_sim]
    
    # Levenshtein: chuẩn hóa về phạm vi [0, 1]
    levenshtein_max_length = max([len(query)] + [len(doc) for doc in corpus])
    levenshtein_sim_normalized = [1 - (score / levenshtein_max_length) for score in levenshtein_dist]

    # Tạo danh sách điểm số
    normalized_scores = {
        'Cosine Similarity': cosine_sim,
        'Subsequence Similarity': subsequence_sim_normalized,
        'Jaccard Similarity': jaccard_sim,
        'Levenshtein Similarity': levenshtein_sim_normalized
    }

    return normalized_scores

# Ví dụ sử dụng các thuật toán tìm kiếm mờ
def fuzzy_search(query, corpus):
    cosine_sim = cosine_similarity_search(query, corpus)
    subsequence_sim = subsequence_search(query, corpus)
    jaccard_sim = jaccard_similarity_search(query, corpus)
    levenshtein_dist = levenshtein_search(query, corpus)

    # Chuẩn hóa điểm số
    results = normalize_scores(cosine_sim, subsequence_sim, jaccard_sim, levenshtein_dist, query, corpus)

    return results

# Dữ liệu ví dụ
corpus = [
    "I love programming",
    "I love python programming",
    "Python is great for data science",
    "I enjoy writing code"
]

query = "love python"

# Kết quả tìm kiếm
results = fuzzy_search(query, corpus)

# In kết quả
for method, result in results.items():
    print(f"{method}: {result}")
