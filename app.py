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
        github_data = None
        if github_username:
            from utils import get_github_data
            github_data = get_github_data(github_username.strip())

            st.subheader("Your GitHub Analysis")

            # ✅ Show feedback so you know if GitHub fetch worked
            if github_data and github_data["repo_count"] > 0:
                st.success(
                    f"GitHub data fetched for **{github_username}**: "
                    f"{github_data['repo_count']} repos, "
                    f"languages: {', '.join(github_data['languages']) or 'none detected'}"
                )
            else:
                st.warning(
                    f"⚠️ Could not fetch GitHub data for **{github_username}**. "
                    "Check the username or token. Proceeding without GitHub data."
                )

            if github_data:
                st.write("Languages:", github_data.get("languages", []))
                st.write("Repositories:", github_data.get("repo_count", 0))

        top_candidates, job_skills = process_dataset(df, job_desc)

        st.subheader("Job Skills")
        st.write(job_skills)

        st.subheader("Top Candidates")

        for cand in top_candidates:
            st.markdown(f"### Candidate {cand['id']} — {cand['score']}%")

            # ✅ Show repo count alongside GitHub username
            github_display = cand.get("github", "Not Found")
            repo_count = cand.get("github_repos", 0)
            if github_display != "Not Found":
                st.write(f"🔗 GitHub: [{github_display}](https://github.com/{github_display}) — {repo_count} repos")
            else:
                st.write("🔗 GitHub: Not Found")

            col1, col2 = st.columns(2)

            with col1:
                st.write("Matched Skills")
                st.write(cand["matched"])

            with col2:
                st.write("Missing Skills")
                st.write(cand["missing"])

            st.write("Reasoning")
            st.write(
                f"Matched {len(cand['matched'])} skills "
                f"and missing {len(cand['missing'])} skills."
            )

            score = cand.get('score', 0)
            if score is None:
                score = 0

            progress_value = max(0, min(float(score) / 100, 1))
            st.progress(progress_value)

            st.divider()