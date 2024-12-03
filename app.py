import os
import streamlit as st
import pdfplumber
import docx2txt
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Gemini with API key
genai.configure(api_key="AIzaSyCKzbgEY93vkwWfk_oW8k5jCpGjC9-4T9s")

# Function to extract text from uploaded PDF
def extract_text_from_pdf(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        text = "".join(page.extract_text() for page in pdf.pages)
    return text

# Function to extract text from uploaded DOCX
def extract_text_from_docx(uploaded_file):
    return docx2txt.process(uploaded_file)

# Function to generate AI response (e.g., match percentage or missing keywords)
def get_gemini_response(prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt, generation_config={"candidate_count": 1,"temperature": 0})
    return response.text.strip()

# Custom background styling
def add_background():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Main Streamlit App
def main():
    add_background()  # Apply custom CSS
    st.markdown("<div class='title'>Resume Evaluator</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Evaluate resumes against job descriptions easily</div>", unsafe_allow_html=True)

    # Input Section
    job_description = st.text_area("Enter Job Description:")
    uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
    evaluate_button = st.button("Evaluate")

    if evaluate_button and job_description and uploaded_file:
        # Extract resume text
        file_type = uploaded_file.type
        if file_type == "application/pdf":
            resume_text = extract_text_from_pdf(uploaded_file)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            resume_text = extract_text_from_docx(uploaded_file)
        else:
            st.error("Unsupported file format")
            return

        # Display extracted resume text
        st.markdown("### Extracted Resume Text")
        st.text_area("", value=resume_text, height=200)

        # Generate AI Responses
        with st.spinner("Analyzing..."):
            match_prompt = f"""
                You are an ATS (Applicant Tracking System) expert. Your task is to evaluate the following resume against the provided job description.  

                Specifically:  
                    1. Assess the alignment of skills, qualifications, and experiences mentioned in the resume with those required in the job description.  
                    2. Assign a percentage match based on the relevance and completeness of the candidate's profile compared to the job requirements.  
                    3. Mandatory or highly emphasized skills in the job description should carry more weight in the calculation.  

                Ensure the response is short, clear, and no more than 300 words. Provide the output strictly in the following format:  

                **Output Format**:  
                **Match Percentage**: Calculated_percentage%  

                **Breakdown of Evaluation**:  
                1. **Skills Match**:  
                   - Total skills in job description: number 

                2. **Experience Match**:  
                   

                3. **Qualifications Match**:  
                    

                4. **Overall Match Evaluation**:  
                   
                    Job Description:  
                        {job_description}  

                        Resume:  
                            {resume_text}
                    """

            match_percentage = get_gemini_response(match_prompt)

            keywords_prompt = f"""
                Identify missing skills or keywords in this resume based on the job description and make it short and precise not more than 300 words.
                **Output Format**:  
                    1. **Missing Skills**:  
                        -
                        -
                    2.  **Missing Qualifications**:  
                        -
                        -
                    3. **Missing Keywords**:  
                        -
                        -
                Job Description:
                {job_description}

                Resume:
                {resume_text}
            """
            missing_keywords = get_gemini_response(keywords_prompt)

        # Display Results
        st.subheader(match_percentage.strip())
        st.markdown("### Missing Keywords:")
        st.write(missing_keywords)

    elif evaluate_button:
        st.error("Please provide both a job description and a resume.")

    # Footer
    st.markdown("<div class='footer'>Powered by HUBNEX LAB | Resume Evaluator</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
