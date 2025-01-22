from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher

def normalize_text(text):
    # Chuyển thành chữ thường và loại bỏ ký tự đặc biệt
    return ''.join(e.lower() for e in text if e.isalnum() or e.isspace())

def cosine_similarity_text(a, b):
    a, b = normalize_text(a), normalize_text(b)
    vectorizer = CountVectorizer().fit([a, b])
    vectors = vectorizer.transform([a, b])
    return cosine_similarity(vectors)[0, 1]
def similar(a, b):
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()
# Ví dụ sử dụng:
text1 = "chao"
text2 = "Chào mừng đến với thế giới"

print("Cosine Similarity:", cosine_similarity_text(text1, text2))
print("Similarity:", similar(text1, text2))