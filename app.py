from flask import Flask, render_template, request
from PyPDF2 import PdfReader
import spacy
import pandas as pd

app = Flask(__name__)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Load dataset
df = pd.read_csv("SoftwareProfessionalExtra.csv")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to extract skills
def ExtractinSkills(text, JobRoles):
    all_skills = set()
    for roles in df[JobRoles]:
        all_skills.update(roles.split(", "))
    doc = nlp(text)
    return list(set([token.text for token in doc if token.text in all_skills]))

# Function to match roles and companies
def match_roles_and_companies(skills, df):
    df['Combined'] = df['Job Roles'] + ", " + df['Job Title']
    df['Matching_Skills'] = df['Job Roles'].apply(lambda x: len(set(x.split(", ")) & set(skills)))
    df['Skill_Match_Percentage'] = (df['Matching_Skills'] / df['Job Roles'].str.split(", ").apply(len)) * 100
    return df.sort_values(by='Skill_Match_Percentage', ascending=False)[['Company Name', 'Job Title', 'Salary', 'Location', 'Skill_Match_Percentage']]

# Home page route
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle resume upload and sorting
@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return 'No file part'
    
    file = request.files['resume']
    
    if file.filename == '':
        return 'No selected file'
    
    if file:
        # Save the uploaded file temporarily
        resume_path = "uploaded_resume.pdf"
        file.save(resume_path)
        
        # Extract text from the PDF
        resume_text = extract_text_from_pdf(resume_path)
        
        # Extract skills from resume
        skills = ExtractinSkills(resume_text, "Job Roles")
        
        # Match roles and companies
        matched_roles = match_roles_and_companies(skills, df)
        
        # Return the top matches as HTML
        return render_template('result.html', matched_roles=matched_roles.to_dict(orient="records"))

if __name__ == '__main__':
    app.run(debug=True)
