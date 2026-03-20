from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from github import Github, GithubException
import re
import os


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

def get_github_data(username):
    # ✅ FIX 3: Specific exception handling so errors are visible
    try:
        g = Github()
        user = g.get_user(username)

        repos = list(user.get_repos())

        languages = {}
        repo_count = len(repos)

        for repo in repos:
            try:
                langs = repo.get_languages()
                for lang in langs:
                    languages[lang.lower()] = languages.get(lang.lower(), 0) + 1
            except GithubException:
                continue

        top_languages = sorted(languages, key=languages.get, reverse=True)

        return {
            "username": username,
            "languages": top_languages[:5],
            "repo_count": repo_count
        }

    except GithubException as e:
        print(f"[GitHub API Error] {username}: {e.status} - {e.data}")
        return {"username": username, "languages": [], "repo_count": 0}
    except Exception as e:
        print(f"[GitHub Unexpected Error] {username}: {e}")
        return {"username": username, "languages": [], "repo_count": 0}

def extract_github_from_text(text):
    match = re.search(r"github\.com/([A-Za-z0-9_-]+)", text)
    if match:
        return match.group(1)
    return None

def process_dataset(df, job_desc, github_data=None):
    job_skills = extract_skills(job_desc)
    results = []

    for idx, row in df.iterrows():
        resume_text = row['Resume_str']

        candidate_skills = extract_skills(resume_text)

        # Auto-detect GitHub username from resume text
        resume_github_username = extract_github_from_text(resume_text)
        local_github_data = None

        if resume_github_username:
            local_github_data = get_github_data(resume_github_username)

        # Do NOT override with manual GitHub here.
        # Each candidate should only use their own GitHub (if found in resume).

        # Determine which GitHub username to display
        if local_github_data and local_github_data.get("username"):
            display_github = local_github_data["username"]
        elif resume_github_username:
            display_github = resume_github_username
        else:
            display_github = "Not Found"

        # Merge GitHub languages into candidate skills
        if local_github_data and local_github_data.get("languages"):
            candidate_skills += local_github_data["languages"]

        candidate_skills = list(set(candidate_skills))

        score = compute_match(candidate_skills, job_skills)

        matched = list(set(candidate_skills) & set(job_skills))
        missing = list(set(job_skills) - set(candidate_skills))

        results.append({
            "id": idx,
            "score": score,
            "matched": matched,
            "missing": missing,
            "github": display_github,
            "github_repos": local_github_data["repo_count"] if local_github_data else 0
        })

    results = sorted(results, key=lambda x: x['score'], reverse=True)
    return results[:5], job_skills