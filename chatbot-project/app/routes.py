from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
import logging

from app.models import JobSearchRequest, JobSearchResponse, SkillsetRequest, SkillsetResponse
from app.agent import search_job_info, get_profession_skillset

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create an APIRouter instance named 'router'
router = APIRouter()


@router.post("/search", response_model=JobSearchResponse)
async def search_jobs(request: JobSearchRequest):
    """
    Search for job information and trends in a specific industry
    """
    try:
        logger.info(f"Received search request for industry: {request.industry}")
        response = await search_job_info(request)
        return response
    except Exception as e:
        logger.error(f"Error in search_jobs endpoint: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "results": [],
                "summary": f"Error processing request: {str(e)}. Please check if Ollama is running and your Serper API key is valid.",
                "industry": request.industry if request else "unknown",
                "query_used": ""
            }
        )


@router.post("/skillset", response_model=SkillsetResponse)
async def get_profession_skills(request: SkillsetRequest):
    """
    Get required skillset for a specific profession
    """
    try:
        logger.info(f"Received skillset request for profession: {request.profession}")
        response = await get_profession_skillset(request)
        return response
    except Exception as e:
        logger.error(f"Error in get_profession_skills endpoint: {str(e)}")
        # Return a fallback response instead of throwing an error
        return JSONResponse(
            status_code=500,
            content={
                "profession": request.profession if request else "unknown",
                "experience_level": request.experience_level if request else "mid-level",
                "technical_skills": [
                    {"name": "Error", "description": f"Could not process request: {str(e)}", "importance": "essential"}
                ],
                "soft_skills": [],
                "certifications": [],
                "tools": [],
                "summary": f"Error processing request: {str(e)}. Please check if Ollama is running properly."
            }
        )


