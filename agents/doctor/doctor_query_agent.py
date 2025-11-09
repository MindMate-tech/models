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
from agents.doctor.memory_store import session_memory


class DoctorQueryAgent:
    """
    AI agent that handles doctor queries using tool calling
    Allows doctors to ask questions in natural language

    Features:
    - Intelligent model routing (Haiku for simple, Sonnet for complex)
    - Sequential thinking for medical reasoning
    - Memory-augmented context
    """

    def __init__(self):
        self.client = AsyncDedalus()
        self.runner = DedalusRunner(self.client)
        self.tools = DoctorTools()

        # Model configuration
        self.HAIKU_MODEL = "anthropic/claude-3-5-haiku-20241022"
        self.SONNET_MODEL = "anthropic/claude-sonnet-4-20250514"

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

7. tools.get_session_by_id(session_id: str) -> Dict
   Get detailed information about a specific session
   Returns session data with patient context and AI analysis

8. tools.analyze_session_performance(session_id: str) -> Dict
   Detailed performance analysis for a specific session
   Returns findings, concerns, and recommendations

Always explain your reasoning and provide actionable insights.
When showing at-risk patients, include the risk_reasons to explain WHY they're flagged.
When analyzing sessions, provide context by comparing to patient's other sessions.
"""

    def _analyze_query_complexity(self, query: str) -> Dict:
        """
        Analyze query complexity to route to appropriate model

        Returns:
            Dict with complexity level and reasoning
        """
        query_lower = query.lower()

        # Simple queries - fast Haiku model
        simple_patterns = [
            'how many', 'count', 'list all', 'show all',
            'find all', 'find female', 'find male', 'search for',
            'who is', 'what is', 'patient id'
        ]

        # Complex queries - detailed Sonnet model
        complex_patterns = [
            'at risk', 'at-risk', 'high risk',
            'declining', 'decline', 'why',
            'analyze', 'analysis', 'explain',
            'compare', 'comparison', 'versus',
            'recommend', 'should i', 'what actions',
            'predict', 'forecast', 'next month'
        ]

        # Check for simple patterns
        for pattern in simple_patterns:
            if pattern in query_lower:
                return {
                    "complexity": "simple",
                    "model": self.HAIKU_MODEL,
                    "reasoning": f"Simple query detected: '{pattern}'"
                }

        # Check for complex patterns
        for pattern in complex_patterns:
            if pattern in query_lower:
                return {
                    "complexity": "complex",
                    "model": self.SONNET_MODEL,
                    "reasoning": f"Complex analysis required: '{pattern}'"
                }

        # Default to Sonnet for safety (medical queries)
        return {
            "complexity": "medium",
            "model": self.SONNET_MODEL,
            "reasoning": "Default to detailed model for medical safety"
        }

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
            # Check memory for follow-up context
            memory_context = session_memory.recall(context, doctor_query)

            if memory_context:
                print(f"🧠 Memory: Detected follow-up query")
                print(f"   Referring to previous query: \"{memory_context['previous_query']}\"")
                print(f"   Patient context: {len(memory_context['patient_ids'])} patients")

                # Add memory context to current context
                context['patient_ids'] = memory_context['patient_ids']
                context['is_follow_up'] = True
                context['previous_query'] = memory_context['previous_query']

            # Analyze query complexity and select appropriate model
            complexity_info = self._analyze_query_complexity(doctor_query)
            selected_model = complexity_info["model"]

            print(f"🧠 Query complexity: {complexity_info['complexity']}")
            print(f"📊 Model selected: {selected_model}")
            print(f"💡 Reasoning: {complexity_info['reasoning']}")

            # Parse intent and execute appropriate tool
            query_lower = doctor_query.lower()

            # Route based on query content and context
            # Session-specific queries (check session_id in context first)
            if context.get('session_id'):
                if 'analyz' in query_lower or 'perform' in query_lower or 'insight' in query_lower:
                    tool_result = self.tools.analyze_session_performance(context['session_id'])
                    tool_name = "analyze_session_performance"
                else:
                    # Default to getting session details
                    tool_result = self.tools.get_session_by_id(context['session_id'])
                    tool_name = "get_session_by_id"

            # Patient prediction queries
            elif 'predict' in query_lower or 'forecast' in query_lower or 'next month' in query_lower or 'will decline' in query_lower:
                tool_result = self.tools.predict_decline_risk(min_probability=0.4)
                tool_name = "predict_decline_risk"

            # At-risk queries
            elif 'at risk' in query_lower or 'at-risk' in query_lower or 'high risk' in query_lower:
                tool_result = self.tools.get_at_risk_patients(threshold=0.5)
                tool_name = "get_at_risk_patients"

            # Patient decline analysis
            elif 'declin' in query_lower and context.get('patient_id'):
                tool_result = self.tools.analyze_patient_decline(context['patient_id'])
                tool_name = "analyze_patient_decline"

            # Comparison queries
            elif 'compar' in query_lower or context.get('is_follow_up'):
                # Extract patient IDs from query or context (including memory)
                patient_ids = []
                if context.get('patient_ids'):
                    # Use patient IDs from memory or context
                    patient_ids = context['patient_ids'][:2]  # Compare first 2
                    tool_result = self.tools.compare_patients(patient_ids)
                    tool_name = "compare_patients"
                elif 'compar' in query_lower:
                    # Get 2 patients for comparison
                    patients = self.tools.supabase.table("patients").select("patient_id").limit(2).execute()
                    patient_ids = [p['patient_id'] for p in patients.data]
                    tool_result = self.tools.compare_patients(patient_ids)
                    tool_name = "compare_patients"
                else:
                    # Follow-up without comparison - fall through to default
                    tool_result = self.tools.get_at_risk_patients(threshold=0.5)
                    tool_name = "get_at_risk_patients"

            # Search queries
            elif 'female' in query_lower or 'male' in query_lower or 'search' in query_lower or 'find' in query_lower:
                gender = 'female' if 'female' in query_lower else 'male' if 'male' in query_lower else None
                tool_result = self.tools.search_patients(gender=gender)
                tool_name = "search_patients"

            # Patient-specific queries
            elif context.get('patient_id'):
                if 'session' in query_lower:
                    # Get session history for patient
                    tool_result = self.tools.get_session_summary(context['patient_id'], limit=10)
                    tool_name = "get_session_summary"
                else:
                    # Get patient details
                    tool_result = self.tools.get_patient_by_id(context['patient_id'])
                    tool_name = "get_patient_by_id"

            else:
                # Default to at-risk
                tool_result = self.tools.get_at_risk_patients(threshold=0.5)
                tool_name = "get_at_risk_patients"

            # Determine if we should use sequential thinking
            use_sequential_thinking = complexity_info["complexity"] == "complex" and (
                'at risk' in query_lower or 'declining' in query_lower or
                'analyze' in query_lower or 'why' in query_lower
            )

            # Build analysis prompt with optional sequential thinking
            if use_sequential_thinking:
                analysis_prompt = f"""You are a medical AI assistant. A doctor asked: "{doctor_query}"

I executed the tool: {tool_name}

Results:
{tool_result}

Provide a comprehensive medical analysis with SEQUENTIAL REASONING. Structure your response as:

## Reasoning Process
Show your step-by-step thinking:
1. ✅ Step 1 description
2. ✅ Step 2 description
3. ✅ Step 3 description
... (as many steps as needed)

## Key Findings
[Analysis results]

## Risk Factors & Concerns
[Specific risks identified]

## Actionable Recommendations
[What the doctor should do]

Be professional, clear, and actionable. Include specific data points and percentages.
"""
            else:
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
                model=selected_model,
                stream=False
            )

            result = {
                "success": True,
                "query": doctor_query,
                "response": analysis_result.final_output,
                "tools_used": [tool_name],
                "raw_data": tool_result,
                "model_info": {
                    "model": selected_model,
                    "complexity": complexity_info["complexity"],
                    "reasoning": complexity_info["reasoning"],
                    "sequential_thinking": use_sequential_thinking,
                    "memory_used": memory_context is not None
                }
            }

            # Store in memory for follow-up queries
            session_memory.remember(context, doctor_query, result)

            return result

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"❌ Query error: {e}")
            print(error_trace)
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
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
