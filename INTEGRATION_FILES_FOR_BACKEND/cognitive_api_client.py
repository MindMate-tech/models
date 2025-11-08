"""
Cognitive API Client
Integration with MindMate Cognitive Analysis microservice
"""
import httpx
from uuid import UUID
from typing import Dict, List, Optional
from datetime import datetime


# ⚠️ UPDATE THIS AFTER DEPLOYING TO RENDER
COGNITIVE_API_URL = "https://mindmate-cognitive-api.onrender.com"


async def analyze_session_with_ai(
    session_id: UUID,
    patient_id: UUID,
    transcript: str,
    patient_data: Dict,
    previous_sessions: Optional[List[Dict]] = None
) -> Dict:
    """
    Call MindMate Cognitive API to analyze a session

    Args:
        session_id: Session UUID
        patient_id: Patient UUID
        transcript: Full conversation transcript
        patient_data: Patient profile from Supabase
        previous_sessions: Recent historical sessions for context

    Returns:
        Complete analysis with memories, scores, metrics, alerts
    """

    # Calculate patient age
    age = calculate_age(patient_data.get("dob"))

    payload = {
        "session_id": str(session_id),
        "patient_id": str(patient_id),
        "transcript": transcript,
        "exercise_type": "memory_recall",
        "session_date": datetime.utcnow().isoformat(),
        "patient_profile": {
            "name": patient_data.get("name", "Patient"),
            "age": age,
            "diagnosis": patient_data.get("diagnosis", ""),
            "interests": patient_data.get("interests", []),
            "expected_info": {
                "family_members": [],  # Add from your patient data
                "profession": "",
                "hometown": ""
            }
        },
        "previous_sessions": previous_sessions or []
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{COGNITIVE_API_URL}/analyze/session",
                json=payload
            )

            if response.status_code != 200:
                raise Exception(f"Cognitive API error: {response.text}")

            result = response.json()
            return result["data"]

    except httpx.TimeoutException:
        raise Exception("Cognitive API timeout - analysis takes 60-120 seconds")
    except Exception as e:
        raise Exception(f"Failed to call Cognitive API: {str(e)}")


async def get_patient_dashboard(
    patient_id: UUID,
    patient_name: str,
    sessions: List[Dict],
    mri_csv_path: Optional[str] = None
) -> Dict:
    """
    Get complete dashboard data formatted for frontend

    Args:
        patient_id: Patient UUID
        patient_name: Patient name
        sessions: Historical sessions from Supabase
        mri_csv_path: Optional path to MRI CSV file

    Returns:
        PatientData formatted for frontend (brain regions, memory metrics, etc.)
    """

    payload = {
        "patient_id": str(patient_id),
        "patient_name": patient_name,
        "sessions": sessions,
        "mri_csv_path": mri_csv_path,
        "days_back": 30
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{COGNITIVE_API_URL}/patient/dashboard",
                json=payload
            )

            if response.status_code != 200:
                raise Exception(f"Cognitive API error: {response.text}")

            result = response.json()
            return result["data"]

    except httpx.TimeoutException:
        raise Exception("Cognitive API timeout")
    except Exception as e:
        raise Exception(f"Failed to get dashboard: {str(e)}")


async def analyze_mri_scan(
    patient_id: UUID,
    mri_csv_path: str,
    baseline_mri_path: Optional[str] = None
) -> Dict:
    """
    Analyze MRI scan and get brain region scores

    Args:
        patient_id: Patient UUID
        mri_csv_path: Path to current MRI CSV
        baseline_mri_path: Optional baseline for progression analysis

    Returns:
        Brain region scores, alerts, and comparison data
    """

    payload = {
        "patient_id": str(patient_id),
        "mri_csv_path": mri_csv_path,
        "baseline_mri_path": baseline_mri_path
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{COGNITIVE_API_URL}/mri/analyze",
                json=payload
            )

            if response.status_code != 200:
                raise Exception(f"Cognitive API error: {response.text}")

            result = response.json()
            return result["data"]

    except Exception as e:
        raise Exception(f"Failed to analyze MRI: {str(e)}")


async def health_check() -> Dict:
    """Check if Cognitive API is healthy"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{COGNITIVE_API_URL}/health")
            return response.json()
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


def calculate_age(dob: str) -> int:
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
