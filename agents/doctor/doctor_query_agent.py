"""
Agentic Doctor Query Handler
Uses Dedalus tool calling to answer natural language queries from doctors
"""
import sys
import os
from typing import Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dedalus_labs import AsyncDedalus, DedalusRunner
from agents.doctor.doctor_tools import DoctorTools


class DoctorQueryAgent:
    """
    AI agent that handles doctor queries using tool calling
    Allows doctors to ask questions in natural language
    """

    def __init__(self):
        self.client = AsyncDedalus()
        self.runner = DedalusRunner(self.client)
        self.tools = DoctorTools()

    def _build_tools_description(self) -> str:
        """Build description of available tools for the AI"""
        return """
You are a medical AI assistant helping doctors query patient data.

You have access to these tools (call them as Python functions):

1. tools.get_patient_by_id(patient_id: str) -> Dict
   Get detailed patient information by ID

2. tools.search_patients(name: str = None, gender: str = None, min_age: int = None, max_age: int = None) -> List[Dict]
   Search for patients by various criteria

3. tools.get_at_risk_patients(threshold: float = 0.5) -> List[Dict]
   Find at-risk patients with detailed reasoning for why they're flagged
   Returns risk_reasons explaining the flags

4. tools.compare_patients(patient_ids: List[str]) -> Dict
   Compare multiple patients across metrics
   Returns insights and analysis

5. tools.analyze_patient_decline(patient_id: str) -> Dict
   Detailed analysis of why a patient is declining
   Returns findings, recommendations, and risk factors

6. tools.get_session_summary(patient_id: str, limit: int = 10) -> Dict
   Get recent session history for a patient

Always explain your reasoning and provide actionable insights.
When showing at-risk patients, include the risk_reasons to explain WHY they're flagged.
"""

    async def query(self, doctor_query: str, context: Dict = None) -> Dict:
        """
        Handle a doctor's natural language query

        Args:
            doctor_query: Natural language question from doctor
            context: Optional context (doctor_id, patient_id, etc.)

        Returns:
            Response with data and AI analysis
        """
        context = context or {}

        try:
            # First, use AI to determine intent and extract parameters
            intent_prompt = f"""You are a medical AI routing system. Analyze this doctor's query and determine what they want.

Doctor's Query: "{doctor_query}"

Available actions:
1. at_risk - Find at-risk patients
2. decline_analysis - Analyze why a patient is declining
3. compare - Compare multiple patients
4. search - Search for patients by criteria
5. patient_info - Get patient details

Respond in JSON format:
{{
  "action": "action_name",
  "parameters": {{parameter details}},
  "reasoning": "why you chose this action"
}}

Example:
Query: "Show me at-risk patients"
Response: {{"action": "at_risk", "parameters": {{"threshold": 0.5}}, "reasoning": "Doctor wants to see patients below 50% score"}}
"""

            # Get intent from AI
            intent_result = await self.runner.run(
                input=intent_prompt,
                model="anthropic/claude-sonnet-4-20250514",
                stream=False
            )

            intent_response = intent_result.final_output

            # Parse intent and execute appropriate tool
            query_lower = doctor_query.lower()

            # Route based on query content
            if 'at risk' in query_lower or 'at-risk' in query_lower or 'high risk' in query_lower:
                tool_result = self.tools.get_at_risk_patients(threshold=0.5)
                tool_name = "get_at_risk_patients"

            elif 'declin' in query_lower and context.get('patient_id'):
                tool_result = self.tools.analyze_patient_decline(context['patient_id'])
                tool_name = "analyze_patient_decline"

            elif 'compar' in query_lower:
                # Extract patient IDs from query or context
                # For MVP, get first 2 patients if not specified
                patient_ids = []
                if context.get('patient_ids'):
                    patient_ids = context['patient_ids']
                else:
                    # Get 2 patients for comparison
                    patients = self.tools.supabase.table("patients").select("patient_id").limit(2).execute()
                    patient_ids = [p['patient_id'] for p in patients.data]

                tool_result = self.tools.compare_patients(patient_ids)
                tool_name = "compare_patients"

            elif 'female' in query_lower or 'male' in query_lower or 'search' in query_lower or 'find' in query_lower:
                gender = 'female' if 'female' in query_lower else 'male' if 'male' in query_lower else None
                tool_result = self.tools.search_patients(gender=gender)
                tool_name = "search_patients"

            elif context.get('patient_id'):
                tool_result = self.tools.get_patient_by_id(context['patient_id'])
                tool_name = "get_patient_by_id"

            else:
                # Default to at-risk
                tool_result = self.tools.get_at_risk_patients(threshold=0.5)
                tool_name = "get_at_risk_patients"

            # Now use AI to analyze the results and generate response
            analysis_prompt = f"""You are a medical AI assistant. A doctor asked: "{doctor_query}"

I executed the tool: {tool_name}

Results:
{tool_result}

Provide a comprehensive medical analysis including:
1. Key findings from the data
2. Risk factors or concerns
3. Specific reasoning for each risk flag
4. Actionable recommendations

Be professional, clear, and actionable. Include specific data points and percentages.
"""

            analysis_result = await self.runner.run(
                input=analysis_prompt,
                model="anthropic/claude-sonnet-4-20250514",
                stream=False
            )

            return {
                "success": True,
                "query": doctor_query,
                "response": analysis_result.final_output,
                "tools_used": [tool_name],
                "raw_data": tool_result
            }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "query": doctor_query
            }

    async def quick_lookup(self, patient_id: str) -> Dict:
        """Quick patient lookup without AI (faster for simple queries)"""
        try:
            data = self.tools.get_patient_by_id(patient_id)
            return {
                "success": True,
                "type": "quick_lookup",
                "data": data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def find_at_risk(self, threshold: float = 0.5) -> Dict:
        """Quick at-risk lookup without AI (faster for simple queries)"""
        try:
            data = self.tools.get_at_risk_patients(threshold)
            return {
                "success": True,
                "type": "at_risk_patients",
                "data": data,
                "count": len(data)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
