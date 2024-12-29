import docx
import PyPDF2
import re
import nltk
from typing import Dict, List, Optional
import io

# Download required NLTK data
try:
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')
except Exception as e:
    print(f"Error downloading NLTK data: {e}")

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file."""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(file_path: str) -> Dict[str, any]:
    """Extract text from DOCX file with formatting information."""
    try:
        doc = docx.Document(file_path)
        text_with_font_sizes = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                # Get the maximum font size in the paragraph
                max_font_size = 0
                for run in paragraph.runs:
                    if hasattr(run._element.rPr, 'sz'):
                        font_size = int(run._element.rPr.sz.val) / 2  # Convert to points
                        max_font_size = max(max_font_size, font_size)
                    
                text_with_font_sizes.append({
                    'text': paragraph.text.strip(),
                    'font_size': max_font_size
                })
        
        # Combine all text
        full_text = '\n'.join(item['text'] for item in text_with_font_sizes)
        
        return {
            'text': full_text,
            'paragraphs': text_with_font_sizes
        }
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return {'text': '', 'paragraphs': []}

def extract_contact_details(text: str, text_with_formatting: Optional[Dict] = None) -> Dict[str, Optional[str]]:
    """Extract name, email, and phone from resume text."""
    # Extract email
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email = re.findall(email_pattern, text)
    email = email[0] if email else None
    
    # Extract phone number (handles multiple formats)
    phone_pattern = r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phone = re.findall(phone_pattern, text)
    phone = phone[0] if phone else None

    # Extract name
    name = None
    
    # Get the first few lines of the text
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    if lines:
        # First try: Look for a line with all caps that contains 2-3 words
        for line in lines[:3]:  # Check first 3 lines
            # Remove any special characters and extra spaces
            cleaned_line = ' '.join(re.findall(r'[A-Z][A-Z\s]+(?:\s[A-Z]+)*', line))
            if cleaned_line and len(cleaned_line.split()) in [2, 3]:
                name = cleaned_line
                break
        
        # Second try: Look for capitalized words if no all-caps name found
        if not name:
            for line in lines[:3]:
                # Match "Firstname [Middle] Lastname" pattern
                name_match = re.search(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}$', line)
                if name_match:
                    name = name_match.group(0)
                    break
    
    # If name found in all caps, convert to title case
    if name and name.isupper():
        name = name.title()

    return {
        'name': name,
        'email': email,
        'phone': phone
    }

def extract_skills(text: str) -> List[str]:
    """Extract skills from the resume using a predefined skill list."""
    # Common technical skills
    SKILLS_LIST = [
        # Programming Languages
        'Python', 'Java', 'C++', 'JavaScript', 'Ruby', 'PHP', 'Swift', 'Kotlin',
        # Web Technologies
        'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask',
        # Data Science & ML
        'Machine Learning', 'Deep Learning', 'NLP', 'Data Science', 'TensorFlow', 'PyTorch',
        # Databases
        'SQL', 'MongoDB', 'PostgreSQL', 'MySQL', 'Oracle',
        # Cloud & DevOps
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins',
        # Version Control
        'Git', 'SVN',
        # Other Technical Skills
        'REST API', 'GraphQL', 'Linux', 'Agile', 'Scrum'
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    for skill in SKILLS_LIST:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return found_skills

def extract_experience(text: str) -> List[Dict[str, str]]:
    """Extract work experience from resume text."""
    experiences = []
    lines = text.split('\n')
    experience_started = False
    current_experience = {}
    
    # Keywords that typically indicate the start of experience section
    experience_headers = ['EXPERIENCE', 'WORK EXPERIENCE', 'EMPLOYMENT HISTORY', 'PROFESSIONAL EXPERIENCE']
    
    # Keywords that might indicate the start of a new section
    section_headers = ['EDUCATION', 'SKILLS', 'PROJECTS', 'CERTIFICATIONS', 'ACHIEVEMENTS']
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Check if we've reached the experience section
        if any(header in line.upper() for header in experience_headers):
            experience_started = True
            continue
            
        # Check if we've moved past the experience section
        if experience_started and any(header in line.upper() for header in section_headers):
            experience_started = False
            if current_experience:
                experiences.append(current_experience)
                current_experience = {}
            continue
            
        if experience_started:
            # Try to match date patterns
            date_pattern = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}\s*(?:-|–|to)\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}\s*(?:-|–|to)\s*Present'
            date_match = re.search(date_pattern, line, re.IGNORECASE)
            
            # Try to match role patterns
            role_patterns = [
                r'(?:^|\s)(Software Engineer|Developer|Engineer|Intern|Manager|Director|Lead|Consultant)(?:\s|$)',
                r'(?:^|\s)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Engineer|Developer|Intern|Manager|Director|Lead|Consultant))(?:\s|$)'
            ]
            
            role_match = None
            for pattern in role_patterns:
                match = re.search(pattern, line)
                if match:
                    role_match = match
                    break
            
            # If we find a date, it's likely the start of a new experience entry
            if date_match:
                if current_experience:
                    experiences.append(current_experience)
                current_experience = {'duration': date_match.group(0)}
                
                # Check if the same line contains the role
                remaining_text = line.replace(date_match.group(0), '').strip()
                if remaining_text:
                    current_experience['role'] = remaining_text
                
            # If we find a role without a date and no role is set yet
            elif role_match and 'role' not in current_experience:
                current_experience['role'] = role_match.group(0).strip()
                
            # If we find a location (typically in parentheses)
            elif '(' in line and ')' in line and 'location' not in current_experience:
                location = re.search(r'\((.*?)\)', line)
                if location:
                    current_experience['location'] = location.group(1)
                    
            # If it's not a date/role/location line and we have a current experience,
            # it's probably a description
            elif current_experience:
                if 'description' not in current_experience:
                    current_experience['description'] = []
                if line.strip().startswith('•'):
                    current_experience['description'].append(line.strip())
                elif line.strip():
                    current_experience['description'].append(line.strip())
    
    # Add the last experience if exists
    if current_experience:
        experiences.append(current_experience)
    
    # Clean up descriptions
    for exp in experiences:
        if 'description' in exp:
            exp['description'] = '\n'.join(exp['description'])
    
    return experiences

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts using simple word overlap."""
    # Tokenize and clean the texts
    words1 = set(word.lower() for word in nltk.word_tokenize(text1) if word.isalnum())
    words2 = set(word.lower() for word in nltk.word_tokenize(text2) if word.isalnum())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)

def parse_resume(file_path: str, resume_text: str = None) -> Dict:
    """Main function to parse resume and extract all information."""
    text = ""
    text_with_formatting = None
    
    if resume_text:
        # If text is directly provided
        text = resume_text
    elif file_path.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.docx'):
        extracted_data = extract_text_from_docx(file_path)
        text = extracted_data['text']
        text_with_formatting = extracted_data
    else:
        raise ValueError("Unsupported file format. Please provide a PDF or DOCX file.")

    if not text:
        raise ValueError("Could not extract text from the resume.")

    # Extract all information
    contact_details = extract_contact_details(text, text_with_formatting)
    skills = extract_skills(text)
    experience = extract_experience(text)

    return {
        'contact_details': contact_details,
        'skills': skills,
        'experience': experience,
        'raw_text': text
    }
