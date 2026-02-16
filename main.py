import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import docx
import os

st.set_page_config(
    page_title="AI Resume ATS Scorer",
    page_icon="📄",
    layout="centered"
)

if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")
else:
    st.error("Missing API Key! Please add GEMINI_API_KEY to your Streamlit Secrets.")
    st.stop()

st.markdown("""
    <style>
        body { background-color: #f5f7fb; }
        .main-title { font-size: 40px; font-weight: bold; color: #2E3A59; text-align: center; }
        .sub-text { text-align: center; font-size: 18px; color: #555; }
        .stButton button {
            background-color: #4A90E2; color: white; font-size: 18px;
            border-radius: 12px; padding: 10px 20px; border: none; width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'> AI Resume ATS Optimizer</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-text'>Upload your resume and test it against job descriptions.</div>", unsafe_allow_html=True)

def extract_text(uploaded_file):
    text = ""
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text() or ""
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text

with st.sidebar:
    st.header(" Upload Resume")
    uploaded_file = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"])
    if uploaded_file:
        st.success("Resume Loaded Successfully!")

# --- MAIN UI ---
jd_input = st.text_area("Paste Job Description Here:", height=250)

if st.button(" Analyze Resume"):
    if not uploaded_file or not jd_input.strip():
        st.error("Please provide both a resume and a job description.")
    else:
        with st.spinner("Analyzing your resume against the JD..."):
            resume_text = extract_text(uploaded_file)

            if len(resume_text.strip()) < 10:
                st.error("Could not extract enough text. Is the PDF a scanned image?")
                st.stop()

            prompt = f"""
            Act as an advanced ATS (Applicant Tracking System).
            Analyze the following resume against the job description.

            JOB DESCRIPTION:
            {jd_input}

            RESUME:
            {resume_text}

            Provide a response with:
            - Overall Score (Percentage)
            - Keyword Match (Missing high-priority skills)
            - Format Review
            - Increasing Your Score (3 actionable bullet points)
            """

            try:
                response = model.generate_content(prompt)
                
                if response and response.text:
                    st.markdown("---")
                    st.subheader(" Results for this JD")
                    st.markdown(response.text)
                else:
                    st.warning("The AI returned an empty response. Please try again.")
            
            except Exception as e:
                st.error(f"AI Analysis Failed: {e}")
                st.info("Check if your API Key is valid and the model 'gemini-2.5-flash' is accessible.")