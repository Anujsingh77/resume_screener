"""
NLP processing: skill extraction using spaCy/NLTK + TF-IDF similarity via scikit-learn.
"""

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── Common tech / soft skills keyword list ──────────────────────────────────
SKILL_KEYWORDS = {
    # Programming languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "kotlin", "swift", "ruby", "php", "scala", "r", "matlab",
    # Web & frameworks
    "react", "angular", "vue", "node.js", "django", "flask", "fastapi",
    "spring", "express", "next.js", "html", "css", "rest", "graphql",
    # Data & ML
    "machine learning", "deep learning", "nlp", "natural language processing",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
    "data analysis", "data science", "statistics", "sql", "nosql",
    "tableau", "power bi", "spark", "hadoop", "etl",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "jenkins",
    "terraform", "linux", "git", "github", "devops",
    # Databases
    "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "oracle",
    # Soft skills
    "communication", "leadership", "teamwork", "problem solving",
    "project management", "agile", "scrum",
    # Other
    "api", "microservices", "blockchain", "cybersecurity", "testing",
    "junit", "selenium", "figma", "jira", "confluence",
}


def preprocess(text: str) -> str:
    """Lowercase and normalise text."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s\.\+#]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_skills(text: str) -> list[str]:
    """
    Extract skills from text using two methods:
    1. Keyword matching against SKILL_KEYWORDS list
    2. spaCy noun-chunk extraction (if available)
    """
    text_lower = preprocess(text)
    found = set()

    # Method 1: keyword matching
    for skill in SKILL_KEYWORDS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.add(skill)

    # Method 2: spaCy NER / noun chunks (if available)
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            nlp = None

        if nlp:
            doc = nlp(text[:5000])  # limit for performance
            for chunk in doc.noun_chunks:
                chunk_text = chunk.text.lower().strip()
                if 2 < len(chunk_text) < 40 and chunk_text in SKILL_KEYWORDS:
                    found.add(chunk_text)
    except ImportError:
        pass

    return sorted(found)


def compute_tfidf_score(job_description: str, resume_text: str) -> float:
    """
    Compute cosine similarity between job description and resume
    using TF-IDF vectors (scikit-learn).
    Returns a float between 0 and 1.
    """
    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000
        )
        tfidf_matrix = vectorizer.fit_transform([
            preprocess(job_description),
            preprocess(resume_text)
        ])
        score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(score), 4)
    except Exception:
        return 0.0
