import streamlit as st
import pandas as pd
from utils import process_dataset

st.set_page_config(page_title="Talent Intelligence AI", layout="wide")

st.title("pip AI Talent Intelligence System")

df = pd.read_csv("data/resumes.csv")

job_desc = st.text_area("Paste Job Description")

if st.button("Analyze Candidates"):
    
    if job_desc.strip() == "":
        st.warning("Enter job description")
    else:
        top_candidates, job_skills = process_dataset(df, job_desc)

        st.subheader("Job Skills")
        st.write(job_skills)

        st.subheader("Top Candidates")

        for cand in top_candidates:
            st.markdown(f"### Candidate {cand['id']} — {cand['score']}%")

            col1, col2 = st.columns(2)

            with col1:
                st.write("Matched Skills")
                st.write(cand["matched"])

            with col2:
                st.write("Missing Skills")
                st.write(cand["missing"])

            st.write("Reason")
            st.write(
                f"Matched {len(cand['matched'])} skills "
                f"and missing {len(cand['missing'])} skills."
            )

            score = cand.get('score', 0)

            if score is None:
                score = 0

            progress_value = float(score) / 100

            # Clamp between 0 and 1
            progress_value = max(0, min(progress_value, 1))

            st.progress(progress_value)

            st.divider()