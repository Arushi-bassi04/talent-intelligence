from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')

SKILLS_DB = [
    "python","java","c++","react","node","sql",
    "machine learning","deep learning","flask","django",
    "docker","kubernetes","aws","api","javascript","mongodb"
]

def extract_skills(text):
    text = text.lower()
    return list(set([skill for skill in SKILLS_DB if skill in text]))

def compute_match(candidate_skills, job_skills):
    if not candidate_skills or not job_skills:
        return 0
    
    emb1 = model.encode([" ".join(candidate_skills)])
    emb2 = model.encode([" ".join(job_skills)])
    
    score = cosine_similarity(emb1, emb2)[0][0]
    return float(round(score * 100, 2))

def process_dataset(df, job_desc):
    job_skills = extract_skills(job_desc)
    results = []

    for idx, row in df.iterrows():
        candidate_skills = extract_skills(row['Resume_str'])
        score = compute_match(candidate_skills, job_skills)

        matched = list(set(candidate_skills) & set(job_skills))
        missing = list(set(job_skills) - set(candidate_skills))

        results.append({
            "id": idx,
            "score": score,
            "matched": matched,
            "missing": missing
        })

    results = sorted(results, key=lambda x: x['score'], reverse=True)
    return results[:5], job_skills