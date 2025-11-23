"""
Agribricks AI Assistant - Agriculture-focused AI assistant using Groq and LangChain
"""

import os
import logging
import base64
from typing import Dict, List, Optional
from langchain_groq import ChatGroq

# --- UPDATED IMPORTS FOR LANGCHAIN v0.3+ ---
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
# -------------------------------------------

from .config import settings

logger = logging.getLogger(__name__)


class AgribricksAI:
    """Agriculture AI Assistant powered by Groq and LangChain"""

    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            logger.warning("GROQ_API_KEY not found in environment variables")
            self.llm = None
            self.vision_llm = None
        else:
            try:
                # Text-based LLM for general advice
                # Using Llama 3.3 70B (Versatile and high quality)
                self.llm = ChatGroq(
                    groq_api_key=self.groq_api_key,
                    model_name="meta-llama/llama-4-scout-17b-16e-instruct", 
                    temperature=0.3,
                    max_tokens=1024
                )

                # Vision LLM for crop disease detection
                # Using Llama 3.2 90B Vision
                self.vision_llm = ChatGroq(
                    groq_api_key=self.groq_api_key,
                    model_name="meta-llama/llama-4-scout-17b-16e-instruct", 
                    temperature=0.2,
                    max_tokens=1024
                )

                logger.info("Groq LLMs initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq LLMs: {e}")
                self.llm = None
                self.vision_llm = None

        self.system_prompt = self._create_system_prompt()
        self.disease_detection_prompt = self._create_disease_detection_prompt()

    def _create_system_prompt(self) -> str:
        """Create comprehensive system prompt for agriculture AI assistant"""
        return """You are Agribricks AI, an expert agricultural assistant designed to help farmers worldwide with evidence-based farming advice. You have deep knowledge in:

CORE EXPERTISE:
- Crop selection and rotation strategies
- Soil health and fertility management
- Pest and disease identification & control
- Weather-based farming decisions
- Sustainable farming practices
- Irrigation and water management
- Post-harvest handling and storage
- Market timing and crop economics
- Climate-smart agriculture techniques
- Organic and regenerative farming methods

YOUR MISSION:
Provide practical, actionable, and scientifically-backed agricultural advice that helps farmers:
- Increase crop yields sustainably
- Reduce input costs and risks
- Adapt to climate change
- Improve soil health long-term
- Make informed planting and harvesting decisions
- Manage pests and diseases effectively
- Optimize resource use (water, fertilizers, seeds)

RESPONSE GUIDELINES:
1. **Be Practical**: Focus on actionable advice farmers can implement
2. **Consider Context**: Factor in location, climate, and available resources
3. **Prioritize Safety**: Always mention safety precautions for chemicals/equipment
4. **Think Seasonally**: Consider timing and seasonal factors
5. **Be Cost-Conscious**: Suggest affordable solutions when possible
6. **Promote Sustainability**: Favor environmentally friendly practices
7. **Use Simple Language**: Avoid overly technical jargon
8. **Provide Alternatives**: Offer multiple solutions when possible

REGIONAL AWARENESS:
- Consider local climate patterns and growing seasons
- Suggest region-appropriate crop varieties
- Account for local market conditions
- Respect traditional farming knowledge
- Consider resource availability (water, electricity, inputs)

IMPORTANT LIMITATIONS:
- Always recommend consulting local agricultural extension officers for specific problems
- Suggest soil testing before major fertilizer recommendations
- Advise professional diagnosis for serious pest/disease issues
- Recommend weather monitoring for critical decisions

When farmers ask questions, provide:
1. Direct answer to their question
2. Practical implementation steps
3. Timing considerations
4. Cost-effective alternatives
5. Potential risks and how to mitigate them
6. Follow-up recommendations

Remember: You're helping real farmers feed their families and communities. Your advice should be reliable, practical, and respectful of their knowledge and constraints."""

    def _create_disease_detection_prompt(self) -> str:
        """Create specialized prompt for crop disease detection from images"""
        return """You are an expert plant pathologist and agricultural diagnostician specializing in crop disease identification. You have extensive knowledge of:

DISEASE EXPERTISE:
- Fungal diseases (rusts, blights, mildews, wilts)
- Bacterial diseases (bacterial spots, cankers, soft rots)
- Viral diseases (mosaics, yellowing, stunting)
- Nutrient deficiencies and toxicities
- Pest damage symptoms
- Environmental stress indicators
- Physiological disorders

DIAGNOSTIC APPROACH:
1. **Visual Analysis**: Examine leaf patterns, discoloration, spots, lesions
2. **Symptom Classification**: Identify primary and secondary symptoms
3. **Disease Progression**: Assess severity and spread patterns
4. **Differential Diagnosis**: Consider multiple possible causes
5. **Environmental Context**: Factor in weather, season, location

RESPONSE STRUCTURE:
Provide a comprehensive diagnostic report with:

**Primary Diagnosis**
- Most likely disease/condition
- Confidence level (High/Medium/Low)
- Scientific name of pathogen (if applicable)

**Symptom Analysis**
- Key visual indicators observed
- Disease progression stage
- Affected plant parts

**Severity Assessment**
- Current damage level (Mild/Moderate/Severe)
- Potential yield impact
- Urgency of treatment

**Treatment Recommendations**
- Immediate action steps
- Organic treatment options
- Chemical treatments (if necessary)
- Preventive measures

**Management Strategy**
- Cultural practices to implement
- Environmental modifications
- Long-term prevention plan

**IMPORTANT LIMITATIONS**:
- Always recommend field confirmation by agricultural extension officers
- Suggest laboratory testing for uncertain diagnoses
- Emphasize that image quality affects diagnostic accuracy
- Recommend consulting local plant pathologists for severe cases

Remember: Accurate disease diagnosis can save crops and livelihoods. Be thorough, cautious, and always prioritize farmer safety and crop health."""

    def _create_prompt_template(self) -> ChatPromptTemplate:
        """Create the prompt template for farmer questions"""
        template = """
{system_prompt}

FARMER'S CONTEXT:
- Location: {location}
- Crop Focus: {crop_type}
- Language: {language}

FARMER'S QUESTION:
{question}

Please provide a comprehensive, practical response that addresses the farmer's specific question while considering their context. Structure your response with clear sections and actionable advice.

RESPONSE FORMAT:
**Direct Answer**
[Main answer to the question]

**Action Steps**
[Numbered list of practical steps]

**Timing Considerations**
[When to implement advice]

**Additional Tips**
[Extra recommendations and alternatives]

**Important Notes**
[Safety, limitations, or professional consultation needs]
"""
        return ChatPromptTemplate.from_template(template)

    async def get_agricultural_advice(
        self,
        question: str,
        location: Optional[str] = None,
        crop_type: Optional[str] = None,
        language: str = "en"
    ) -> Dict:
        if not self.llm:
            return {
                "answer": "I apologize, but the AI assistant is currently unavailable. Please check the API configuration.",
                "confidence_score": 0.0,
                "sources": [],
                "recommendations": ["Contact your local agricultural extension office for assistance"],
                "error": "LLM not initialized"
            }

        try:
            prompt_template = self._create_prompt_template()
            formatted_prompt = prompt_template.format(
                system_prompt=self.system_prompt,
                question=question,
                location=location or "Not specified",
                crop_type=crop_type or "General agriculture",
                language=language
            )
            messages = [HumanMessage(content=formatted_prompt)]
            response = await self.llm.ainvoke(messages)

            recommendations = self._extract_recommendations(response.content)
            confidence_score = self._calculate_confidence_score(response.content, question)
            sources = self._extract_sources(response.content)

            return {
                "answer": response.content,
                "confidence_score": confidence_score,
                "sources": sources,
                "recommendations": recommendations
            }

        except Exception as e:
            logger.error(f"Error getting agricultural advice: {e}")
            return {
                "answer": f"I encountered an error while processing your question: {str(e)}. Please try again or contact support.",
                "confidence_score": 0.0,
                "sources": [],
                "recommendations": ["Try rephrasing your question", "Contact local agricultural extension services"],
                "error": str(e)
            }

    def _extract_recommendations(self, response_text: str) -> List[str]:
        recommendations = []
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if (line and (line[0].isdigit() and '.' in line[:3] or line.startswith(('-', '*', '•')))):
                clean_rec = line.lstrip('0123456789.-•* ').strip()
                if len(clean_rec) > 10:
                    recommendations.append(clean_rec)
        if not recommendations:
            sentences = response_text.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20 and any(k in sentence.lower() for k in ['should', 'recommend', 'consider', 'try', 'use', 'apply', 'plant', 'harvest']):
                    recommendations.append(sentence + '.')
        return recommendations[:5]

    def _calculate_confidence_score(self, response_text: str, question: str) -> float:
        score = 0.5
        ag_terms = ['crop', 'soil', 'fertilizer', 'pest', 'disease', 'harvest', 'plant', 'seed', 'irrigation']
        score += min(sum(1 for t in ag_terms if t in response_text.lower()) * 0.05, 0.2)
        if '**' in response_text or '##' in response_text:
            score += 0.1
        action_words = ['should', 'can', 'try', 'consider', 'recommend', 'apply', 'use']
        score += min(sum(1 for w in action_words if w in response_text.lower()) * 0.02, 0.1)
        if 100 < len(response_text) < 2000:
            score += 0.1
        if 'consult' in response_text.lower() and 'extension' in response_text.lower():
            score += 0.05
        return min(score, 1.0)

    def _extract_sources(self, response_text: str) -> List[str]:
        return [
            "Agricultural best practices database",
            "Climate-smart agriculture guidelines",
            "Integrated pest management protocols"
        ]

    def _encode_image_to_base64(self, image_data: bytes) -> str:
        return base64.b64encode(image_data).decode("utf-8")

    def _validate_image(self, image_data: bytes) -> bool:
        image_headers = {
            b'\xff\xd8\xff': 'jpeg',
            b'\x89\x50\x4e\x47': 'png',
            b'\x47\x49\x46\x38': 'gif',
            b'\x52\x49\x46\x46': 'webp'
        }
        return any(image_data.startswith(h) for h in image_headers)

    async def detect_crop_disease(
        self,
        image_data: bytes,
        crop_type: Optional[str] = None,
        location: Optional[str] = None,
        additional_symptoms: Optional[str] = None
    ) -> Dict:
        if not self.vision_llm:
            return {
                "diagnosis": "Vision AI service is currently unavailable. Please check the API configuration.",
                "confidence": "Low",
                "severity": "Unknown",
                "treatment_recommendations": ["Contact your local agricultural extension office for visual diagnosis"],
                "management_strategy": ["Consult with your local pathologist"],
                "error": "Vision LLM not initialized"
            }

        try:
            if not self._validate_image(image_data):
                return {
                    "diagnosis": "Invalid image format. Please upload a clear JPEG, PNG, GIF, or WebP image.",
                    "confidence": "Low",
                    "severity": "Unknown",
                    "treatment_recommendations": ["Upload a clear, high-quality image of the affected plant"],
                    "management_strategy": ["Ensure good lighting and focus when taking plant photos"],
                    "error": "Invalid image format"
                }

            base64_image = self._encode_image_to_base64(image_data)

            diagnostic_context = f"""
{self.disease_detection_prompt}

DIAGNOSTIC CONTEXT:
- Crop Type: {crop_type or 'Unknown - please identify from image'}
- Location: {location or 'Not specified'}
- Additional Symptoms: {additional_symptoms or 'None provided'}

Please analyze the uploaded plant image and provide a comprehensive diagnostic report following the structured format above.
"""

            messages = [
                HumanMessage(
                    content=[
                        {"type": "text", "text": diagnostic_context},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                )
            ]

            response = await self.vision_llm.ainvoke(messages)
            diagnosis_data = self._parse_disease_diagnosis(response.content)
            diagnosis_data.update({
                "crop_type": crop_type,
                "location": location,
                "additional_symptoms": additional_symptoms,
                "model_used": "llama-3.2-90b-vision-preview"
            })

            return diagnosis_data

        except Exception as e:
            logger.error(f"Error in crop disease detection: {e}")
            return {
                "diagnosis": f"I encountered an error while analyzing the image: {str(e)}. Please try again with a clear, well-lit image.",
                "confidence": "Low",
                "severity": "Unknown",
                "treatment_recommendations": [
                    "Try uploading the image again",
                    "Ensure the image is clear and well-lit",
                    "Contact local agricultural extension services",
                    "Consult with a plant pathologist if symptoms persist"
                ],
                "management_strategy": [
                    "Monitor plant closely for symptom changes",
                    "Isolate affected plants if possible",
                    "Document symptoms with multiple photos"
                ],
                "model_used": "llama-3.2-90b-vision-preview",
                "error": str(e)
            }

    def _parse_disease_diagnosis(self, response_text: str) -> Dict:
        diagnosis_data = {
            "diagnosis": "Analysis completed",
            "confidence": "Medium",
            "severity": "Unknown",
            "treatment_recommendations": [],
            "management_strategy": [],
            "full_analysis": response_text
        }

        try:
            # Primary diagnosis
            if "Primary Diagnosis" in response_text or "**Primary Diagnosis**" in response_text:
                lines = response_text.split('\n')
                for i, line in enumerate(lines):
                    if "Primary Diagnosis" in line or "**Primary Diagnosis**" in line:
                        for j in range(i + 1, min(i + 5, len(lines))):
                            if lines[j].strip() and not lines[j].startswith('#') and not lines[j].startswith('**'):
                                diagnosis_data["diagnosis"] = lines[j].strip('- ').strip()
                                break

            # Confidence
            for indicator in ["High", "Medium", "Low"]:
                if indicator in response_text:
                    diagnosis_data["confidence"] = indicator
                    break

            # Severity
            for sev in ["Mild", "Moderate", "Severe"]:
                if sev.lower() in response_text.lower():
                    diagnosis_data["severity"] = sev
                    break

            # Treatment and management
            treatment_section = self._extract_section(response_text, ["Treatment Recommendations", "**Treatment Recommendations**"])
            if treatment_section:
                diagnosis_data["treatment_recommendations"] = self._extract_list_items(treatment_section)

            management_section = self._extract_section(response_text, ["Management Strategy", "**Management Strategy**"])
            if management_section:
                diagnosis_data["management_strategy"] = self._extract_list_items(management_section)

        except Exception as e:
            logger.warning(f"Error parsing diagnosis response: {e}")

        return diagnosis_data

    def _extract_section(self, text: str, section_headers: List[str]) -> str:
        lines = text.split('\n')
        section_content = []
        in_section = False
        for line in lines:
            if any(header in line for header in section_headers):
                in_section = True
                continue
            if in_section and line.startswith('**') and line.endswith('**'):
                break
            if in_section and line.strip():
                section_content.append(line)
        return '\n'.join(section_content)

    def _extract_list_items(self, text: str) -> List[str]:
        items = []
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and ((line[0].isdigit() and '.' in line[:3]) or line.startswith(('-', '*', '•'))):
                clean_item = line.lstrip('0123456789.-•* ').strip()
                if len(clean_item) > 5:
                    items.append(clean_item)
        return items[:8]
