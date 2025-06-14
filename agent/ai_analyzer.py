# agent/ai_analyzer.py - Uses AI to analyze and categorize content
import openai
from typing import Dict, List
import os
import json
from dotenv import load_dotenv

load_dotenv()

class AIAnalyzer:
    """Uses AI to analyze file content and make decisions"""
    
    def __init__(self):
        # Initialize OpenAI client
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.model = "gpt-3.5-turbo"  # Cost-effective model for learning
    
    def analyze_content(self, file_data: Dict) -> Dict:
        """
        Analyze file content using AI
        
        Returns:
            dict: Contains category, summary, tags, priority
        """
        content = file_data.get('content', '')
        file_name = file_data.get('file_name', '')
        file_type = file_data.get('file_type', '')
        
        # Create a prompt for the AI
        prompt = f"""
        Analyze this file and provide insights:
        
        File: {file_name} ({file_type})
        Content: {content[:1000]}...
        
        Please respond with a JSON object containing:
        1. "category": One of [document, data, report, personal, work, other]
        2. "summary": Brief 2-sentence summary
        3. "tags": List of 3-5 relevant keywords
        4. "priority": One of [high, medium, low]
        5. "action_needed": Brief suggestion for what to do with this file
        
        Focus on being practical and helpful.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful file organization assistant. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            # Parse the AI response
            ai_response = response.choices[0].message.content
            analysis = self._parse_ai_response(ai_response)
            
            print(f"✓ AI analyzed {file_name}: {analysis.get('category', 'unknown')} category")
            return analysis
            
        except Exception as e:
            print(f"✗ AI analysis failed for {file_name}: {str(e)}")
            # Return a default analysis if AI fails
            return {
                'category': 'other',
                'summary': f'File processing completed for {file_name}',
                'tags': [file_type.replace('.', ''), 'unanalyzed'],
                'priority': 'medium',
                'action_needed': 'Manual review recommended'
            }
    
    def _parse_ai_response(self, response: str) -> Dict:
        """Parse AI response and handle potential JSON errors"""
        try:
            # Try to parse as JSON
            return json.loads(response)
        except:
            # If JSON parsing fails, create a basic structure
            return {
                'category': 'other',
                'summary': response[:100] + '...' if len(response) > 100 else response,
                'tags': ['parsed_response'],
                'priority': 'medium',
                'action_needed': 'Review AI response parsing'
            }