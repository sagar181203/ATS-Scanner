# Applicant Tracking System (ATS)

An intelligent Applicant Tracking System that helps analyze and process resumes using AI/ML techniques.

## Overview

This project implements an Applicant Tracking System (ATS) that helps streamline the recruitment process by automatically analyzing resumes and matching them with job requirements. The system uses machine learning algorithms to extract relevant information from resumes and provide meaningful insights.

## Features

- Resume parsing and information extraction
- Skills matching and analysis
- Automated resume scoring
- Candidate ranking system
- User-friendly interface

## Setup

### Prerequisites

- Python 3.8 or higher
- Required Python packages (install using `pip install -r requirements.txt`)
- NLTK data (will be downloaded during setup)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/sagar181203/ATS-Scanner.git
```

2. Navigate to the project directory:
```bash
cd ATS
```

3. Run the setup script to install dependencies and download NLTK data:
```bash
python setup.py install
python setup_nltk.py
```

4. Install additional requirements:
```bash
pip install -r requirements.txt
```

### Initial Setup

Before running the application for the first time, ensure NLTK data is properly downloaded:
```bash
python setup_nltk.py
```
This will download necessary NLTK packages like punkt, averaged_perceptron_tagger, and other required datasets.

## Usage

Run the main application:
```bash
python main.py
```

## Project Structure

```
ATS/
├── main.py               # Main application entry point
├── job_matcher.py        # Job matching and scoring algorithms
├── resume_parser.py      # Resume parsing and information extraction
├── setup.py             # Project installation script
├── setup_nltk.py        # NLTK data download script
├── job_descriptions/    # Directory containing job description files
├── sample_resumes/      # Directory containing sample resume files
├── requirements.txt     # Project dependencies
└── README.md           # Project documentation
```

## Contributing

Feel free to submit issues and enhancement requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For queries or suggestions, please contact me at sagar181203@gmail.com
