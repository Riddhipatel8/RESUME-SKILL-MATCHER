from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
import fitz
import json
from streamlit_lottie import st_lottie

load_dotenv()

# Gemini 1.5 pro to get the ATS Score 
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input):
    generation_config = {
    "temperature": 0.3,
    "top_p": 0.9,
    "top_k": 20,
    "max_output_tokens": 4000,}
    model=genai.GenerativeModel(model_name='gemini-1.5-pro', generation_config=generation_config)
    response=model.generate_content(input)
    return response.text

# Extracting the pdf Content from the PDF files 
def extract_text_from_pdf(pdf_file):
    try:
        pdf_bytes = pdf_file.read()
        if not pdf_bytes:
            raise ValueError("Uploaded file is empty.")
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        return text
    except Exception as e:
        st.error(f"An error occurred while extracting text from the PDF: {e}")
        return ""
    
# Function to parse the JSON-like string response into a list of dictionaries
def parse_response(response_str):
    try:
        # Remove triple backticks and any leading/trailing whitespace
        cleaned_response = response_str.strip().strip('`')
        cleaned_response = cleaned_response.strip().strip('json')
        if not cleaned_response:
            return []  # Return empty list if cleaned_response is empty
        response_dict = json.loads(cleaned_response)
        table_data = [{"Aspect": key, "Details": value} for key, value in response_dict.items()]
        return table_data
    except json.JSONDecodeError as e:
        st.error(f"Error parsing JSON: {e}")
        return []
    
# Function to load Lottie animation files
def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)


# Streamlit App Code 
st.title("RESUME SKILL MATCHER")

st.markdown("<h1 style='font-size:24px;'>Unlock Your Resume's Potential: Get ATS Match Insights Instantly!</h1>", unsafe_allow_html=True)

#for putting job Description 
input_text=st.text_area("Job Description: ",key="input")

#for uploding the files
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
resume_content = ""
#Checking the files uploaded are 
if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")
    resume_content=extract_text_from_pdf(uploaded_file)   
    

# System prompts for review
input_prompt_for_review=f'''As an experienced Technical Human Resource Manager, your task is to review the provided resume, extracted from a PDF, against the specified job description. Your tasks are to:
1. Evaluate whether the candidate's profile aligns with the role.
2. Highlight the strengths and weaknesses of the applicant in relation to the job requirements.
Resume: {resume_content}
Job Description: {input_text}'''

# System prompts for Percenatge Score
input_prompt_for_percentage_score=f'''As an ATS analyst with expertise in technology, software engineering, data science, full stack web development, cloud engineering, cloud development, DevOps engineering, and big data engineering, evaluate resumes against job descriptions. Your tasks are to:
1. Assign a percentage match based on key criteria.
2. Identify missing keywords.
Use the following structure for the response:
{{"Job Description Match":"%","Missing Keywords":"","Candidate Summary":"","Experience":""}}
Resume: {resume_content}
Job Description: {input_text}'''

#Submit button 1
submit1 = st.button("Tell Me About the Resume")
#Submit button 2
submit2 = st.button("Percentage match")

if submit1:
    if uploaded_file is not None:        
        response=get_gemini_response(input_prompt_for_review)
        st.subheader("The Repsonse is")
        st.write(response)
    else:
        st.write("Please uplaod the resume")

elif submit2:
    # define the table_data as none
    table_data=None
    if uploaded_file is not None:
        response=get_gemini_response(input_prompt_for_percentage_score)        
        st.subheader("The Repsonse is")
        #st.write(response)    
        table_data = parse_response(response)
        # Display the table
        st.table(table_data)
    else:
        st.write("Please uplaod the resume")

    for item in table_data:
        if item["Aspect"] == "Job Description Match":
            job_match_value = int(item["Details"].strip('%'))

    # Determine which emoji to display based on the job match value
    if job_match_value < 60:
        lottie_path = "animation_files/crying.json"
    elif 60 <= job_match_value < 70:
        lottie_path = "animation_files/neutral.json"
    elif 70 <= job_match_value < 80:
        lottie_path = "animation_files/happy.json"
    else:  # 80 and above
        lottie_path = "animation_files/awesome.json"

    # Check if the file exists
    if not os.path.exists(lottie_path):
        st.error(f"File not found: {lottie_path}")
    else:
        # Load the Lottie animation
        lottie_animation=None
        lottie_animation = load_lottiefile(lottie_path)
        # Display the Lottie animation centered using columns
        col1, col2, col3 = st.columns([1, 1, 1])

        with col2:
            st_lottie(lottie_animation,width=100, height=100)


   
