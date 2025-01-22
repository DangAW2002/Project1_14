from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def levenshtein_distance(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            elif s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

    return dp[m][n]

def cosine_similarity_strings(s1, s2):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([s1, s2])
    return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

def kmp_search(text, pattern):
    def compute_lps(pattern):
        lps = [0] * len(pattern)
        length = 0
        i = 1
        while i < len(pattern):
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
        return lps

    lps = compute_lps(pattern)
    i = j = 0
    matches = []
    while i < len(text):
        if pattern[j] == text[i]:
            i += 1
            j += 1
        if j == len(pattern):
            matches.append(i - j)
            j = lps[j - 1]
        elif i < len(text) and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return matches

# Normalize scores to a scale (higher is better)
def calculate_scores(s1, s2, text, pattern):
    lev_distance = levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2))
    lev_score = 1 - lev_distance / max_len  # Normalize to [0, 1]

    cosine_score = cosine_similarity_strings(s1, s2)  # Already in [0, 1]

    kmp_matches = kmp_search(text, pattern)
    kmp_score = len(kmp_matches)  # Number of matches as score

    return {
        "Levenshtein Score": lev_score,
        "Cosine Similarity Score": cosine_score,
        "KMP Match Count": kmp_score
    }

# Input strings
s1 = "kitten"
s2 = "sitting"
s3 = "this is a sample document"
s4 = "this documentt iss aa sampleee"
pattern = "ababcd"
text = "ababcabcabababd"

# Calculate scores
scores = calculate_scores(s3, s4, text, pattern)

# Output results
for method, score in scores.items():
    print(f"{method}: {score}")
