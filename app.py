import os
import google.generativeai as genai
import streamlit as st
import pdfplumber
from dotenv import load_dotenv
import json
from google.generativeai.types import HarmBlockThreshold
import docx2txt  # Use docx2txt instead of python-docx

load_dotenv()

# Configure Google Gemini with API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to extract text from uploaded PDF using pdfplumber
def extract_text_from_pdf(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Function to extract text from uploaded DOCX file using docx2txt
def extract_text_from_docx(uploaded_file):
    # Using docx2txt to extract text from docx
    text = docx2txt.process(uploaded_file)
    return text

# Function to get Gemini response and match percentage
def get_gemini_response(job_description, resume_text, prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    safety_settings = [{"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE}] 
    response = model.generate_content([job_description, resume_text, prompt], generation_config={"candidate_count": 1}, safety_settings=safety_settings)
    return response.text

# Function to calculate match percentage using semantic analysis
def calculate_match_percentage(job_description, resume_text):
    prompt = f"""
    You are an experienced ATS (Applicant Tracking System) expert. Your task is to evaluate the following resume and job description.
    Calculate the percentage match between the two, considering skills, experiences, and qualifications. Assign weights to the skills based on their importance as stated in the job description (Mandatory skills get higher weight).

    Job Description:
    {job_description}

    Resume:
    {resume_text}

    Provide a percentage of match between the job description and the resume.
    """
    return get_gemini_response(job_description, resume_text, prompt)

# Function to identify missing keywords from the resume based on the job description
def get_missing_keywords(job_description, resume_text):
    prompt = f"""
    You are an experienced recruiter. Based on the following job description and resume, identify the missing skills, qualifications, or keywords in the resume.

    Job Description:
    {job_description}

    Resume:
    {resume_text}

    Provide a list of missing keywords.
    """
    return get_gemini_response(job_description, resume_text, prompt)

# Load external CSS file for styling
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Streamlit UI Setup
st.title("HUBNEX LABS Resume Evaluator")
st.header("Evaluate Resume Against a Job Description")

input_text = st.text_area("Job Description:", key="input")
uploaded_file = st.file_uploader("Upload Your Resume (PDF or DOCX)...", type=["pdf", "docx"])

if uploaded_file is not None:
    file_type = uploaded_file.type
    if file_type == "application/pdf":
        st.write("PDF Resume Uploaded Successfully")
        resume_text = extract_text_from_pdf(uploaded_file)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        st.write("DOCX Resume Uploaded Successfully")
        resume_text = extract_text_from_docx(uploaded_file)

    st.text_area("Resume Text Extracted", value=resume_text, height=200)

submit_button = st.button("Evaluate Resume")

if submit_button:
    if uploaded_file is not None and input_text.strip():
        with st.spinner('Analyzing...'):
            # 1. Calculate match percentage using Gemini
            match_percentage = calculate_match_percentage(input_text, resume_text)
            
            # 2. Identify missing keywords using Gemini
            missing_keywords = get_missing_keywords(input_text, resume_text)

            # Display results
            st.subheader(f"Match Percentage: ")
            st.subheader(match_percentage.strip())
            st.write(f"Missing Keywords: {missing_keywords.strip()}")
            
    else:
        st.write("Please upload a resume and provide a job description.")
