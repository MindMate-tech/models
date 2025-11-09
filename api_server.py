"""
MindMate Cognitive Analysis API
Microservice for AI-powered cognitive analysis using Dedalus
"""
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.session_analyzer import SessionAnalyzer
from services.patient_cache import get_cache
from tools.brain_region_mapper import BrainRegionMapper, analyze_mri_file
from tools.memory_metrics_engine import MemoryMetricsEngine
from config.settings import settings
from agents.doctor.doctor_query_agent import DoctorQueryAgent

# ==================== FastAPI App ====================

app = FastAPI(
    title="MindMate Cognitive Analysis API",
    description="AI-powered cognitive analysis microservice",
    version="1.0.0"
)

# CORS for integration with main backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
session_analyzer = SessionAnalyzer()
cache = get_cache()
brain_mapper = BrainRegionMapper()
memory_engine = MemoryMetricsEngine()
doctor_agent = DoctorQueryAgent()


# ==================== Request Models ====================

class AnalyzeSessionRequest(BaseModel):
    """Request to analyze a session"""
    session_id: UUID
    patient_id: UUID
    transcript: str
    exercise_type: Optional[str] = "memory_recall"
    session_date: Optional[str] = None
    patient_profile: Dict = Field(
        default_factory=dict,
        description="Patient info (name, age, expected_info, etc.)"
    )
    previous_sessions: Optional[List[Dict]] = Field(
        default_factory=list,
        description="Historical sessions for context"
    )


class PatientDashboardRequest(BaseModel):
    """Request for patient dashboard data"""
    patient_id: UUID
    patient_name: str
    sessions: List[Dict] = Field(
        description="Historical sessions with analysis"
    )
    mri_csv_path: Optional[str] = None
    days_back: int = 30


class MRIAnalysisRequest(BaseModel):
    """Request to analyze MRI data"""
    patient_id: UUID
    mri_csv_path: str
    baseline_mri_path: Optional[str] = None


class DoctorQueryRequest(BaseModel):
    """Request for doctor to query patient data in natural language"""
    query: str = Field(
        description="Natural language query from doctor"
    )
    context: Optional[Dict] = Field(
        default_factory=dict,
        description="Optional context (patient_id, doctor_id, etc.)"
    )


# ==================== Health & Info ====================

@app.get("/")
async def root():
    """API info"""
    return {
        "service": "MindMate Cognitive Analysis API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "analyze_session": "POST /analyze/session",
            "patient_dashboard": "POST /patient/dashboard",
            "mri_analysis": "POST /mri/analyze",
            "doctor_query": "POST /doctor/query - AI-powered natural language queries",
            "at_risk_patients": "GET /doctor/at-risk",
            "patient_lookup": "GET /doctor/patient/{patient_id}",
            "cache_stats": "GET /cache/stats"
        },
        "new_features": {
            "doctor_ai_agent": "Ask questions in natural language, AI uses tools to answer",
            "example_queries": [
                "Show me all at-risk patients",
                "Why is patient declining?",
                "Compare two patients",
                "Find patients that need attention"
            ]
        }
    }


@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "dedalus": bool(settings.dedalus_api_key),
            "anthropic": bool(settings.anthropic_api_key),
            "cache": cache.get_stats()
        }
    }


# ==================== Main Analysis Endpoint ====================

