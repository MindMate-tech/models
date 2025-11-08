"""
Updated Sessions Routes with Cognitive API Integration

INSTRUCTIONS:
1. Replace your existing NewMindmate/routes/sessions.py with this file
2. Make sure cognitive_api_client.py is in NewMindmate/services/
3. Update COGNITIVE_API_URL in cognitive_api_client.py with your Render URL
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from uuid import UUID
from datetime import datetime
from typing import List

from schemas import SessionCreate, SessionResponse
from db.supabase_client import get_supabase
from db.vector_utils import store_memory_embedding
from services.cognitive_api_client import (
    analyze_session_with_ai,
    get_patient_dashboard,
    analyze_mri_scan
)

router = APIRouter(prefix="/sessions", tags=["sessions"])
supabase = get_supabase()


# ------------------------------
# Create a new session
# ------------------------------
@router.post("/", response_model=SessionResponse)
def create_session(session: SessionCreate):
    """Create a new session in Supabase"""

    session_date = session.session_date or datetime.utcnow()

    # Compute overall score if test scores provided
    overall_score = None
    if session.cognitive_test_scores:
        scores = [(t.score / t.max_score) * 100 for t in session.cognitive_test_scores]
        overall_score = sum(scores) / len(scores)

    session_data = session.dict()
    session_data.update({
        "session_date": session_date.isoformat(),
        "overall_score": overall_score,
        "created_at": datetime.utcnow().isoformat()
    })

    result = supabase.table("sessions").insert(session_data).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {result}")

    return SessionResponse(**result.data[0])


# ------------------------------
# Get sessions for a patient
# ------------------------------
@router.get("/patient/{patient_id}", response_model=List[SessionResponse])
def get_sessions(patient_id: UUID):
    """Get all sessions for a patient"""

    result = (
        supabase.table("sessions")
        .select("*")
        .eq("patient_id", str(patient_id))
        .order("session_date", desc=True)
        .execute()
    )

    if not result.data:
        return []

    return [SessionResponse(**row) for row in result.data]


# ------------------------------
# Analyze session with Cognitive API
# ------------------------------
@router.post("/analyze/{session_id}")
async def analyze_session(session_id: UUID, background_tasks: BackgroundTasks):
    """
    Trigger AI analysis using MindMate Cognitive API

    This endpoint:
    1. Fetches session and patient data from Supabase
    2. Calls Cognitive API for AI analysis
    3. Stores results back in Supabase
    4. Stores memories in ChromaDB
    """

    # Fetch session from Supabase
    result = supabase.table("sessions").select("*").eq("session_id", str(session_id)).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Session not found")

    session = result.data[0]
    patient_id = session["patient_id"]

    # Fetch patient data
    patient_result = supabase.table("patients").select("*").eq("patient_id", patient_id).execute()
    if not patient_result.data:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient_data = patient_result.data[0]

    # Fetch previous sessions for context
    prev_sessions = (
        supabase.table("sessions")
        .select("*")
        .eq("patient_id", patient_id)
        .order("session_date", desc=True)
        .limit(5)
        .execute()
    )

    async def run_analysis():
        """Background task to run AI analysis"""
        try:
            print(f"🧠 Starting AI analysis for session {session_id}")

            # CALL COGNITIVE API
            analysis = await analyze_session_with_ai(
                session_id=session_id,
                patient_id=UUID(patient_id),
                transcript=session.get("transcript", ""),
                patient_data=patient_data,
                previous_sessions=prev_sessions.data
            )

            print(f"✅ Analysis complete! Overall score: {analysis['overall_score']:.1%}")

            # Store results in Supabase
            supabase.table("sessions").update({
                "ai_extracted_data": analysis,
                "cognitive_test_scores": analysis["cognitive_test_scores"],
                "overall_score": analysis["overall_score"],
                "memory_metrics": analysis.get("memory_metrics"),
                "notable_events": analysis.get("notable_events", []),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("session_id", str(session_id)).execute()

            print(f"💾 Stored analysis in Supabase")

            # Store extracted memories in ChromaDB
            for memory in analysis.get("memories", []):
                try:
                    store_memory_embedding(
                        supabase,
                        patient_id=patient_id,
                        title=memory.get("title", "Memory"),
                        description=memory.get("description", ""),
                        embedding=memory.get("embedding"),
                        dateapprox=memory.get("dateapprox"),
                        location=memory.get("location"),
                        emotional_tone=memory.get("emotional_tone"),
                        tags=memory.get("tags", []),
                        significance_level=memory.get("significance_level", 1)
                    )
                    print(f"📝 Stored memory: {memory.get('title')}")
                except Exception as e:
                    print(f"⚠️  Failed to store memory: {e}")

            print(f"🎉 Analysis pipeline complete for session {session_id}")

        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            # Store error in session
            supabase.table("sessions").update({
                "ai_extracted_data": {"error": str(e)},
                "updated_at": datetime.utcnow().isoformat()
            }).eq("session_id", str(session_id)).execute()

    # Run analysis in background
    background_tasks.add_task(run_analysis)

    return {
        "status": "Analysis started in background",
        "session_id": str(session_id),
        "message": "Check back in 60-120 seconds for results"
    }


# ------------------------------
# Get patient dashboard
# ------------------------------
@router.get("/patient/{patient_id}/dashboard")
async def get_dashboard(patient_id: UUID):
    """
    Get comprehensive patient dashboard data for frontend

    Returns data formatted exactly as PatientData TypeScript interface:
    - Brain region scores (from MRI)
    - Memory metrics time series
    - Recent sessions
    - Overall cognitive score
    - Memory retention rate
    """

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

    # Check for MRI data
    mri_path = f"data/mri_outputs/report_{patient_id}.csv"

    try:
        # Call Cognitive API for dashboard data
        dashboard = await get_patient_dashboard(
            patient_id=patient_id,
            patient_name=patient["name"],
            sessions=sessions_result.data,
            mri_csv_path=mri_path
        )

        return dashboard  # Already in correct format for frontend!

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate dashboard: {str(e)}"
        )


# ------------------------------
# Analyze MRI scan
# ------------------------------
@router.post("/patient/{patient_id}/mri/analyze")
async def analyze_patient_mri(
    patient_id: UUID,
    current_mri_path: str,
    baseline_mri_path: str = None
):
    """
    Analyze MRI scan and get brain region scores

    Returns:
    - Brain region health scores (0-1)
    - Atrophy alerts
    - Progression analysis (if baseline provided)
    """

    try:
        analysis = await analyze_mri_scan(
            patient_id=patient_id,
            mri_csv_path=current_mri_path,
            baseline_mri_path=baseline_mri_path
        )

        # Optionally store in patient record
        supabase.table("patients").update({
            "latest_mri_analysis": analysis,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("patient_id", str(patient_id)).execute()

        return analysis

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze MRI: {str(e)}"
        )