@router.get("/", response_class=HTMLResponse)
async def root():
    """
    Root page with simple forms for API access
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Job Search Agent</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            .container {
                display: flex;
                gap: 20px;
                flex-wrap: wrap;
            }
            .form-container {
                flex: 1;
                min-width: 300px;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-bottom: 20px;
            }
            label, input, select, button {
                display: block;
                margin-bottom: 10px;
                width: 100%;
            }
            input, select {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            button {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            #result {
                margin-top: 20px;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                white-space: pre-wrap;
            }
            .spinner {
                border: 4px solid rgba(0, 0, 0, 0.1);
                width: 36px;
                height: 36px;
                border-radius: 50%;
                border-left-color: #4CAF50;
                animation: spin 1s linear infinite;
                margin: 20px auto;
                display: none;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .notification {
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
                display: none;
            }
            .error {
                background-color: #ffebee;
                border: 1px solid #ffcdd2;
                color: #b71c1c;
            }
            .success {
                background-color: #e8f5e9;
                border: 1px solid #c8e6c9;
                color: #1b5e20;
            }
        </style>
    </head>
    <body>
        <h1>Job Search Agent</h1>
        
        <div class="notification" id="notification"></div>
        
        <div class="container">
            <div class="form-container">
                <h2>Search Job Information</h2>
                <form id="jobSearchForm">
                    <label for="industry">Industry:</label>
                    <input type="text" id="industry" name="industry" required placeholder="e.g., software development, healthcare">
                    
                    <label for="keywords">Keywords (comma separated):</label>
                    <input type="text" id="keywords" name="keywords" placeholder="e.g., remote, AI, entry-level">
                    
                    <label for="location">Location:</label>
                    <input type="text" id="location" name="location" placeholder="e.g., United States, London">
                    
                    <label for="time_period">Time Period:</label>
                    <select id="time_period" name="time_period">
                        <option value="past week">Past Week</option>
                        <option value="past month">Past Month</option>
                        <option value="past year">Past Year</option>
                    </select>
                    
                    <button type="submit">Search</button>
                </form>
            </div>
            
            <div class="form-container">
                <h2>Get Professional Skillset</h2>
                <form id="skillsetForm">
                    <label for="profession">Profession:</label>
                    <input type="text" id="profession" name="profession" required placeholder="e.g., data scientist, graphic designer">
                    
                    <label for="experience_level">Experience Level:</label>
                    <select id="experience_level" name="experience_level">
                        <option value="entry-level">Entry Level</option>
                        <option value="mid-level" selected>Mid Level</option>
                        <option value="senior">Senior Level</option>
                    </select>
                    
                    <button type="submit">Get Skillset</button>
                </form>
            </div>
        </div>
        
        <div class="spinner" id="spinner"></div>
        
        <div id="result">
            <p>Results will appear here...</p>
        </div>
        
        <script>
            // Show notification
            function showNotification(message, isError = false) {
                const notification = document.getElementById('notification');
                notification.textContent = message;
                notification.classList.remove('error', 'success');
                notification.classList.add(isError ? 'error' : 'success');
                notification.style.display = 'block';
                
                setTimeout(() => {
                    notification.style.display = 'none';
                }, 5000);
            }
            
            // Show/hide loading spinner
            function toggleSpinner(show) {
                document.getElementById('spinner').style.display = show ? 'block' : 'none';
            }
            
            document.getElementById('jobSearchForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                toggleSpinner(true);
                
                const formData = new FormData(this);
                const industry = formData.get('industry');
                const keywordsRaw = formData.get('keywords');
                const keywords = keywordsRaw ? keywordsRaw.split(',').map(k => k.trim()).filter(k => k) : [];
                const location = formData.get('location');
                const timePeriod = formData.get('time_period');
                
                const payload = {
                    industry: industry,
                    keywords: keywords.length > 0 ? keywords : undefined,
                    location: location || undefined,
                    time_period: timePeriod
                };
                
                try {
                    const response = await fetch('/api/search', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(payload)
                    });
                    
                    const data = await response.json();
                    
                    // Check if there was an error
                    if (!response.ok) {
                        showNotification(data.summary || 'An error occurred with the search request', true);
                    }
                    
                    let resultHtml = '<h3>Job Search Results</h3>';
                    resultHtml += '<p><strong>Summary:</strong> ' + data.summary + '</p>';
                    
                    if (data.results && data.results.length > 0) {
                        resultHtml += '<h4>Top Results:</h4><ul>';
                        data.results.forEach(r => {
                            resultHtml += `<li><a href="${r.link}" target="_blank">${r.title}</a> - ${r.snippet}</li>`;
                        });
                        resultHtml += '</ul>';
                    } else {
                        resultHtml += '<p>No results found. Try different keywords or check API configuration.</p>';
                    }
                    
                    document.getElementById('result').innerHTML = resultHtml;
                } catch (error) {
                    showNotification('Error: ' + error.message, true);
                    document.getElementById('result').innerHTML = '<p>Error: ' + error.message + '</p>';
                } finally {
                    toggleSpinner(false);
                }
            });
            
            document.getElementById('skillsetForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                toggleSpinner(true);
                
                const formData = new FormData(this);
                const profession = formData.get('profession');
                const experienceLevel = formData.get('experience_level');
                
                const payload = {
                    profession: profession,
                    experience_level: experienceLevel
                };
                
                try {
                    const response = await fetch('/api/skillset', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(payload)
                    });
                    
                    const data = await response.json();
                    
                    // Check if there was an error
                    if (!response.ok) {
                        showNotification(data.summary || 'An error occurred with the skillset request', true);
                    }
                    
                    let resultHtml = `<h3>Skillset for ${data.experience_level} ${data.profession}</h3>`;
                    resultHtml += `<p><strong>Summary:</strong> ${data.summary}</p>`;
                    
                    // Technical Skills
                    resultHtml += '<h4>Technical Skills:</h4><ul>';
                    data.technical_skills.forEach(skill => {
                        resultHtml += `<li><strong>${skill.name}</strong> (${skill.importance}) - ${skill.description}</li>`;
                    });
                    resultHtml += '</ul>';
                    
                    // Soft Skills
                    resultHtml += '<h4>Soft Skills:</h4><ul>';
                    data.soft_skills.forEach(skill => {
                        resultHtml += `<li><strong>${skill.name}</strong> (${skill.importance}) - ${skill.description}</li>`;
                    });
                    resultHtml += '</ul>';
                    
                    // Certifications
                    if (data.certifications && data.certifications.length > 0) {
                        resultHtml += '<h4>Recommended Certifications:</h4><ul>';
                        data.certifications.forEach(cert => {
                            resultHtml += `<li>${cert}</li>`;
                        });
                        resultHtml += '</ul>';
                    }
                    
                    // Tools
                    if (data.tools && data.tools.length > 0) {
                        resultHtml += '<h4>Recommended Tools:</h4><ul>';
                        data.tools.forEach(tool => {
                            resultHtml += `<li>${tool}</li>`;
                        });
                        resultHtml += '</ul>';
                    }
                    
                    document.getElementById('result').innerHTML = resultHtml;
                } catch (error) {
                    showNotification('Error: ' + error.message, true);
                    document.getElementById('result').innerHTML = '<p>Error: ' + error.message + '</p>';
                } finally {
                    toggleSpinner(false);
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content