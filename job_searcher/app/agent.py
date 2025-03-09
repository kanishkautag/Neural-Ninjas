import os
from typing import List, Dict, Any, Optional
import requests
import json
from app.config import settings

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
        Include:
        1. Technical skills
        2. Soft skills
        3. Tools and technologies
        4. Certifications
        5. Learning resources
        
        Format each as a bulleted list with brief explanations.
        """
        
        response = self._query_ollama(prompt)
        
        # Parse the response to get structured data
        sections = ["Technical skills", "Soft skills", "Tools and technologies", 
                    "Certifications", "Learning resources"]
        
        skillset = {}
        current_section = None
        
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check if line is a section header
            for section in sections:
                if section.lower() in line.lower():
                    current_section = section
                    skillset[current_section] = []
                    break
                    
            # Add content to current section
            if current_section and line and not any(section.lower() in line.lower() for section in sections):
                # Remove bullet points if present
                clean_line = line
                for bullet in ['•', '-', '*', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.']:
                    if line.startswith(bullet):
                        clean_line = line[len(bullet):].strip()
                skillset[current_section].append(clean_line)
        
        return {
            "profession": profession,
            "experience_level": experience_level,
            "skillset": skillset
        }