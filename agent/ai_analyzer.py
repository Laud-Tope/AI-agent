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
        Content: {content[:800]}...
        
        Please respond with a JSON object containing:
        1. "category": One of [document, data, report, personal, work, images, other]
        2. "summary": Brief 2-sentence summary
        3. "tags": List of 3-5 relevant keywords
        4. "priority": One of [high, medium, low]
        5. "action_needed": Brief suggestion for what to do with this file
        
        For images, focus on the type and potential use.
        Focus on being practical and helpful.
        """
        
        try:
            # Check if we have content to analyze
            if not content.strip():
                print(f"⚠️  No content extracted from {file_name}")
                return self._create_default_analysis(file_name, file_type, "No content extracted")
            
            print(f"🔍 Sending {len(content)} characters to AI for analysis...")
            
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
            print(f"🤖 AI Response: {ai_response[:100]}...")
            
            analysis = self._parse_ai_response(ai_response)
            
            print(f"✓ AI analyzed {file_name}: {analysis.get('category', 'unknown')} category")
            return analysis
            
        except Exception as e:
            print(f"✗ AI analysis failed for {file_name}: {str(e)}")
            return self._create_default_analysis(file_name, file_type, str(e))
    
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
    
    def _create_default_analysis(self, file_name: str, file_type: str, error_msg: str) -> Dict:
        """Create a smart default analysis based on file type"""
        # Smart defaults based on file extension
        if file_type in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            category = 'images'
            summary = f'Image file: {file_name}. May contain photos, graphics, or visual content.'
            tags = ['image', 'visual', file_type.replace('.', '')]
            action = 'Review and organize in image collection'
        elif file_type == '.pdf':
            category = 'document'
            summary = f'PDF document: {file_name}. Likely contains text, reports, or formatted content.'
            tags = ['pdf', 'document', 'text']
            action = 'Review document content and file appropriately'
        elif file_type in ['.csv', '.xlsx']:
            category = 'data'
            summary = f'Data file: {file_name}. Contains structured data in tabular format.'
            tags = ['data', 'spreadsheet', file_type.replace('.', '')]
            action = 'Analyze data structure and content'
        else:
            category = 'other'
            summary = f'File: {file_name}. Requires manual review to determine content and purpose.'
            tags = [file_type.replace('.', ''), 'needs_review']
            action = 'Manual review recommended'
        
        return {
            'category': category,
            'summary': summary,
            'tags': tags,
            'priority': 'medium',
            'action_needed': action,
            'note': f'Default analysis used due to: {error_msg}'
        }