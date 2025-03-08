# FastAPI Resume Analyzer

A FastAPI application that analyzes resumes using Ollama AI. This application allows users to upload a PDF resume, extracts text from it, and provides AI-powered analysis and feedback.

## Features

- PDF text extraction
- Resume analysis using Ollama AI (Mistral model)
- Clean and responsive web interface
- Real-time feedback with:
  - Resume strengths
  - Areas for improvement
  - ATS-friendly suggestions
  - Overall score

## Prerequisites

- Python 3.8+
- Ollama installed and running locally or accessible on your network

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fastapi-resume-analyzer.git
cd fastapi-resume-analyzer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Make sure Ollama is installed and running with the Mistral model:
```bash
ollama pull mistral
```

## Running the Application

1. Start the FastAPI server:
```bash
python main.py
```

2. Open your browser and go to:
```
http://localhost:8000
```

## API Endpoints

- `GET /`: Returns the HTML frontend
- `POST /analyze-resume`: Accepts a PDF file upload and returns the analysis results

## Project Structure

```
fastapi-resume-analyzer/
├── main.py              # FastAPI application
├── requirements.txt     # Project dependencies
├── static/              # Static files
│   └── index.html       # Frontend HTML
└── README.md            # This file
```

## Customization

- Modify the AI prompt in the `analyze_resume` function to adjust the analysis criteria
- Update the frontend design in `static/index.html`
- Add more features to the API in `main.py`

## License

MIT