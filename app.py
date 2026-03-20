import streamlit as st
import pandas as pd
from utils import process_dataset

st.set_page_config(page_title="Talent Intelligence AI", layout="wide")

st.title("AI Talent Intelligence System")

df = pd.read_csv("data/resumes.csv")

job_desc = st.text_area("Paste Job Description")
github_username = st.text_input("Enter GitHub Username (optional)")

if st.button("Analyze Candidates"):
    
    if job_desc.strip() == "":
        st.warning("Enter job description")

    else:
        from utils import get_github_data, extract_skills, compute_match

        job_skills = extract_skills(job_desc)

        # 🟩 MODE 2: GitHub Evaluation
        if github_username:
            github_data = get_github_data(github_username.strip())

            st.subheader("GitHub Candidate Evaluation")

            if github_data and github_data["repo_count"] > 0:
                st.success(f"GitHub: {github_username}")

                github_skills = github_data["languages"]

                score = compute_match(github_skills, job_skills)

                st.write("GitHub Skills:", github_skills)
                st.write("Job Skills:", job_skills)
                st.write(f"Match Score: {score}%")

                progress_value = max(0, min(float(score)/100, 1))
                st.progress(progress_value)

                if score > 70:
                    st.success("Strong Candidate")
                elif score > 40:
                    st.warning("Moderate Match")
                else:
                    st.error("Weak Match")

            else:
                st.warning("Could not fetch GitHub data")

        # 🟦 MODE 1: Dataset Ranking
        else:
            top_candidates, job_skills = process_dataset(df, job_desc)

            st.subheader("Top Candidates")

            for cand in top_candidates:
                st.markdown(f"### Candidate {cand['id']} — {cand['score']}%")
                st.write("Matched:", cand["matched"])
                st.write("Missing:", cand["missing"])

            score = cand.get('score', 0)
            if score is None:
                score = 0

            progress_value = max(0, min(float(score) / 100, 1))
            st.progress(progress_value)

            st.divider()