@app.post("/analyze/session")
async def analyze_session(request: AnalyzeSessionRequest):
    """
    Analyze a patient session with AI-powered cognitive assessment

    Called by main backend after video call session.

    Returns:
    - Extracted memories
    - Cognitive test scores
    - Memory metrics (5 types)
    - Overall score
    - Doctor alerts
    """
    try:
        print(f"\n{'='*60}")
        print(f"🔍 Received session analysis request")
        print(f"Patient: {request.patient_id}")
        print(f"Session: {request.session_id}")
        print(f"{'='*60}")

        # Prepare session data
        session_data = {
            'session_id': str(request.session_id),
            'patient_id': str(request.patient_id),
            'transcript': request.transcript,
            'exercise_type': request.exercise_type,
            'session_date': request.session_date or datetime.utcnow().isoformat()
        }

        # Run analysis
        analysis_result = await session_analyzer.analyze_session(
            session_data=session_data,
            patient_profile=request.patient_profile,
            previous_sessions=request.previous_sessions
        )

        # Update cache with new session
        patient_id_str = str(request.patient_id)
        cache.update_session_data(
            patient_id=patient_id_str,
            new_session=session_data,
            new_analysis=analysis_result
        )

        return {
            "success": True,
            "data": analysis_result,
            "message": "Session analyzed successfully"
        }

    except Exception as e:
        print(f"❌ Analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


# ==================== Patient Dashboard Endpoint ====================

@app.post("/patient/dashboard")
async def get_patient_dashboard(request: PatientDashboardRequest):
    """
    Generate complete patient dashboard data for frontend

    Returns data in PatientData format:
    - Brain region scores (from MRI)
    - Memory metrics time series
    - Recent sessions
    - Overall cognitive score
    - Memory retention rate
    """
    try:
        patient_id_str = str(request.patient_id)

        # Check cache first
        cached_data = cache.get(patient_id_str)
        if cached_data:
            print(f"✅ Cache hit for patient {patient_id_str}")
            return {
                "success": True,
                "data": cached_data,
                "cached": True
            }

        print(f"📊 Building dashboard for patient {patient_id_str}")

        # 1. Brain regions from MRI
        brain_regions = {'hippocampus': 0.75, 'prefrontalCortex': 0.75, 'temporalLobe': 0.75,
                        'parietalLobe': 0.75, 'amygdala': 0.75, 'cerebellum': 0.75}

        if request.mri_csv_path and os.path.exists(request.mri_csv_path):
            mri_analysis = analyze_mri_file(request.mri_csv_path)
            brain_regions = mri_analysis['brain_regions']

        # 2. Memory metrics time series
        memory_metrics = memory_engine.generate_time_series(
            sessions=request.sessions,
            days_back=request.days_back
        )

        # 3. Recent sessions summary
        recent_sessions = []
        for session in request.sessions[:10]:  # Last 10
            analysis = session.get('ai_extracted_data', {})
            recent_sessions.append({
                'date': session.get('session_date', datetime.utcnow().isoformat()),
                'score': analysis.get('overall_score', session.get('overall_score', 0.5)),
                'exerciseType': session.get('exercise_type', 'memory_recall'),
                'notableEvents': analysis.get('notable_events', [])
            })

        # 4. Overall cognitive score (from recent sessions)
        if recent_sessions:
            overall_score = sum(s['score'] for s in recent_sessions) / len(recent_sessions)
        else:
            overall_score = 0.5

        # 5. Memory retention rate
        memory_retention_rate = memory_engine.calculate_memory_retention_rate(
            sessions=request.sessions,
            days_back=7
        )

        # Build final dashboard data
        dashboard_data = {
            'patientId': patient_id_str,
            'patientName': request.patient_name,
            'lastUpdated': datetime.utcnow().isoformat(),
            'brainRegions': brain_regions,
            'memoryMetrics': memory_metrics,
            'recentSessions': recent_sessions,
            'overallCognitiveScore': round(overall_score, 3),
            'memoryRetentionRate': round(memory_retention_rate, 3)
        }

        # Cache the result
        cache.set(patient_id_str, dashboard_data, ttl_hours=24)

        return {
            "success": True,
            "data": dashboard_data,
            "cached": False
        }

    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Dashboard generation failed: {str(e)}"
        )


# ==================== MRI Analysis Endpoint ====================

@app.post("/mri/analyze")
async def analyze_mri(request: MRIAnalysisRequest):
    """
    Analyze MRI volumetric data and map to brain regions

    Optionally compare with baseline to detect progression
    """
    try:
        patient_id_str = str(request.patient_id)

        if not os.path.exists(request.mri_csv_path):
            raise HTTPException(
                status_code=404,
                detail=f"MRI file not found: {request.mri_csv_path}"
            )

        # Parse and analyze current MRI
        print(f"🧠 Analyzing MRI for patient {patient_id_str}")
        current_analysis = analyze_mri_file(request.mri_csv_path)

        result = {
            'patient_id': patient_id_str,
            'analyzed_at': datetime.utcnow().isoformat(),
            'brain_regions': current_analysis['brain_regions'],
            'alerts': current_analysis['alerts'],
            'requires_doctor_review': len(current_analysis['alerts']) > 0
        }

        # Compare with baseline if provided
        if request.baseline_mri_path and os.path.exists(request.baseline_mri_path):
            print("📈 Comparing with baseline MRI...")
            baseline_analysis = analyze_mri_file(request.baseline_mri_path)

            comparison = brain_mapper.compare_mri_scans(
                baseline_regions=baseline_analysis['brain_regions'],
                current_regions=current_analysis['brain_regions']
            )

            result['comparison'] = comparison
            result['requires_doctor_review'] = comparison['requires_doctor_review']

        # Invalidate cache to force refresh with new MRI data
        cache.invalidate(patient_id_str)

        return {
            "success": True,
            "data": result
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ MRI analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"MRI analysis failed: {str(e)}"
        )


# ==================== Doctor Query Endpoint (AI-Powered) ====================

