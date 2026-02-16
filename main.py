import streamlit as st
import google.generativeai as genai

from pypdf import PdfReader
import docx
import os

if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Missing API Key! Please set GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

st.set_page_config(
    page_title="AI Resume ATS Scorer",
    page_icon="📄",
    layout="centered"
)

st.markdown("""
    <style>
        body {
            background-color: #f5f7fb;
        }

        .main-title {
            font-size: 40px;
            font-weight: bold;
            color: #2E3A59;
            text-align: center;
        }

        .sub-text {
            text-align: center;
            font-size: 18px;
            color: #555;
        }

        .stButton button {
            background-color: #4A90E2;
            color: white;
            font-size: 18px;
            border-radius: 12px;
            padding: 10px 20px;
            border: none;
        }

        .stButton button:hover {
            background-color: #357ABD;
            color: white;
        }

        .result-box {
            background: white;
            padding: 20px;
            border-radius: 15px;
            border: 2px solid #4A90E2;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'> AI Resume ATS Optimizer</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-text'>Upload your resume and test it against multiple job descriptions.</div>", unsafe_allow_html=True)

st.write("")

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
    uploaded_file = st.file_uploader(
        "Upload PDF or DOCX",
        type=["pdf", "docx"]
    )

    if uploaded_file:
        st.success(" Resume Loaded Successfully!")

jd_input = st.text_area(
    " Paste Job Description Here:",
    height=250
)

if st.button("🚀 Analyze Resume"):
    if not uploaded_file:
        st.error("Please upload a resume first!")
    elif not jd_input.strip():
        st.warning("Please paste a Job Description.")
    else:
        with st.spinner(" Comparing Resume with Job Description..."):
            resume_text = extract_text(uploaded_file)

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

            response = model.generate_content(prompt)
            
            st.markdown("---")
            st.subheader(" Results for this JD")
            st.markdown(response.text)


