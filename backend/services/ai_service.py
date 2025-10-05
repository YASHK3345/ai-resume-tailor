import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage
from models.ai import AIContentRequest, AIContentResponse, ATSAnalysisRequest, ATSAnalysisResponse
import json
import re

load_dotenv()

class AIService:
    """AI content generation and optimization service"""
    
    def __init__(self):
        self.api_key = os.getenv("EMERGENT_LLM_KEY")
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
    
    async def optimize_content(self, request: AIContentRequest) -> AIContentResponse:
        """Optimize CV content for ATS and engagement"""
        
        # Create AI chat instance
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"content_optimization_{request.section_type}",
            system_message="You are an expert CV writer and ATS optimization specialist. You help professionals create compelling, ATS-friendly CV content that stands out to both algorithms and human recruiters."
        ).with_model("openai", "gpt-4o-mini")
        
        # Create optimization prompt
        prompt = self._create_content_optimization_prompt(request)
        user_message = UserMessage(text=prompt)
        
        try:
            # Get AI response
            response = await chat.send_message(user_message)
            
            # Parse the response
            return self._parse_content_response(response, request)
            
        except Exception as e:
            raise Exception(f"AI content optimization failed: {str(e)}")
    
    async def analyze_ats_score(self, request: ATSAnalysisRequest) -> ATSAnalysisResponse:
        """Analyze CV content for ATS compatibility"""
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"ats_analysis",
            system_message="You are an ATS (Applicant Tracking System) expert. You analyze CVs and provide detailed ATS compatibility scores and improvement suggestions."
        ).with_model("openai", "gpt-4o-mini")
        
        prompt = self._create_ats_analysis_prompt(request)
        user_message = UserMessage(text=prompt)
        
        try:
            response = await chat.send_message(user_message)
            return self._parse_ats_response(response, request)
            
        except Exception as e:
            raise Exception(f"ATS analysis failed: {str(e)}")
    
    def _create_content_optimization_prompt(self, request: AIContentRequest) -> str:
        """Create prompt for content optimization"""
        return f"""
Optimize the following CV {request.section_type} section for maximum ATS compatibility and human appeal:

Job Title: {request.job_title}
Company: {request.company or 'Not specified'}
Tone: {request.tone}
Target Keywords: {', '.join(request.target_keywords)}

Existing Content:
{request.existing_content}

Please provide:
1. Optimized content that is ATS-friendly and engaging
2. 3-5 specific improvement suggestions
3. List of keywords incorporated
4. ATS compatibility score (0-100)

Return your response in this JSON format:
{{
  "optimized_content": "Your optimized content here",
  "suggestions": ["suggestion1", "suggestion2", "suggestion3"],
  "keywords_used": ["keyword1", "keyword2"],
  "ats_score": 85
}}
"""
    
    def _create_ats_analysis_prompt(self, request: ATSAnalysisRequest) -> str:
        """Create prompt for ATS analysis"""
        job_desc_text = f"\nJob Description:\n{request.job_description}" if request.job_description else ""
        
        return f"""
Analyze this CV content for ATS compatibility and provide a detailed assessment:

CV Content:
{request.cv_content}{job_desc_text}

Provide a comprehensive ATS analysis including:
1. Overall ATS compatibility score (0-100)
2. Section-by-section scores
3. Specific improvement suggestions
4. Missing keywords that should be included
5. Keyword density analysis

Return your response in this JSON format:
{{
  "overall_score": 75,
  "section_scores": {{
    "contact_info": 90,
    "summary": 80,
    "experience": 70,
    "skills": 85,
    "education": 75
  }},
  "suggestions": ["Add more action verbs", "Include industry keywords"],
  "missing_keywords": ["project management", "data analysis"],
  "keyword_density": {{
    "management": 2.5,
    "leadership": 1.8
  }}
}}
"""
    
    def _parse_content_response(self, response: str, request: AIContentRequest) -> AIContentResponse:
        """Parse AI content optimization response"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return AIContentResponse(**data)
            else:
                # Fallback if JSON parsing fails
                return AIContentResponse(
                    optimized_content=response,
                    suggestions=["AI response parsing failed - manual review recommended"],
                    keywords_used=request.target_keywords,
                    ats_score=70
                )
        except Exception:
            return AIContentResponse(
                optimized_content=response,
                suggestions=["AI response parsing failed - manual review recommended"],
                keywords_used=request.target_keywords,
                ats_score=70
            )
    
    def _parse_ats_response(self, response: str, request: ATSAnalysisRequest) -> ATSAnalysisResponse:
        """Parse ATS analysis response"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return ATSAnalysisResponse(**data)
            else:
                return ATSAnalysisResponse(
                    overall_score=70,
                    section_scores={"general": 70},
                    suggestions=["AI analysis parsing failed - manual review recommended"],
                    missing_keywords=[],
                    keyword_density={}
                )
        except Exception:
            return ATSAnalysisResponse(
                overall_score=70,
                section_scores={"general": 70},
                suggestions=["AI analysis parsing failed - manual review recommended"],
                missing_keywords=[],
                keyword_density={}
            )