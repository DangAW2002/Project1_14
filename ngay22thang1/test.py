from collections import Counter
import math

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

# Ví dụ sử dụng
string1 = "hello world"
string2 = "hello everyone in the world"
similarity = cosine_similar_notfidf(string1, string2)
print(f"Cosine Similarity: {similarity}")
