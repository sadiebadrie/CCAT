import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
from openai import OpenAI

# Set up Streamlit page
st.set_page_config(page_title="CCAT Auto-Appraiser", layout="wide")
st.title("📚 CCAT Critical Appraisal Tool (v1.4) Auto-Appraiser")
st.markdown("Upload a journal article PDF. GPT-4 will analyze it and auto-score each CCAT v1.4 domain.")

# Initialize OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# CCAT domains
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

ccat_prompts = {
    "Preliminaries": "Evaluate the title, abstract, and general writing quality. Is it clear, concise, and detailed enough for reproduction?",
    "Introduction": "Does the introduction summarize current knowledge, identify the research problem, and state the study objectives or hypothesis?",
    "Design": "Assess the clarity and appropriateness of the research design, including details on interventions, measurements, and bias reduction.",
    "Sampling": "Was the sampling method suitable, explained, and justified? Were inclusion/exclusion criteria and sample size appropriate?",
    "Data Collection": "How were data collected? Were protocols clear, instruments reliable, and missing data handled well?",
    "Ethical Matters": "Did the study discuss ethics approval, informed consent, conflicts of interest, and researcher–participant relationships?",
    "Results": "Were data clearly presented and analyzed properly? Were limitations and bias acknowledged?",
    "Discussion": "Did the authors interpret findings appropriately, acknowledge bias and limitations, and assess generalisability?"
}

# File uploader
uploaded_file = st.file_uploader("📄 Upload a PDF file", type=["pdf"])

if uploaded_file:
    # Extract text from PDF
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    full_text = "\n".join([page.get_text() for page in doc])
    st.success("✅ PDF uploaded and text extracted.")

    with st.expander("📖 View Extracted Article Text"):
        st.text_area("Full Article Text", full_text, height=400)

    # Run GPT scoring
    st.header("🤖 AI-Generated CCAT Scores")
    scores = {}
    explanations = {}

    with st.spinner("Scoring all CCAT sections using GPT-4..."):
        for domain in ccat_domains:
            prompt = (
                f"You are a research appraiser using the Crowe Critical Appraisal Tool (CCAT) v1.4.\n"
                f"Based on the full article text below, appraise the '{domain}' domain.\n\n"
                f"Instructions: {ccat_prompts[domain]}\n\n"
                f"Text:\n{full_text}\n\n"
                f"Return in the format:\nScore: X\nExplanation: ..."
            )

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            result = response.choices[0].message.content.strip()

            try:
                score_line, explanation_line = result.split("\n", 1)
                score = int(score_line.replace("Score:", "").strip())
                explanation = explanation_line.replace("Explanation:", "").strip()
            except:
                score = 0
                explanation = "⚠️ GPT response formatting issue."

            scores[domain] = score
            explanations[domain] = explanation

    # Show results
    df = pd.DataFrame({
        "Domain": ccat_domains,
        "Score (0–5)": [scores[d] for d in ccat_domains],
        "Explanation": [explanations[d] for d in ccat_domains]
    })

    total = sum(scores.values())
    percent = round((total / 40) * 100)

    st.dataframe(df, use_container_width=True)
    st.markdown(f"### ✅ Total Score: {total}/40  📊 Validity Percentage: {percent}%")

    # Download results
    csv = df.to_csv(index=False)
    st.download_button("⬇️ Download Results as CSV", data=csv, file_name="ccat_results.csv", mime="text/csv")

    # Re-run option
    st.markdown("---")
    if st.button("🔁 Appraise Another Article"):
        st.experimental_rerun()
