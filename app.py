import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
from io import StringIO

st.set_page_config(page_title="CCAT Appraisal Tool", layout="wide")

# CCAT Domains
ccat_domains = [
    "Preliminaries",
    "Introduction",
    "Design",
    "Sampling",
    "Data Collection",
    "Ethical Matters",
    "Results",
    "Discussion"
]

st.title("📚 CCAT Critical Appraisal Tool")
st.markdown("Upload a journal article in PDF, read through, and manually assign scores (0–5) for each section.")

# PDF Upload
uploaded_file = st.file_uploader("📄 Upload PDF file", type=["pdf"])

# Text extraction
article_text = ""
if uploaded_file:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    for page in doc:
        article_text += page.get_text()
    st.success("✅ PDF uploaded and text extracted successfully!")

    with st.expander("📖 View Extracted Text"):
        st.text_area("Full Article Text", article_text, height=400)

    st.markdown("---")

    st.header("📝 Manual CCAT Scoring")
    scores = {}
    comments = {}

    with st.form("ccat_form"):
        for domain in ccat_domains:
            st.subheader(f"{domain}")
            scores[domain] = st.slider(f"Score for {domain}", 0, 5, 0, key=domain)
            comments[domain] = st.text_area(f"Comments on {domain}", key=f"{domain}_comment")

        submitted = st.form_submit_button("✅ Submit Scores")

    if submitted:
        df = pd.DataFrame({
            "Domain": ccat_domains,
            "Score (0-5)": [scores[d] for d in ccat_domains],
            "Comments": [comments[d] for d in ccat_domains]
        })

        total_score = sum(scores.values())
        max_score = len(ccat_domains) * 5
        percent = round((total_score / max_score) * 100, 2)

        st.markdown("---")
        st.subheader("📊 Appraisal Summary")
        st.dataframe(df, use_container_width=True)
        st.metric(label="Total Score", value=f"{total_score} / {max_score}")
        st.metric(label="Percent Score", value=f"{percent}%")

        csv = df.to_csv(index=False)
        st.download_button("⬇️ Download Results as CSV", csv, file_name="ccat_appraisal.csv", mime="text/csv")


