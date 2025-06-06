import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import openai
import os

# Set up the page
st.set_page_config(page_title="CCAT Auto-Appraiser", layout="wide")
st.title("📚 Crowe Critical Appraisal Tool (CCAT v1.4)")
st.markdown("Upload a journal article PDF and automatically generate CCAT v1.4 scores using GPT-4.")

# Load API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Define CCAT categories
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

# Domain-specific instructions based on the CCAT v1.4 guide
ccat_prompts = {
    "Preliminaries": "Evaluate whether the title, abstract, and general writing style of the paper meet CCAT standards. Score from 0 to 5.",
    "Introduction": "Does the introduction summarize current knowledge, state specific problems, and outline clear objectives or hypotheses?",
    "Design": "Assess the suitability and clarity of the research design, interventions, outcome measures, and bias minimization strategies.",
    "Sampling": "Was the sampling method well-chosen, described, and justified? Consider inclusion/exclusion criteria and sample size rationale.",
    "Data Collection": "Evaluate how data was collected, including protocols, instruments, and quality assurance processes.",
    "Ethical Matters": "Check if ethics approval, informed consent, conflict of interest, and researcher relationships are addressed.",
    "Results": "Are the data clearly presented, analyzed correctly, and limitations acknowledged? Assess interpretation accuracy and completeness.",
    "Discussion": "Did the discussion align results with objectives, account for bias, and mention generalizability and study limitations?"
}

# PDF Upload
uploaded_file = st.file_uploader("📄 Upload a PDF file", type=["pdf"])
if uploaded_file:
    # Extract PDF text
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    full_text = "\n".join([page.get_text() for page in doc])

    st.success("✅ PDF text extracted successfully.")
    with st.expander("📖 View Extracted Article Text"):
        st.text_area("Article Content", value=full_text, height=400)

    # Ask GPT-4 to evaluate each section
    st.header("🤖 AI-Generated CCAT Scores")
    scores = {}
    explanations = {}

    with st.spinner("Generating CCAT scores with GPT-4..."):
        for domain in ccat_domains:
            prompt = (
                f"You are a research appraiser using the Crowe Critical Appraisal Tool (CCAT) v1.4.\n"
                f"Based on the full article text below, appraise the '{domain}' domain.\n\n"
                f"Instructions: {ccat_prompts[domain]}\n\n"
                f"Text:\n{full_text}\n\n"
                f"Give:\n1. A score from 0 to 5\n2. A brief explanation (2–3 lines max)\n"
                f"Format your response like:\nScore: X\nExplanation: ...\n"
            )
           client = openai.OpenAI()

chat_response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3
)
result = chat_response.choices[0].message.content.strip()
            try:
                score_line, explanation_line = result.split("\n", 1)
                score = int(score_line.replace("Score:", "").strip())
                explanation = explanation_line.replace("Explanation:", "").strip()
            except:
                score = 0
                explanation = "Error: Could not parse GPT response."

            scores[domain] = score
            explanations[domain] = explanation

    # Display results
    df = pd.DataFrame({
        "Domain": ccat_domains,
        "Score (0–5)": [scores[d] for d in ccat_domains],
        "Explanation": [explanations[d] for d in ccat_domains]
    })

    total_score = sum(scores.values())
    percent_score = round((total_score / 40) * 100)

    st.dataframe(df, use_container_width=True)
    st.markdown(f"### ✅ Total Score: {total_score} / 40  |  Percent: {percent_score}%")

    # Download CSV
    csv = df.to_csv(index=False)
    st.download_button("⬇️ Download Appraisal as CSV", data=csv, file_name="ccat_appraisal.csv", mime="text/csv")

    # Reset option
    st.markdown("---")
    if st.button("🔁 Upload another article"):
        st.experimental_rerun()
