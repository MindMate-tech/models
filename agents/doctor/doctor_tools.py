"""
Tool library for Doctor Agent with Dedalus tool calling
Provides functions that can be called by the AI to answer doctor queries
"""
import sys
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db.supabase_client import get_supabase
from agents.doctor.predictive_scoring import predictor


class DoctorTools:
    """Tools that can be called by Dedalus agent to answer doctor queries"""

    def __init__(self):
        self.supabase = get_supabase()
        self.predictor = predictor

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

    def get_patient_by_id(self, patient_id: str) -> Dict:
        """
        Get detailed patient information by ID

        Args:
            patient_id: UUID of the patient

        Returns:
            Patient details with session history
        """
        result = self.supabase.table("patients").select("*").eq("patient_id", patient_id).execute()

        if not result.data:
            return {"error": f"Patient {patient_id} not found"}

        patient = result.data[0]

        # Get sessions
        sessions = (
            self.supabase.table("sessions")
            .select("*")
            .eq("patient_id", patient_id)
            .order("session_date", desc=True)
            .execute()
        )

        return {
            "patient_id": patient.get('patient_id'),
            "name": patient.get('name'),
            "age": self._calculate_age(patient.get('dob')),
            "dob": patient.get('dob'),
            "gender": patient.get('gender'),
            "total_sessions": len(sessions.data),
            "sessions": sessions.data
        }

    def search_patients(self, name: Optional[str] = None, gender: Optional[str] = None,
                       min_age: Optional[int] = None, max_age: Optional[int] = None) -> List[Dict]:
        """
        Search for patients by various criteria

        Args:
            name: Patient name (partial match)
            gender: Patient gender
            min_age: Minimum age
            max_age: Maximum age

        Returns:
            List of matching patients
        """
        patients_result = self.supabase.table("patients").select("*").execute()

        results = []
        for patient in patients_result.data:
            age = self._calculate_age(patient.get('dob'))

            # Apply filters
            if name and name.lower() not in patient.get('name', '').lower():
                continue
            if gender and patient.get('gender') != gender:
                continue
            if min_age and age < min_age:
                continue
            if max_age and age > max_age:
                continue

            results.append({
                'patient_id': patient.get('patient_id'),
                'name': patient.get('name'),
                'age': age,
                'gender': patient.get('gender'),
                'dob': patient.get('dob')
            })

        return results

    def get_at_risk_patients(self, threshold: float = 0.5) -> List[Dict]:
        """
        Find patients at risk based on recent cognitive scores
        Includes detailed reasoning for why each patient is flagged

        Args:
            threshold: Score threshold (0-1). Patients below this are at risk.

        Returns:
            List of at-risk patients with detailed analysis
        """
        patients_result = self.supabase.table("patients").select("*").execute()

        at_risk = []

        for patient in patients_result.data:
            patient_id = patient.get('patient_id')

            # Get recent sessions (last 5)
            sessions = (
                self.supabase.table("sessions")
                .select("*")
                .eq("patient_id", patient_id)
                .order("session_date", desc=True)
                .limit(5)
                .execute()
            )

            if not sessions.data:
                continue

            # Calculate metrics
            scores = [s.get('overall_score', 0) for s in sessions.data if s.get('overall_score') is not None]

            if not scores:
                continue

            avg_score = sum(scores) / len(scores) / 100
            latest_score = scores[0] / 100

            # Check if at risk
            if avg_score < threshold or latest_score < threshold:
                # Analyze WHY they're at risk
                risk_reasons = []

                # Reason 1: Low average score
                if avg_score < threshold:
                    risk_reasons.append(f"Average score ({avg_score:.1%}) below threshold ({threshold:.0%})")

                # Reason 2: Declining trend
                if len(scores) >= 3:
                    first_three_avg = sum(scores[-3:]) / 3 / 100
                    if avg_score < first_three_avg * 0.8:
                        decline_pct = ((first_three_avg - avg_score) / first_three_avg * 100)
                        risk_reasons.append(f"Declining trend: {decline_pct:.0f}% drop from earlier sessions")

                # Reason 3: Latest session very low
                if latest_score < 0.3:
                    risk_reasons.append(f"Latest session critically low ({latest_score:.1%})")

                # Reason 4: Inconsistent performance
                if len(scores) >= 2:
                    score_variance = max(scores) / 100 - min(scores) / 100
                    if score_variance > 0.3:
                        risk_reasons.append(f"High score variability ({score_variance:.1%} range)")

                # Reason 5: Missing recent sessions
                if len(sessions.data) < 3:
                    risk_reasons.append(f"Limited session data ({len(sessions.data)} sessions)")

                at_risk.append({
                    'patient_id': patient_id,
                    'name': patient.get('name'),
                    'age': self._calculate_age(patient.get('dob')),
                    'average_score': avg_score,
                    'latest_score': latest_score,
                    'risk_level': 'critical' if latest_score < 0.3 else 'high' if avg_score < 0.5 else 'medium',
                    'sessions_analyzed': len(scores),
                    'risk_reasons': risk_reasons,
                    'trend': 'declining' if len(scores) >= 3 and scores[0] < scores[-1] else 'stable'
                })

        # Sort by risk (lowest score first)
        at_risk.sort(key=lambda x: x['average_score'])

        return at_risk

    def compare_patients(self, patient_ids: List[str]) -> Dict:
        """
        Compare multiple patients across various metrics

        Args:
            patient_ids: List of patient IDs to compare

        Returns:
            Comparison analysis with insights
        """
        if len(patient_ids) < 2:
            return {"error": "Need at least 2 patients to compare"}

        patients_data = []

        for patient_id in patient_ids:
            patient_info = self.get_patient_by_id(patient_id)

            if "error" in patient_info:
                continue

            # Calculate metrics
            sessions = patient_info.get('sessions', [])
            scores = [s.get('overall_score', 0) for s in sessions if s.get('overall_score') is not None]

            if scores:
                avg_score = sum(scores) / len(scores) / 100
                latest_score = scores[0] / 100

                # Calculate trend
                if len(scores) >= 3:
                    early_avg = sum(scores[-3:]) / 3 / 100
                    trend_direction = "improving" if avg_score > early_avg else "declining"
                    trend_magnitude = abs(avg_score - early_avg)
                else:
                    trend_direction = "insufficient_data"
                    trend_magnitude = 0

                patients_data.append({
                    'patient_id': patient_id,
                    'name': patient_info.get('name'),
                    'age': patient_info.get('age'),
                    'gender': patient_info.get('gender'),
                    'total_sessions': len(sessions),
                    'average_score': avg_score,
                    'latest_score': latest_score,
                    'trend_direction': trend_direction,
                    'trend_magnitude': trend_magnitude,
                    'score_history': [s / 100 for s in scores[:10]]  # Last 10 sessions
                })

        if len(patients_data) < 2:
            return {"error": "Not enough valid patients to compare"}

        # Generate comparison insights
        insights = []

        # Who has the best/worst average score?
        best_patient = max(patients_data, key=lambda x: x['average_score'])
        worst_patient = min(patients_data, key=lambda x: x['average_score'])

        insights.append(f"{best_patient['name']} has the highest average score ({best_patient['average_score']:.1%})")
        insights.append(f"{worst_patient['name']} has the lowest average score ({worst_patient['average_score']:.1%})")

        # Who is improving/declining?
        improving = [p for p in patients_data if p['trend_direction'] == 'improving']
        declining = [p for p in patients_data if p['trend_direction'] == 'declining']

        if improving:
            insights.append(f"{len(improving)} patient(s) showing improvement: {', '.join(p['name'] for p in improving)}")

        if declining:
            insights.append(f"{len(declining)} patient(s) declining: {', '.join(p['name'] for p in declining)}")

        # Age correlation
        avg_age = sum(p['age'] for p in patients_data) / len(patients_data)
        insights.append(f"Average age: {avg_age:.0f} years")

        return {
            'patients_compared': len(patients_data),
            'patients': patients_data,
            'insights': insights,
            'summary': {
                'best_performer': best_patient['name'],
                'needs_attention': worst_patient['name'],
                'average_score_all': sum(p['average_score'] for p in patients_data) / len(patients_data)
            }
        }

    def analyze_patient_decline(self, patient_id: str) -> Dict:
        """
        Detailed analysis of why a patient's scores are declining

        Args:
            patient_id: Patient UUID

        Returns:
            Analysis with potential causes and recommendations
        """
        patient_info = self.get_patient_by_id(patient_id)

        if "error" in patient_info:
            return patient_info

        sessions = patient_info.get('sessions', [])

        if len(sessions) < 3:
            return {
                "error": "Need at least 3 sessions to analyze decline",
                "patient": patient_info['name']
            }

        scores = [s.get('overall_score', 0) for s in sessions if s.get('overall_score') is not None]

        # Calculate decline metrics
        recent_scores = scores[:3]  # Last 3
        older_scores = scores[-3:] if len(scores) >= 6 else scores[3:]  # Earlier ones

        recent_avg = sum(recent_scores) / len(recent_scores) / 100
        older_avg = sum(older_scores) / len(older_scores) / 100 if older_scores else recent_avg

        decline_rate = ((older_avg - recent_avg) / older_avg * 100) if older_avg > 0 else 0

        # Analyze patterns
        findings = []

        if decline_rate > 20:
            findings.append({
                "finding": "Rapid cognitive decline detected",
                "severity": "high",
                "detail": f"{decline_rate:.0f}% decline from earlier sessions"
            })

        # Check for session gaps
        session_dates = [datetime.fromisoformat(s.get('session_date', '').replace('Z', '')) for s in sessions if s.get('session_date')]

        if len(session_dates) >= 2:
            gaps = [(session_dates[i] - session_dates[i+1]).days for i in range(len(session_dates)-1)]
            avg_gap = sum(gaps) / len(gaps)

            if avg_gap > 7:
                findings.append({
                    "finding": "Irregular session attendance",
                    "severity": "medium",
                    "detail": f"Average {avg_gap:.0f} days between sessions (weekly recommended)"
                })

        # Check score consistency
        score_variance = max(scores) - min(scores)

        if score_variance > 30:
            findings.append({
                "finding": "High performance variability",
                "severity": "medium",
                "detail": f"{score_variance:.0f} point score range indicates inconsistent performance"
            })

        recommendations = []

        if decline_rate > 20:
            recommendations.append("Immediate medical evaluation recommended")
            recommendations.append("Increase session frequency to monitor progression")

        if avg_gap > 7:
            recommendations.append("Improve adherence to weekly session schedule")

        if recent_avg < 0.5:
            recommendations.append("Consider additional cognitive support interventions")

        return {
            'patient_id': patient_id,
            'patient_name': patient_info['name'],
            'decline_rate': f"{decline_rate:.1f}%",
            'recent_average': recent_avg,
            'earlier_average': older_avg,
            'sessions_analyzed': len(sessions),
            'findings': findings,
            'recommendations': recommendations,
            'risk_level': 'critical' if decline_rate > 30 else 'high' if decline_rate > 20 else 'moderate'
        }

    def get_session_summary(self, patient_id: str, limit: int = 10) -> Dict:
        """
        Get summary of recent sessions for a patient

        Args:
            patient_id: Patient UUID
            limit: Number of recent sessions to include

        Returns:
            Session history with trends
        """
        sessions = (
            self.supabase.table("sessions")
            .select("*")
            .eq("patient_id", patient_id)
            .order("session_date", desc=True)
            .limit(limit)
            .execute()
        )

        if not sessions.data:
            return {"error": "No sessions found", "patient_id": patient_id}

        session_list = []
        for session in sessions.data:
            session_list.append({
                'session_id': session.get('session_id'),
                'date': session.get('session_date'),
                'score': session.get('overall_score', 0) / 100,
                'duration_minutes': session.get('duration_minutes'),
                'notes': session.get('notes', '')
            })

        return {
            'patient_id': patient_id,
            'total_sessions': len(session_list),
            'sessions': session_list
        }

    def predict_decline_risk(self, min_probability: float = 0.4) -> List[Dict]:
        """
        Predict which patients are likely to decline in the next month

        Args:
            min_probability: Minimum decline probability to include (0-1)

        Returns:
            List of patients with decline predictions, sorted by risk
        """
        predictions = self.predictor.predict_all_patients(min_decline_prob=min_probability)

        # Add cache info
        cache_info = self.predictor.get_cache_info()

        return {
            'predictions': predictions,
            'count': len(predictions),
            'cache_info': cache_info,
            'threshold': min_probability
        }

    def get_session_by_id(self, session_id: str) -> Dict:
        """
        Get detailed information about a specific session

        Args:
            session_id: UUID of the session

        Returns:
            Session details with patient context and analysis
        """
        try:
            session_result = self.supabase.table("sessions").select("*").eq("session_id", session_id).execute()

            if not session_result.data:
                return {"error": f"Session {session_id} not found"}
        except Exception as e:
            return {"error": f"Invalid session_id format or database error: {str(e)}"}

        session = session_result.data[0]
        patient_id = session.get('patient_id')

        # Get patient info for context
        patient_result = self.supabase.table("patients").select("*").eq("patient_id", patient_id).execute()

        patient_name = "Unknown"
        patient_age = 0

        if patient_result.data:
            patient = patient_result.data[0]
            patient_name = patient.get('name', 'Unknown')
            patient_age = self._calculate_age(patient.get('dob'))

        # Get other sessions for comparison
        other_sessions = (
            self.supabase.table("sessions")
            .select("*")
            .eq("patient_id", patient_id)
            .order("session_date", desc=True)
            .limit(5)
            .execute()
        )

        # Calculate how this session compares to others
        all_scores = [s.get('overall_score', 0) for s in other_sessions.data if s.get('overall_score') is not None]
        current_score = session.get('overall_score', 0)

        comparison = "N/A"
        if len(all_scores) > 1:
            avg_other_scores = sum([s for s in all_scores if s != current_score]) / max(1, len(all_scores) - 1)
            if current_score > avg_other_scores * 1.1:
                comparison = "Above average"
            elif current_score < avg_other_scores * 0.9:
                comparison = "Below average"
            else:
                comparison = "Average"

        # Extract AI analysis if available
        ai_data = session.get('ai_extracted_data', {})

        return {
            'session_id': session_id,
            'patient_id': patient_id,
            'patient_name': patient_name,
            'patient_age': patient_age,
            'session_date': session.get('session_date'),
            'overall_score': current_score,
            'duration_minutes': session.get('duration_minutes'),
            'exercise_type': session.get('exercise_type'),
            'comparison_to_average': comparison,
            'total_patient_sessions': len(other_sessions.data),
            'ai_analysis': {
                'memories_extracted': ai_data.get('memories_extracted', []),
                'cognitive_test_scores': ai_data.get('cognitive_test_scores', []),
                'notable_events': ai_data.get('notable_events', []),
                'doctor_alerts': ai_data.get('doctor_alerts', [])
            },
            'notes': session.get('notes', '')
        }

    def analyze_session_performance(self, session_id: str) -> Dict:
        """
        Detailed performance analysis for a specific session

        Args:
            session_id: UUID of the session

        Returns:
            Analysis with insights, concerns, and recommendations
        """
        session_info = self.get_session_by_id(session_id)

        if "error" in session_info:
            return session_info

        score = session_info.get('overall_score', 0)
        comparison = session_info.get('comparison_to_average', 'N/A')
        ai_analysis = session_info.get('ai_analysis', {})

        # Analyze performance
        findings = []

        # Score analysis
        if score < 30:
            findings.append({
                "category": "Critical Performance",
                "finding": f"Very low score ({score}%)",
                "severity": "critical"
            })
        elif score < 50:
            findings.append({
                "category": "Below Threshold",
                "finding": f"Score ({score}%) below acceptable level",
                "severity": "high"
            })
        elif score > 80:
            findings.append({
                "category": "Strong Performance",
                "finding": f"Score ({score}%) above average",
                "severity": "positive"
            })

        # Comparison analysis
        if comparison == "Below average":
            findings.append({
                "category": "Declining Performance",
                "finding": "Performance below patient's typical level",
                "severity": "medium"
            })

        # AI alerts
        alerts = ai_analysis.get('doctor_alerts', [])
        if alerts:
            for alert in alerts:
                findings.append({
                    "category": "AI Alert",
                    "finding": alert,
                    "severity": "high"
                })

        recommendations = []

        if score < 50:
            recommendations.append("Consider immediate follow-up session")
            recommendations.append("Review patient's medication and sleep patterns")

        if comparison == "Below average":
            recommendations.append("Investigate recent life changes or stressors")

        if len(findings) == 0:
            findings.append({
                "category": "Normal Performance",
                "finding": "No significant concerns identified",
                "severity": "none"
            })
            recommendations.append("Continue regular session schedule")

        return {
            'session_id': session_id,
            'patient_name': session_info.get('patient_name'),
            'session_date': session_info.get('session_date'),
            'score': score,
            'comparison': comparison,
            'findings': findings,
            'recommendations': recommendations,
            'ai_alerts': alerts
        }
