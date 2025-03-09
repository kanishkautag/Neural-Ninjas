import os
from typing import List, Dict, Any, Optional
import requests
import json
from config import settings

class JobSearchAgent:
    """Job search agent that uses Ollama and Serper API for job searching and skillset recommendations"""
    
    def __init__(self):
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.serper_api_key = settings.SERPER_API_KEY
        self.model = settings.OLLAMA_MODEL
    
    def _query_ollama(self, prompt: str) -> str:
        """Send a query to Ollama and get response"""
        try:
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={"model": self.model, "prompt": prompt}
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            print(f"Error querying Ollama: {e}")
            return ""
    
    def _search_serper(self, query: str) -> List[Dict[Any, Any]]:
        """Search using Serper API"""
        try:
            headers = {
                'X-API-KEY': self.serper_api_key,
                'Content-Type': 'application/json'
            }
            payload = {
                "q": query,
                "gl": "us",
                "hl": "en",
                "num": 10
            }
            response = requests.post(
                'https://google.serper.dev/search',
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json().get("organic", [])
        except Exception as e:
            print(f"Error searching Serper: {e}")
            return []
    
    def search_jobs(self, industry: str, keywords: str, location: str, time_period: str) -> Dict[str, Any]:
        """Search for jobs based on criteria"""
        search_query = f"job openings {industry} {keywords} {location} {time_period}"
        
        # Use Serper API to get job listings
        search_results = self._search_serper(search_query)
        
        # Extract job information
        jobs = []
        for result in search_results:
            if result.get("title") and "job" in result.get("title", "").lower():
                jobs.append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "source": result.get("source", "")
                })
        
        # Use Ollama to generate a market summary
        market_summary_prompt = f"""
        Based on the following job search:
        Industry: {industry}
        Keywords: {keywords}
        Location: {location}
        Time Period: {time_period}
        
        Provide a brief summary of the current job market situation. Focus on demand, salary ranges, 
        and required skills.
        """
        
        market_summary = self._query_ollama(market_summary_prompt)
        
        return {
            "jobs": jobs,
            "market_summary": market_summary,
            "query": {
                "industry": industry,
                "keywords": keywords,
                "location": location,
                "time_period": time_period
            }
        }
    
    def get_professional_skillset(self, profession: str, experience_level: str) -> Dict[str, Any]:
        """Get skillset recommendations for a profession at a specific experience level"""
        prompt = f"""
        Create a comprehensive professional skillset guide for a {profession} at {experience_level} level.
        Include sections for:
        1. Technical skills
        2. Soft skills
        3. Tools and technologies
        4. Certifications
        5. Learning resources
        
        Format your response as a JSON object with these section names as keys and arrays of skills as values.
        Example format:
        {{
        "Technical skills": ["skill1", "skill2"],
        "Soft skills": ["skill1", "skill2"],
        "Tools and technologies": ["tool1", "tool2"],
        "Certifications": ["cert1", "cert2"],
        "Learning resources": ["resource1", "resource2"]
        }}
        """
        
        response = self._query_ollama(prompt)
        
        try:
            # Try to parse the response as JSON
            import json
            json_data = json.loads(response)
            
            # Add missing sections if any
            sections = ["Technical skills", "Soft skills", "Tools and technologies", 
                    "Certifications", "Learning resources"]
                    
            for section in sections:
                if section not in json_data:
                    json_data[section] = ["No data available"]
            
            return {
                "profession": profession,
                "experience_level": experience_level,
                "skillset": json_data
            }
        except json.JSONDecodeError:
            # If not valid JSON, fall back to a basic structure
            print("Could not parse Ollama response as JSON")
            print(f"Raw response: {response[:500]}...")  # Print beginning of response
            
            return {
                "profession": profession,
                "experience_level": experience_level,
                "skillset": {
                    "Technical skills": ["Could not retrieve data"],
                    "Soft skills": ["Could not retrieve data"],
                    "Tools and technologies": ["Could not retrieve data"],
                    "Certifications": ["Could not retrieve data"],
                    "Learning resources": ["Could not retrieve data"]
                }
            }