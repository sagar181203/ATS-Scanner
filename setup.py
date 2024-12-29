import os

# Create directories
directories = ['sample_resumes', 'job_descriptions']
for directory in directories:
    os.makedirs(directory, exist_ok=True)
