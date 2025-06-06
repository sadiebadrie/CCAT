import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import openai

# ── 1) STREAMLIT PAGE CONFIG (MUST BE FIRST) ─────────────────────────────────
st.set_page_config(
    page_title="CCAT Auto-Appraiser",
    layout="wide"
)

# ── 2) DEBUG: Confirm the secret is loaded ─────────────────────────────────
# (Once confirmed, you can delete these lines.)
if "OPENAI_API_KEY" not in st.secrets:
    st.error("❌ OPENAI_API_KEY not found in secrets.toml!")
    st.stop()
else:
    st.success("🔐 OPENAI key loaded successfully.")

# ── 3) INITIALIZE OPENAI AFTER DEBUG ─────────────────────────────────────────
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ── 4) PAGE TITLE & DESCRIPTION ─────────────────────────────────────────────
st.title("📚 CCAT Critical Appraisal Tool (v1.4) Auto-Appraiser")
st.markdown(
    "Upload a journal article PDF below. GPT-4 will read it and automatically score each CCAT v1.4 domain."
)

# ── 5) CCAT DOMAINS & PROMPTS ─────────────────────────────────────────────────
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
    "Preliminaries": (
        "Evaluate the title, abstract, and general writing quality. "
        "Is it clear, concise, and detailed enough?"
    ),
    "Introduction": (
        "Does the introduction summarize current knowledge, identify the research problem, "
        "and state the study objectives or hypothesis?"
    ),
    "Design": (
        "Assess the clarity and appropriateness of the research design, "
        "including details on interventions, measurements, and bias reduction."
    ),
    "Sampling": (
        "Was the sampling method suitable, explained, and justified? "
        "Were inclusion/exclusion criteria and sample size appropriate?"
    ),
    "Data Collection": (
        "How were data collected? Were protocols clear, instruments reliable, "
        "and missing data handled well?"
    ),
    "Ethical Matters": (
        "Did the study discuss ethics approval, informed consent, conflicts of interest, "
        "and researcher–participant relationships?"
    ),
    "Results": (
        "Were data clearly presented and analyzed properly? Were limitations and bias acknowledged?"
    ),
    "Discussion": (
        "Did the authors interpret findings appropriately, acknowledge bias and limitations, "
        "and assess generalisability?"
    )
}

# ── 6) PDF UPLOADER ────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("📄 Upload a PDF file", type=["pdf"])

if uploaded_file:
    # Extract full text from the PDF
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    full_text = "\n".join([page.get_text() for page in doc])
    st.success("✅ PDF uploaded and text extracted.")

    # Optional: Let the user view the extracted text
    with st.expander("📖 View Extracted Article Text"):
        st.text_area("Full Article Text", value=full_text, height=300)

    # ── 7) AI-GENERATED CCAT SCORING ──────────────────────────────────────────
    st.header("🤖 AI-Generated CCAT Scores")
    scores = {}
    explanations = {}

    with st.spinner("Scoring all CCAT sections using GPT-4..."):
        for domain in ccat_domains:
            prompt = (
                f"You are a research appraiser using the Crowe Critical Appraisal Tool (CCAT) v1.4.\n"
                f"Based on the full article text below, appraise the '{domain}' domain.\n\n"
                f"Instructions: {ccat_prompts[domain]}\n\n"
                f"Article Text:\n{full_text}\n\n"
                f"Return in this format:\n"
                f"Score: X  (where X is an integer from 0 to 5)\n"
                f"Explanation: <two-to-three-sentence rationale>"
            )

            # Call OpenAI ChatCompletion (v0.27.0 syntax)
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            result = response.choices[0].message.content.strip()

            # Parse the lines "Score: X" and "Explanation: …"
            try:
                score_line, explanation_line = result.split("\n", 1)
                score = int(score_line.replace("Score:", "").strip())
                explanation = explanation_line.replace("Explanation:", "").strip()
            except:
                score = 0
                explanation = "⚠️ GPT response formatting issue."

            scores[domain] = score
            explanations[domain] = explanation

    # ── 8) DISPLAY RESULTS & DOWNLOAD ─────────────────────────────────────────
    df = pd.DataFrame({
        "Domain": ccat_domains,
        "Score (0–5)": [scores[d] for d in ccat_domains],
        "Explanation": [explanations[d] for d in ccat_domains]
    })

    total_score = sum(scores.values())
    percent_score = round((total_score / 40) * 100)

    st.dataframe(df, use_container_width=True)
    st.markdown(f"### ✅ Total Score: {total_score}/40  📊 Validity: {percent_score}%")

    csv = df.to_csv(index=False)
    st.download_button(
        "⬇️ Download Appraisal as CSV",
        data=csv,
        file_name="ccat_appraisal.csv",
        mime="text/csv"
    )

    # ── 9) “Appraise Another Article” BUTTON ──────────────────────────────────
    st.markdown("---")
    if st.button("🔁 Appraise Another Article"):
        st.experimental_rerun()