@app.post("/doctor/query")
async def doctor_query(request: DoctorQueryRequest):
    """
    AI-powered natural language query interface for doctors

    Allows doctors to ask questions about patients in natural language.
    The AI agent will use appropriate tools to answer the query.

    Example queries:
    - "Show me all at-risk patients"
    - "Why is patient X declining?"
    - "Compare patients A and B"
    - "Find female patients over 60"

    Returns intelligent analysis with reasoning and recommendations.
    """
    try:
        print(f"\n{'='*60}")
        print(f"🩺 Doctor Query: {request.query}")
        print(f"{'='*60}")

        result = await doctor_agent.query(
            doctor_query=request.query,
            context=request.context
        )

        return {
            "success": result.get("success", True),
            "query": request.query,
            "response": result.get("response", ""),
            "tools_used": result.get("tools_used", []),
            "model_info": result.get("model_info", {}),
            "raw_data": result.get("raw_data")
        }

    except Exception as e:
        print(f"❌ Doctor query error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Query failed: {str(e)}"
        )


@app.get("/doctor/at-risk")
async def get_at_risk_patients_quick(threshold: float = 0.5):
    """
    Quick endpoint to get at-risk patients (no AI, faster)

    Args:
        threshold: Score threshold (0-1). Patients below this are at risk.

    Returns:
        List of at-risk patients with detailed risk reasoning
    """
    try:
        result = await doctor_agent.find_at_risk(threshold=threshold)

        return {
            "success": True,
            "count": result.get("count", 0),
            "threshold": threshold,
            "patients": result.get("data", [])
        }

    except Exception as e:
        print(f"❌ At-risk query error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"At-risk query failed: {str(e)}"
        )


@app.get("/doctor/patient/{patient_id}")
async def get_patient_quick(patient_id: UUID):
    """
    Quick endpoint to get patient details (no AI, faster)

    Args:
        patient_id: Patient UUID

    Returns:
        Patient details with session history
    """
    try:
        result = await doctor_agent.quick_lookup(str(patient_id))

        if not result.get("success"):
            raise HTTPException(
                status_code=404,
                detail=result.get("error", "Patient not found")
            )

        return {
            "success": True,
            "patient": result.get("data", {})
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Patient lookup error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Patient lookup failed: {str(e)}"
        )


@app.get("/doctor/database-stats")
async def get_database_stats():
    """
    Diagnostic endpoint to check database contents
    Shows counts and sample data without exposing sensitive info
    """
    try:
        from db.supabase_client import get_supabase
        supabase = get_supabase()

        # Count patients
        patients_result = supabase.table("patients").select("*", count="exact").limit(3).execute()
        patient_count = len(patients_result.data)

        # Count sessions
        sessions_result = supabase.table("sessions").select("*", count="exact").limit(3).execute()
        session_count = len(sessions_result.data)

        # Get sample scores
        sample_scores = []
        if sessions_result.data:
            for session in sessions_result.data[:3]:
                sample_scores.append(session.get('overall_score', 'None'))

        return {
            "success": True,
            "database": {
                "total_patients": patient_count,
                "total_sessions": session_count,
                "sample_scores": sample_scores,
                "patients_table_columns": list(patients_result.data[0].keys()) if patients_result.data else [],
                "sessions_table_columns": list(sessions_result.data[0].keys()) if sessions_result.data else []
            }
        }

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Database stats error: {e}")
        print(error_trace)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": error_trace
        }


# ==================== Cache Management ====================

@app.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    return cache.get_stats()


@app.post("/cache/invalidate/{patient_id}")
async def invalidate_cache(patient_id: UUID):
    """Invalidate cache for specific patient"""
    removed = cache.invalidate(str(patient_id))
    return {
        "success": True,
        "patient_id": str(patient_id),
        "was_cached": removed
    }


@app.post("/cache/clear")
async def clear_cache():
    """Clear entire cache"""
    count = cache.clear_all()
    return {
        "success": True,
        "entries_cleared": count
    }


@app.post("/cache/cleanup")
async def cleanup_expired():
    """Remove expired cache entries"""
    count = cache.cleanup_expired()
    return {
        "success": True,
        "entries_removed": count
    }


# ==================== Background Tasks ====================

async def periodic_cache_cleanup():
    """Background task to cleanup expired cache entries"""
    import asyncio
    while True:
        await asyncio.sleep(3600)  # Every hour
        removed = cache.cleanup_expired()
        if removed > 0:
            print(f"🧹 Cleaned up {removed} expired cache entries")


@app.on_event("startup")
async def startup_event():
    """Run on server startup"""
    print("\n" + "="*60)
    print("🧠 MindMate Cognitive Analysis API")
    print("="*60)
    print(f"Environment: {settings.run_mode.value}")
    print(f"Model: {settings.default_model}")
    print(f"Dedalus API: {'✓' if settings.dedalus_api_key else '✗'}")
    print(f"Anthropic API: {'✓' if settings.anthropic_api_key else '✗'}")
    print("="*60 + "\n")

    # Start background cleanup task
    import asyncio
    asyncio.create_task(periodic_cache_cleanup())


# ==================== Run Server ====================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=False,  # Disable reload for production
        log_level="info"
    )
