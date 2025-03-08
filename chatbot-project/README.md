# Industry Job Search Agent

An AI-powered agent that searches for the latest job findings and industry news using Ollama for LLM processing and Serper API for web search capabilities.

## Setup

1. Clone this repository

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file based on `.env.example`
   - Add your Serper API key
   - Configure Ollama URL (default is http://localhost:11434)

4. Start Ollama locally (if you haven't already):
   - Install Ollama from https://ollama.ai/
   - Pull the LLM model: `ollama pull llama3` (or your preferred model)
   - Ensure Ollama is running

5. Run the application:
   ```
   python main.py
   ```

## API Usage

### Search for Job Information

**Endpoint:** `POST /api/search`

**Request Body:**
```json
{
  "industry": "software development",
  "keywords": ["remote", "AI", "machine learning"],
  "location": "United States",
  "time_period": "past month"
}
```

**Response:**
```json
{
  "results": [
    {
      "title": "Example Job Trend Article",
      "link": "https://example.com/article",
      "snippet": "Summary of the article...",
      "date": "Mar 1, 2025",
      "source": "Example News"
    }
  ],
  "summary": "An AI-generated summary of the job market trends...",
  "industry": "software development",
  "query_used": "software development jobs remote AI machine learning United States past month"
}
```

### Get Professional Skillset

**Endpoint:** `POST /api/skillset`

**Request Body:**
```json
{
  "profession": "data scientist",
  "experience_level": "mid-level"
}
```

**Response:**
```json
{
  "profession": "data scientist",
  "experience_level": "mid-level",
  "technical_skills": [
    {
      "name": "Python",
      "description": "Advanced programming in Python with data science libraries",
      "importance": "essential"
    },
    {
      "name": "Machine Learning",
      "description": "Understanding of ML algorithms and implementation",
      "importance": "essential"
    }
  ],
  "soft_skills": [
    {
      "name": "Communication",
      "description": "Ability to explain complex concepts to non-technical stakeholders",
      "importance": "essential"
    }
  ],
  "certifications": [
    "Azure Data Scientist Associate",
    "Google Professional Data Engineer"
  ],
  "tools": [
    "Jupyter Notebooks",
    "TensorFlow",
    "PyTorch",
    "Pandas",
    "SQL"
  ],
  "summary": "Mid-level data scientists need strong Python programming skills with ML implementation experience..."
}
```

### Health Check

**Endpoint:** `GET /api/health`

## Requirements

- Python 3.8+
- FastAPI
- Ollama (running locally)
- Serper API Key