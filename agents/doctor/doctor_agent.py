"""Doctor-facing agent for patient management"""
import asyncio
from typing import Dict, List, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dedalus_labs import AsyncDedalus, DedalusRunner

class DoctorAgent:
    """Agent for doctor queries and patient management"""
    
    def __init__(self):
        self.client = AsyncDedalus()
        self.runner = DedalusRunner(self.client)
        
        # Mock patient database (would be real DB in production)
        self.patient_db = {
            "p001": {
                "patient_id": "p001",
                "name": "Margaret",
                "age": 68,
                "diagnosis": "early-onset dementia",
                "last_checkin": "2025-11-08",
                "baseline_score": 0.85,
                "current_score": 0.46,
                "risk_level": "high",
                "mri_summary": "Mild hippocampal atrophy",
                "recent_alerts": [
                    {"date": "2025-11-08", "type": "cognitive_decline", "severity": "high"},
                    {"date": "2025-11-07", "type": "temporal_disorientation", "severity": "medium"}
                ]
            },
            "p002": {
                "patient_id": "p002",
                "name": "Robert",
                "age": 72,
                "diagnosis": "mild cognitive impairment",
                "last_checkin": "2025-11-08",
                "baseline_score": 0.75,
                "current_score": 0.73,
                "risk_level": "low",
                "mri_summary": "Normal volumetrics",
                "recent_alerts": []
            }
        }
    
    async def lookup_patient(self, patient_id: str = None, query: str = None) -> Dict:
        """Look up patient by ID or natural language query"""
        
        if patient_id:
            # Direct lookup
            patient = self.patient_db.get(patient_id)
            if patient:
                return patient
            else:
                return {"error": f"Patient {patient_id} not found"}
        
        elif query:
            # Natural language search using LLM
            try:
                result = await self.runner.run(
                    input=f"""You are helping a doctor search for patients.

            Doctor's query: "{query}"

            Available patients:
            {self._format_patients_for_search()}

            Return the patient_id(s) that match, or explain if no match.
            Return JSON: {{"patient_ids": ["p001"], "reasoning": "..."}}""",
                                model="anthropic/claude-sonnet-4-20250514",
                                stream=False
                            )
                return {"search_result": result.final_output}
            except Exception as e:
                return {"error": str(e), "fallback": "Use direct patient_id lookup"}
            
        return {"error": "You must provide either a patient_id or a query."}
    
    def _format_patients_for_search(self) -> str:
        """Format patient data for LLM search"""
        formatted = []
        for pid, patient in self.patient_db.items():
            formatted.append(f"{pid}: {patient['name']}, {patient['age']}y, {patient['diagnosis']}, risk: {patient['risk_level']}")
        return "\n".join(formatted)
    
    async def get_dashboard(self, patient_id: str) -> Dict:
        """Get comprehensive dashboard data for a patient"""
        
        patient = self.patient_db.get(patient_id)
        if not patient:
            return {"error": f"Patient {patient_id} not found"}
        
        # Mock timeline data (would come from database)
        timeline = [
            {"date": "2025-11-01", "cognitive_score": 0.85, "mood": "happy"},
            {"date": "2025-11-02", "cognitive_score": 0.83, "mood": "neutral"},
            {"date": "2025-11-03", "cognitive_score": 0.80, "mood": "happy"},
            {"date": "2025-11-04", "cognitive_score": 0.75, "mood": "frustrated"},
            {"date": "2025-11-05", "cognitive_score": 0.70, "mood": "frustrated"},
            {"date": "2025-11-06", "cognitive_score": 0.65, "mood": "confused"},
            {"date": "2025-11-07", "cognitive_score": 0.55, "mood": "anxious"},
            {"date": "2025-11-08", "cognitive_score": 0.46, "mood": "confused"},
        ]
        
        return {
            **patient,
            "timeline": timeline,
            "metrics": {
                "decline_rate": f"{((patient['baseline_score'] - patient['current_score']) / patient['baseline_score'] * 100):.1f}%",
                "days_monitored": len(timeline),
                "avg_daily_score": sum(d['cognitive_score'] for d in timeline) / len(timeline)
            }
        }
    
    async def generate_report(self, patient_id: str, timeframe: str = "7 days") -> str:
        """Generate medical report for doctor"""
        
        dashboard = await self.get_dashboard(patient_id)
        
        if "error" in dashboard:
            return dashboard["error"]
        
        try:
            result = await self.runner.run(
                input=f"""Generate a concise medical progress report.

Patient: {dashboard['name']}, {dashboard['age']} years old
Diagnosis: {dashboard['diagnosis']}
Timeframe: {timeframe}

Key Data:
- Baseline cognitive score: {dashboard['baseline_score']:.0%}
- Current score: {dashboard['current_score']:.0%}
- Decline rate: {dashboard['metrics']['decline_rate']}
- MRI findings: {dashboard['mri_summary']}
- Recent alerts: {len(dashboard['recent_alerts'])} high-priority

Timeline trend:
{dashboard['timeline'][-7:]}

Format as professional medical report with:
1. Executive Summary
2. Cognitive Assessment
3. MRI Correlation
4. Risk Factors
5. Recommendations

Be concise and actionable.""",
                model="anthropic/claude-sonnet-4-20250514",
                stream=False
            )
            return result.final_output
        except Exception as e:
            # Fallback template
            return f"""PATIENT PROGRESS REPORT
            
Patient: {dashboard['name']} (ID: {patient_id})
Period: {timeframe}

SUMMARY: Significant cognitive decline detected ({dashboard['metrics']['decline_rate']} from baseline)

COGNITIVE ASSESSMENT:
- Current Score: {dashboard['current_score']:.0%}
- Baseline: {dashboard['baseline_score']:.0%}

MRI FINDINGS: {dashboard['mri_summary']}

ALERTS: {len(dashboard['recent_alerts'])} high-priority alerts

RECOMMENDATION: Immediate neurologist consultation advised.
"""
    
    async def get_at_risk_patients(self) -> List[Dict]:
        """Get list of patients with high risk alerts"""
        at_risk = []
        for pid, patient in self.patient_db.items():
            if patient['risk_level'] in ['high', 'critical']:
                at_risk.append({
                    'patient_id': pid,
                    'name': patient['name'],
                    'risk_level': patient['risk_level'],
                    'recent_alerts': len(patient['recent_alerts'])
                })
        return at_risk
