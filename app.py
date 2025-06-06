import streamlit as st

# ── 1) STREAMLIT PAGE CONFIG (MUST BE FIRST) ───────────────────────────────
st.set_page_config(page_title="Secret Check", layout="wide")

# ── 2) Check for OPENAI_API_KEY in st.secrets ───────────────────────────────
if "OPENAI_API_KEY" in st.secrets:
    # Reveal just the first 6 characters (so you can confirm it’s the right key,
    # but without exposing the full string)
    key_preview = st.secrets["OPENAI_API_KEY"][:6] + "..."
    st.success(f"🔐 OPENAI_API_KEY found! Key starts with: {key_preview}")
else:
    st.error("❌ OPENAI_API_KEY NOT found in Streamlit secrets!")
