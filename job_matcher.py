from typing import Dict, List, Tuple
from resume_parser import calculate_similarity

class JobMatcher:
    def __init__(self):
        """Initialize the JobMatcher."""
        pass

    def calculate_skills_match(self, resume_skills: List[str], required_skills: List[str]) -> Tuple[float, List[str], List[str]]:
        """Calculate the percentage of required skills present in resume."""
        if not required_skills:
            return 0.0, [], []

        resume_skills_lower = [skill.lower() for skill in resume_skills]
        required_skills_lower = [skill.lower() for skill in required_skills]

        matched_skills = [skill for skill in required_skills if skill.lower() in resume_skills_lower]
        missing_skills = [skill for skill in required_skills if skill.lower() not in resume_skills_lower]

        match_percentage = len(matched_skills) / len(required_skills)
        return match_percentage, matched_skills, missing_skills

    def rank_resume(self, resume_data: Dict, job_description: Dict) -> Dict:
        """Rank a resume against a job description and return detailed results."""
        # Calculate text similarity
        text_similarity = calculate_similarity(
            resume_data['raw_text'],
            job_description['description']
        )

        # Calculate skills match
        skills_match, matched_skills, missing_skills = self.calculate_skills_match(
            resume_data['skills'],
            job_description.get('required_skills', [])
        )

        # Calculate overall score (weighted average)
        overall_score = (text_similarity * 0.6) + (skills_match * 0.4)

        return {
            'overall_score': overall_score,
            'text_similarity': text_similarity,
            'skills_match': skills_match,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills
        }

    def rank_resumes(self, resumes: List[Dict], job_description: Dict) -> List[Dict]:
        """Rank multiple resumes against a job description."""
        ranked_resumes = []
        
        for resume in resumes:
            ranking = self.rank_resume(resume, job_description)
            ranked_resumes.append({
                'resume': resume,
                'ranking': ranking
            })

        # Sort by overall score in descending order
        ranked_resumes.sort(key=lambda x: x['ranking']['overall_score'], reverse=True)
        return ranked_resumes
