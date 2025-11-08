"""
Integration Example: How to call MindMate Cognitive API from your existing backend

Add this to your existing FastAPI backend (the one with Supabase/ChromaDB)
"""
import httpx
from uuid import UUID
from typing import Dict, List
from datetime import datetime


# =============================================================================
# Configuration
# =============================================================================

MINDMATE_API_URL = "https://mindmate-cognitive-api.onrender.com"  # Your Render URL
# For local testing: "http://localhost:8000"


# =============================================================================
# Integration Functions
# =============================================================================

async def analyze_session_with_mindmate(
    session_id: UUID,
    patient_id: UUID,
    transcript: str,
    patient_data: Dict,
    previous_sessions: List[Dict] = None
) -> Dict:
    """
    Call MindMate API to analyze a video call session

    Args:
        session_id: Session UUID from your database
        patient_id: Patient UUID
        transcript: Full conversation transcript
        patient_data: Patient profile from Supabase
        previous_sessions: Recent historical sessions for context

    Returns:
        Complete analysis with memories, scores, alerts
    """

    payload = {
        "session_id": str(session_id),
        "patient_id": str(patient_id),
        "transcript": transcript,
        "exercise_type": "memory_recall",
        "session_date": datetime.utcnow().isoformat(),
        "patient_profile": {
            "name": patient_data.get("name"),
            "age": calculate_age(patient_data.get("dob")),
            "interests": ["family", "hobbies"],  # Add from your data
            "expected_info": {
                "family_members": [],  # Add from your data
                "profession": "",
                "hometown": ""
            }
        },
        "previous_sessions": previous_sessions or []
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{MINDMATE_API_URL}/analyze/session",
            json=payload
        )

        if response.status_code != 200:
            raise Exception(f"MindMate API error: {response.text}")

        result = response.json()
        return result["data"]


async def get_patient_dashboard_data(
    patient_id: UUID,
    patient_name: str,
    sessions: List[Dict],
    mri_csv_path: str = None
) -> Dict:
    """
    Get complete dashboard data formatted for frontend

    Args:
        patient_id: Patient UUID
        patient_name: Patient name
        sessions: Historical sessions from Supabase
        mri_csv_path: Optional path to MRI CSV

    Returns:
        PatientData formatted for frontend
    """

    payload = {
        "patient_id": str(patient_id),
        "patient_name": patient_name,
        "sessions": sessions,
        "mri_csv_path": mri_csv_path,
        "days_back": 30
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{MINDMATE_API_URL}/patient/dashboard",
            json=payload
        )

        if response.status_code != 200:
            raise Exception(f"MindMate API error: {response.text}")

        result = response.json()
        return result["data"]


async def analyze_mri_scan(
    patient_id: UUID,
    mri_csv_path: str,
    baseline_mri_path: str = None
) -> Dict:
    """
    Analyze MRI scan and get brain region scores

    Args:
        patient_id: Patient UUID
        mri_csv_path: Path to current MRI CSV
        baseline_mri_path: Optional baseline for comparison

    Returns:
        Brain region scores and alerts
    """

    payload = {
        "patient_id": str(patient_id),
        "mri_csv_path": mri_csv_path,
        "baseline_mri_path": baseline_mri_path
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{MINDMATE_API_URL}/mri/analyze",
            json=payload
        )

        if response.status_code != 200:
            raise Exception(f"MindMate API error: {response.text}")

        result = response.json()
        return result["data"]


# =============================================================================
# Add to Your Existing Routes
# =============================================================================

"""
EXAMPLE 1: Modify your /sessions/analyze endpoint

from fastapi import APIRouter, BackgroundTasks, HTTPException
from uuid import UUID
from db.supabase_client import get_supabase

router = APIRouter()
supabase = get_supabase()

@router.post("/sessions/analyze/{session_id}")
async def analyze_session(session_id: UUID, background_tasks: BackgroundTasks):
    # Fetch session from Supabase
    result = supabase.table("sessions").select("*").eq("session_id", str(session_id)).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Session not found")

    session = result.data[0]
    patient_id = session["patient_id"]

    # Fetch patient data
    patient_result = supabase.table("patients").select("*").eq("patient_id", patient_id).execute()
    patient_data = patient_result.data[0] if patient_result.data else {}

    # Fetch previous sessions for context
    prev_sessions = (
        supabase.table("sessions")
        .select("*")
        .eq("patient_id", patient_id)
        .order("session_date", desc=True)
        .limit(5)
        .execute()
    )

    def run_analysis():
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # CALL MINDMATE API
        analysis = loop.run_until_complete(
            analyze_session_with_mindmate(
                session_id=session_id,
                patient_id=patient_id,
                transcript=session.get("transcript", ""),
                patient_data=patient_data,
                previous_sessions=prev_sessions.data
            )
        )

        # Store results in Supabase
        supabase.table("sessions").update({
            "ai_extracted_data": analysis,
            "cognitive_test_scores": analysis["cognitive_test_scores"],
            "overall_score": analysis["overall_score"],
            "notable_events": analysis["notable_events"]
        }).eq("session_id", str(session_id)).execute()

        # Store extracted memories in ChromaDB/vector store
        for memory in analysis["memories"]:
            # Your existing vector storage logic
            pass

    background_tasks.add_task(run_analysis)

    return {"status": "Analysis started", "session_id": str(session_id)}
"""


"""
EXAMPLE 2: Add new dashboard endpoint

@router.get("/patients/{patient_id}/dashboard")
async def get_patient_dashboard(patient_id: UUID):
    # Fetch patient
    patient_result = supabase.table("patients").select("*").eq("patient_id", str(patient_id)).execute()
    if not patient_result.data:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient = patient_result.data[0]

    # Fetch all sessions
    sessions_result = (
        supabase.table("sessions")
        .select("*")
        .eq("patient_id", str(patient_id))
        .order("session_date", desc=True)
        .limit(30)
        .execute()
    )

    # Get MRI path if available
    mri_path = f"data/mri_outputs/report_{patient_id}.csv"

    # CALL MINDMATE API
    dashboard_data = await get_patient_dashboard_data(
        patient_id=patient_id,
        patient_name=patient["name"],
        sessions=sessions_result.data,
        mri_csv_path=mri_path if os.path.exists(mri_path) else None
    )

    return dashboard_data  # Ready for frontend!
"""


# =============================================================================
# Helper Functions
# =============================================================================

def calculate_age(dob: str) -> int:
    """Calculate age from date of birth"""
    from datetime import datetime
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


# =============================================================================
# Testing
# =============================================================================

async def test_integration():
    """Test the integration"""
    from uuid import uuid4

    print("Testing MindMate API integration...")

    # Test 1: Health check
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{MINDMATE_API_URL}/health")
        print(f"✅ Health check: {response.json()}")

    # Test 2: Mock session analysis
    mock_session_id = uuid4()
    mock_patient_id = uuid4()

    try:
        analysis = await analyze_session_with_mindmate(
            session_id=mock_session_id,
            patient_id=mock_patient_id,
            transcript="Patient discussed their family and hobbies.",
            patient_data={"name": "Test Patient", "dob": "1955-06-15"},
            previous_sessions=[]
        )
        print(f"✅ Session analysis: Score {analysis['overall_score']:.1%}")
    except Exception as e:
        print(f"❌ Session analysis failed: {e}")

    print("\nIntegration test complete!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_integration())
