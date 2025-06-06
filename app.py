import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

# 1) Streamlit configuration
st.set_page_config(page_title="CCAT Manual Appraiser", layout="wide")
st.title("📚 CCAT Critical Appraisal Tool (v1.4)")
st.markdown(
    "Upload a journal article PDF, read it, and manually assign scores (0–5) "
    "for each of the 8 CCAT domains. Then download your results as a CSV."
)

# 2) CCAT domains and instructions
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
ccat_instructions = {
    "Preliminaries": "Evaluate title, abstract, and general writing quality: clarity, detail, reproducibility.",
    "Introduction": "Does the introduction summarize current knowledge, define the problem, and state objectives?",
    "Design": "Assess appropriateness and clarity of research design, interventions/measures, and bias reduction.",
    "Sampling": "Was the sampling method suitable and justified? Were criteria and sample size explained?",
    "Data Collection": "Evaluate protocols, instruments, data handling, missing data, and quality assurance.",
    "Ethical Matters": "Check ethics approval, informed consent, conflicts of interest, researcher–participant relationships.",
    "Results": "Are data clearly presented and analyzed? Are limitations and bias acknowledged?",
    "Discussion": "Did authors interpret findings appropriately, acknowledge bias, limitations, and generalizability?"
}

# 3) PDF uploader
uploaded_file = st.file_uploader("📄 Upload a PDF file", type=["pdf"])
if uploaded_file:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    full_text = "\n".join([page.get_text() for page in doc])
    st.success("✅ PDF uploaded and text extracted.")
    with st.expander("📖 View Extracted Article Text"):
        st.text_area("Full Article Text", full_text, height=300)

    st.header("📝 Manual CCAT Scoring")
    scores = {}
    comments = {}
    with st.form("ccat_form"):
        for domain in ccat_domains:
            st.subheader(f"{domain}")
            st.write(ccat_instructions[domain])
            scores[domain] = st.slider(f"Score for {domain}", 0, 5, 0, key=domain)
            comments[domain] = st.text_area(f"Comments on {domain}", key=f"{domain}_comment")
        submitted = st.form_submit_button("✅ Submit Scores")
    if submitted:
        df = pd.DataFrame({
            "Domain": ccat_domains,
            "Score (0–5)": [scores[d] for d in ccat_domains],
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
        st.markdown("---")
        if st.button("🔁 Appraise Another Article"):
            st.experimental_rerun()
