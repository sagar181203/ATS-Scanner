import streamlit as st
import os
from resume_parser import parse_resume
from job_matcher import JobMatcher
import tempfile

def save_uploaded_file(uploaded_file):
    """Save uploaded file temporarily and return the path"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

def main():
    st.title("ATS Resume Scanner")
    st.write("Upload a resume and enter job details to get matching scores and analysis.")

    # Initialize the job matcher
    job_matcher = JobMatcher()

    # File upload or text input
    upload_method = st.radio(
        "Choose input method",
        ["Upload Resume", "Paste resume text"]
    )

    resume_text = None
    temp_file_path = None

    if upload_method == "Upload Resume":
        uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
        if uploaded_file:
            temp_file_path = save_uploaded_file(uploaded_file)
            if temp_file_path:
                st.success(f"Successfully uploaded {uploaded_file.name}")
    else:
        resume_text = st.text_area(
            "Paste resume text here",
            height=300,
            placeholder="Copy and paste the content of your resume here..."
        )

    # Job description input
    job_description = st.text_area(
        "Job Description",
        height=200,
        placeholder="Enter the full job description here..."
    )

    # Required skills input
    required_skills = st.text_input(
        "Required Skills (comma-separated)",
        placeholder="Python, Machine Learning, SQL, etc."
    )

    if st.button("Analyze Resume"):
        if (temp_file_path or resume_text) and job_description and required_skills:
            try:
                with st.spinner("Analyzing resume..."):
                    # Parse resume
                    if temp_file_path:
                        resume_data = parse_resume(temp_file_path)
                    else:
                        resume_data = parse_resume("", resume_text=resume_text)

                    # Prepare job data
                    job_data = {
                        'description': job_description,
                        'required_skills': [skill.strip() for skill in required_skills.split(',')]
                    }

                    # Get ranking
                    ranking = job_matcher.rank_resume(resume_data, job_data)

                    # Display results
                    st.subheader("Analysis Results")
                    
                    # Contact Information
                    st.write("### Candidate Information")
                    for key, value in resume_data['contact_details'].items():
                        st.write(f"**{key.title()}:** {value if value else 'Not found'}")

                    # Experience Section
                    st.write("### Work Experience")
                    if resume_data.get('experience'):
                        for exp in resume_data['experience']:
                            with st.expander(f"{exp.get('role', 'Role Not Found')}"):
                                if exp.get('duration'):
                                    st.write(f"**Duration:** {exp['duration']}")
                                if exp.get('location'):
                                    st.write(f"**Location:** {exp['location']}")
                                if exp.get('description'):
                                    st.write("**Responsibilities:**")
                                    st.write(exp['description'])
                    else:
                        st.info("No work experience found in the resume")

                    # Skills
                    st.write("### Skills Found")
                    if resume_data['skills']:
                        st.write(", ".join(resume_data['skills']))
                    else:
                        st.warning("No relevant skills found in the resume")

                    # Matching Scores
                    st.write("### Matching Scores")
                    
                    # Create three columns for scores
                    score_col1, score_col2, score_col3 = st.columns(3)
                    
                    with score_col1:
                        st.metric("Overall Match", f"{ranking['overall_score']*100:.1f}%")
                    with score_col2:
                        st.metric("Skills Match", f"{ranking['skills_match']*100:.1f}%")
                    with score_col3:
                        st.metric("Content Similarity", f"{ranking['text_similarity']*100:.1f}%")

                    # Matched and Missing Skills
                    skill_col1, skill_col2 = st.columns(2)
                    
                    with skill_col1:
                        st.write("### Matched Skills")
                        if ranking['matched_skills']:
                            for skill in ranking['matched_skills']:
                                st.write(f"✅ {skill}")
                        else:
                            st.warning("No matching skills found")
                    
                    with skill_col2:
                        st.write("### Missing Skills")
                        if ranking['missing_skills']:
                            for skill in ranking['missing_skills']:
                                st.write(f"❌ {skill}")
                        else:
                            st.success("No missing required skills!")

                    # Cleanup temporary file
                    if temp_file_path:
                        os.unlink(temp_file_path)

            except Exception as e:
                st.error(f"Error processing resume: {e}")
        else:
            st.warning("Please provide resume content and job details.")

if __name__ == "__main__":
    main()
