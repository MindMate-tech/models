"""Doctor-facing agent with real Supabase integration"""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dedalus_labs import AsyncDedalus, DedalusRunner
from db.supabase_client import get_supabase


class DoctorAgentSupabase:
    """Agent for doctor queries with real Supabase database"""

    def __init__(self):
        self.client = AsyncDedalus()
        self.runner = DedalusRunner(self.client)
        self.supabase = get_supabase()

    def _calculate_age(self, dob: str) -> int:
        """Calculate age from date of birth"""
        if not dob:
            return 0
        try:
            birth_date = datetime.fromisoformat(dob.replace('Z', ''))
            today = datetime.utcnow()
            return today.year - birth_date.year - (
                (today.month, today.day) < (birth_date.month, birth_date.day)
            )
        except:
            return 0

    async def lookup_patient(self, patient_id: str = None, query: str = None) -> Dict:
        """Look up patient by ID or natural language query"""

        if patient_id:
            # Direct lookup from Supabase
            result = self.supabase.table("patients").select("*").eq("patient_id", patient_id).execute()

            if result.data:
                patient = result.data[0]

                # Get sessions for this patient
                sessions = self.supabase.table("sessions").select("*").eq("patient_id", patient_id).order("session_date", desc=True).execute()

                # Calculate stats
                avg_score = 0
                if sessions.data:
                    scores = [s.get('overall_score', 0) for s in sessions.data if s.get('overall_score') is not None]
                    if scores:
                        avg_score = sum(scores) / len(scores)

                return {
                    "patient_id": patient.get('patient_id'),
                    "name": patient.get('name', 'Unknown'),
                    "age": self._calculate_age(patient.get('dob')),
                    "dob": patient.get('dob'),
                    "gender": patient.get('gender'),
                    "total_sessions": len(sessions.data),
                    "avg_score": avg_score,
                    "last_session": sessions.data[0].get('session_date') if sessions.data else None,
                    "recent_sessions": sessions.data[:5]
                }
            else:
                return {"error": f"Patient {patient_id} not found"}

        elif query:
            # Natural language search using AI
            try:
                # Get all patients from Supabase
                all_patients = self.supabase.table("patients").select("*").execute()

                # Format for AI search
                patient_list = []
                for p in all_patients.data:
                    patient_list.append({
                        'patient_id': p.get('patient_id'),
                        'name': p.get('name'),
                        'age': self._calculate_age(p.get('dob')),
                        'gender': p.get('gender')
                    })

                result = await self.runner.run(
                    input=f"""You are helping a doctor search for patients.

Doctor's query: "{query}"

Available patients:
{patient_list}

Return the patient_id(s) that match, or explain if no match.
Return JSON: {{"patient_ids": ["xxx"], "reasoning": "..."}}""",
                    model="anthropic/claude-sonnet-4-20250514",
                    stream=False
                )
                return {"search_result": result.final_output, "total_patients": len(all_patients.data)}

            except Exception as e:
                return {"error": str(e), "fallback": "Use direct patient_id lookup"}

        return {"error": "You must provide either a patient_id or a query."}

    async def get_dashboard(self, patient_id: str) -> Dict:
        """Get comprehensive dashboard data for a patient"""

        # Fetch patient from Supabase
        patient_result = self.supabase.table("patients").select("*").eq("patient_id", patient_id).execute()

        if not patient_result.data:
            return {"error": f"Patient {patient_id} not found"}

        patient = patient_result.data[0]

        # Fetch all sessions
        sessions_result = (
            self.supabase.table("sessions")
            .select("*")
            .eq("patient_id", patient_id)
            .order("session_date", desc=True)
            .execute()
        )

        sessions = sessions_result.data

        # Build timeline from real sessions
        timeline = []
        for session in sessions:
            timeline.append({
                "date": session.get('session_date', ''),
                "cognitive_score": session.get('overall_score', 0) / 100 if session.get('overall_score') else 0.5,
                "session_id": session.get('session_id')
            })

        # Calculate metrics
        if sessions:
            scores = [s.get('overall_score', 0) for s in sessions if s.get('overall_score') is not None]
            if scores:
                baseline_score = max(scores) / 100
                current_score = scores[0] / 100 if scores else 0.5
                avg_score = sum(scores) / len(scores) / 100
            else:
                baseline_score = current_score = avg_score = 0.5
        else:
            baseline_score = current_score = avg_score = 0.5

        decline_rate = ((baseline_score - current_score) / baseline_score * 100) if baseline_score > 0 else 0

        return {
            "patient_id": patient_id,
            "name": patient.get('name', 'Unknown'),
            "age": self._calculate_age(patient.get('dob')),
            "dob": patient.get('dob'),
            "gender": patient.get('gender'),
            "baseline_score": baseline_score,
            "current_score": current_score,
            "risk_level": "high" if current_score < 0.5 else "medium" if current_score < 0.7 else "low",
            "timeline": timeline,
            "metrics": {
                "decline_rate": f"{decline_rate:.1f}%",
                "days_monitored": len(timeline),
                "avg_daily_score": avg_score,
                "total_sessions": len(sessions)
            }
        }

    async def generate_report(self, patient_id: str, timeframe: str = "7 days") -> str:
        """Generate medical report for doctor using real data"""

        dashboard = await self.get_dashboard(patient_id)

        if "error" in dashboard:
            return dashboard["error"]

        try:
            result = await self.runner.run(
                input=f"""Generate a concise medical progress report.

Patient: {dashboard['name']}, {dashboard['age']} years old
Gender: {dashboard.get('gender', 'Unknown')}
Timeframe: {timeframe}

Key Data:
- Baseline cognitive score: {dashboard['baseline_score']:.0%}
- Current score: {dashboard['current_score']:.0%}
- Decline rate: {dashboard['metrics']['decline_rate']}
- Total sessions: {dashboard['metrics']['total_sessions']}
- Risk level: {dashboard['risk_level']}

Recent Timeline (last {min(7, len(dashboard['timeline']))} sessions):
{dashboard['timeline'][:7]}

Format as professional medical report with:
1. Executive Summary
2. Cognitive Assessment
3. Risk Factors
4. Recommendations

Be concise and actionable.""",
                model="anthropic/claude-sonnet-4-20250514",
                stream=False
            )
            return result.final_output

        except Exception as e:
            # Fallback template
            return f"""PATIENT PROGRESS REPORT

Patient: {dashboard['name']} (ID: {patient_id})
Age: {dashboard['age']} | Gender: {dashboard.get('gender', 'Unknown')}
Period: {timeframe}

SUMMARY: Current cognitive score at {dashboard['current_score']:.0%} ({dashboard['metrics']['decline_rate']} from baseline)

COGNITIVE ASSESSMENT:
- Current Score: {dashboard['current_score']:.0%}
- Baseline: {dashboard['baseline_score']:.0%}
- Total Sessions: {dashboard['metrics']['total_sessions']}

RISK LEVEL: {dashboard['risk_level'].upper()}

RECOMMENDATION: {"Immediate consultation advised" if dashboard['risk_level'] == 'high' else "Continue monitoring"}
"""

    async def get_at_risk_patients(self, threshold: float = 0.5) -> List[Dict]:
        """Get list of patients with scores below threshold"""

        # Get all patients
        patients_result = self.supabase.table("patients").select("*").execute()

        at_risk = []

        for patient in patients_result.data:
            patient_id = patient.get('patient_id')

            # Get recent sessions
            sessions = (
                self.supabase.table("sessions")
                .select("overall_score")
                .eq("patient_id", patient_id)
                .order("session_date", desc=True)
                .limit(3)
                .execute()
            )

            if sessions.data:
                # Calculate average recent score
                scores = [s.get('overall_score', 0) for s in sessions.data if s.get('overall_score') is not None]
                if scores:
                    avg_score = sum(scores) / len(scores) / 100

                    if avg_score < threshold:
                        at_risk.append({
                            'patient_id': patient_id,
                            'name': patient.get('name', 'Unknown'),
                            'age': self._calculate_age(patient.get('dob')),
                            'recent_score': avg_score,
                            'risk_level': 'high' if avg_score < 0.5 else 'medium',
                            'sessions_analyzed': len(scores)
                        })

        # Sort by score (lowest first)
        at_risk.sort(key=lambda x: x['recent_score'])

        return at_risk

    async def search_by_criteria(self, min_age: int = None, max_age: int = None,
                                 gender: str = None, min_sessions: int = None) -> List[Dict]:
        """Search patients by specific criteria"""

        # Get all patients
        patients_result = self.supabase.table("patients").select("*").execute()

        results = []

        for patient in patients_result.data:
            patient_id = patient.get('patient_id')
            age = self._calculate_age(patient.get('dob'))

            # Apply filters
            if min_age and age < min_age:
                continue
            if max_age and age > max_age:
                continue
            if gender and patient.get('gender') != gender:
                continue

            # Check session count if required
            if min_sessions:
                sessions = self.supabase.table("sessions").select("session_id").eq("patient_id", patient_id).execute()
                if len(sessions.data) < min_sessions:
                    continue

            results.append({
                'patient_id': patient_id,
                'name': patient.get('name', 'Unknown'),
                'age': age,
                'gender': patient.get('gender'),
                'dob': patient.get('dob')
            })

        return results
