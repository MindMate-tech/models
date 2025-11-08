# MindMate Full System Integration Guide

## 🗺️ Your Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────┐    ┌──────────────────────────┐  │
│  │  Doctor Dashboard        │    │  Patient Companion       │  │
│  │  (doctor-frontend)       │    │  (stellar-mind-companion)│  │
│  │  React/TypeScript        │    │  React/LiveKit           │  │
│  │  Vercel/Netlify          │    │  Vercel/Netlify          │  │
│  └────────────┬─────────────┘    └────────────┬─────────────┘  │
│               │                                │                 │
│               └────────────┬───────────────────┘                 │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │ HTTPS API Calls
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND LAYER                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Main Backend API (backend repo)                           │ │
│  │  - FastAPI + Supabase                                      │ │
│  │  - Session management                                      │ │
│  │  - Patient records                                         │ │
│  │  - ChromaDB for vectors                                    │ │
│  │  WHERE: Railway? Render? (You need to deploy this)        │ │
│  └─────────────────────────┬──────────────────────────────────┘ │
│                             │                                     │
│                             │ Calls for AI analysis               │
│                             ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Cognitive Analysis Microservice (models repo)             │ │
│  │  - Dedalus AI agents                                       │ │
│  │  - Memory metrics engine                                   │ │
│  │  - MRI brain mapping                                       │ │
│  │  WHERE: Render (needs deployment)                          │ │
│  │  URL: https://mindmate-cognitive-api.onrender.com          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Supabase    │  │  ChromaDB    │  │  MRI Files          │  │
│  │  (Postgres)  │  │  (Vectors)   │  │  (CSV Storage)      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📍 Current Deployment Status

| Repository | Status | Where It Should Be Deployed |
|------------|--------|----------------------------|
| **models** (cognitive API) | ✅ Code on GitHub<br>❌ NOT deployed | **Render** → You need to do this! |
| **backend** (main API) | ✅ Code on GitHub<br>❓ Unknown if deployed | Railway? Render? Fly.io? |
| **doctor-frontend** | ✅ Code on GitHub<br>❓ Unknown if deployed | Vercel or Netlify |
| **stellar-mind-companion** | ✅ Code on GitHub<br>❓ Unknown if deployed | Vercel or Netlify |

---

## 🔗 How Data Flows (Complete User Journey)

### **1. Patient Has Video Call**
```
stellar-mind-companion (LiveKit)
  → Records conversation
  → Generates transcript
  → POST /sessions (creates session in Supabase)
```

### **2. Backend Triggers AI Analysis**
```
backend/routes/sessions.py
  → POST /sessions/analyze/{session_id}
  → Calls: https://mindmate-cognitive-api.onrender.com/analyze/session
  → Gets: memories, cognitive scores, memory metrics
  → Stores in Supabase
```

### **3. Doctor Views Dashboard**
```
doctor-frontend
  → GET /patients/{id}/dashboard
  → Backend calls: https://mindmate-cognitive-api.onrender.com/patient/dashboard
  → Returns: brain regions, memory metrics, sessions (PatientData format)
  → Frontend displays charts and data
```

---

## 🚀 Deployment Steps - Do This Now

### **Step 1: Deploy Cognitive Analysis API (models repo) to Render**

**You are here →** This is the most important step!

1. Go to https://dashboard.render.com
2. Click "New +" → "Blueprint"
3. Connect: `MindMate-tech/models`
4. Add environment variables:
   ```
   DEDALUS_API_KEY=dsk_live_e6adeae3ea9a_4aaaa9f9bca6165a640b92e6af9b2026
   ANTHROPIC_API_KEY=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
   ```
5. Click "Apply"
6. Wait 5-10 minutes
7. Copy your URL: `https://mindmate-cognitive-api-xxxxx.onrender.com`

### **Step 2: Update Backend to Call Cognitive API**

In your `backend` repo, add this integration:

**File: `NewMindmate/services/cognitive_api_client.py` (NEW FILE)**
```python
import httpx
from uuid import UUID
from typing import Dict, List

# Your Render URL from Step 1
COGNITIVE_API_URL = "https://mindmate-cognitive-api.onrender.com"

async def analyze_session_with_ai(
    session_id: UUID,
    patient_id: UUID,
    transcript: str,
    patient_data: Dict,
    previous_sessions: List[Dict] = None
) -> Dict:
    """
    Call MindMate Cognitive API to analyze session
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
            "expected_info": {}
        },
        "previous_sessions": previous_sessions or []
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{COGNITIVE_API_URL}/analyze/session",
            json=payload
        )

        if response.status_code != 200:
            raise Exception(f"Cognitive API error: {response.text}")

        return response.json()["data"]


async def get_patient_dashboard(
    patient_id: UUID,
    patient_name: str,
    sessions: List[Dict]
) -> Dict:
    """
    Get complete dashboard data for frontend
    """

    payload = {
        "patient_id": str(patient_id),
        "patient_name": patient_name,
        "sessions": sessions,
        "days_back": 30
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{COGNITIVE_API_URL}/patient/dashboard",
            json=payload
        )

        return response.json()["data"]


def calculate_age(dob: str) -> int:
    from datetime import datetime
    if not dob:
        return 0
    birth_date = datetime.fromisoformat(dob.replace('Z', ''))
    today = datetime.utcnow()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )
```

**Update: `NewMindmate/routes/sessions.py`**
```python
from services.cognitive_api_client import analyze_session_with_ai, get_patient_dashboard

@router.post("/analyze/{session_id}")
async def analyze_session(session_id: UUID, background_tasks: BackgroundTasks):
    """Trigger AI analysis using Cognitive API"""

    # Fetch session
    result = supabase.table("sessions").select("*").eq("session_id", str(session_id)).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Session not found")

    session = result.data[0]
    patient_id = session["patient_id"]

    # Fetch patient
    patient_result = supabase.table("patients").select("*").eq("patient_id", patient_id).execute()
    patient_data = patient_result.data[0] if patient_result.data else {}

    # Fetch previous sessions
    prev_sessions = (
        supabase.table("sessions")
        .select("*")
        .eq("patient_id", patient_id)
        .order("session_date", desc=True)
        .limit(5)
        .execute()
    )

    async def run_analysis():
        # CALL COGNITIVE API
        analysis = await analyze_session_with_ai(
            session_id=session_id,
            patient_id=patient_id,
            transcript=session.get("transcript", ""),
            patient_data=patient_data,
            previous_sessions=prev_sessions.data
        )

        # Store results
        supabase.table("sessions").update({
            "ai_extracted_data": analysis,
            "cognitive_test_scores": analysis["cognitive_test_scores"],
            "overall_score": analysis["overall_score"],
            "memory_metrics": analysis["memory_metrics"]
        }).eq("session_id", str(session_id)).execute()

        # Store memories in ChromaDB
        for memory in analysis["memories"]:
            store_memory_embedding(
                supabase,
                patient_id=patient_id,
                title=memory["title"],
                description=memory["description"],
                embedding=memory.get("embedding")
            )

    background_tasks.add_task(run_analysis)
    return {"status": "Analysis started", "session_id": str(session_id)}


@router.get("/patient/{patient_id}/dashboard")
async def get_dashboard(patient_id: UUID):
    """Get patient dashboard data for frontend"""

    # Fetch patient
    patient_result = supabase.table("patients").select("*").eq("patient_id", str(patient_id)).execute()
    if not patient_result.data:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient = patient_result.data[0]

    # Fetch sessions
    sessions_result = (
        supabase.table("sessions")
        .select("*")
        .eq("patient_id", str(patient_id))
        .order("session_date", desc=True)
        .limit(30)
        .execute()
    )

    # Call Cognitive API for dashboard data
    dashboard = await get_patient_dashboard(
        patient_id=patient_id,
        patient_name=patient["name"],
        sessions=sessions_result.data
    )

    return dashboard  # Ready for frontend!
```

### **Step 3: Deploy Your Backend**

Your backend needs to be deployed somewhere. Options:

**Render (Recommended):**
1. Create `render.yaml` in backend repo
2. Similar to what we did for models
3. Deploy to Render

**Railway:**
```bash
cd /home/lucas/mindmate-backend/NewMindmate
railway init
railway up
```

**Fly.io:**
```bash
cd /home/lucas/mindmate-backend/NewMindmate
fly launch
fly deploy
```

### **Step 4: Deploy Frontends**

**Doctor Dashboard:**
```bash
# If using Vercel
cd doctor-frontend
vercel deploy
```

**Patient Companion:**
```bash
# If using Vercel
cd stellar-mind-companion
vercel deploy
```

### **Step 5: Configure Environment Variables**

**Backend needs:**
```
SUPABASE_URL=...
SUPABASE_KEY=...
COGNITIVE_API_URL=https://mindmate-cognitive-api.onrender.com
```

**Frontends need:**
```
BACKEND_API_URL=https://your-backend-url.com
LIVEKIT_URL=...
```

---

## ✅ Testing The Complete Flow

### **1. Test Cognitive API (models)**
```bash
curl https://mindmate-cognitive-api.onrender.com/health
```

### **2. Test Backend**
```bash
curl https://your-backend-url.com/health
```

### **3. Test Integration**
```bash
# Create session in backend
curl -X POST https://your-backend-url.com/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "...",
    "transcript": "Test conversation"
  }'

# Trigger analysis (should call cognitive API)
curl -X POST https://your-backend-url.com/sessions/analyze/{session_id}

# Get dashboard (should use cognitive API)
curl https://your-backend-url.com/sessions/patient/{patient_id}/dashboard
```

---

## 🎯 Summary - What You Need To Do RIGHT NOW

1. ✅ **Deploy models repo to Render** (5 minutes)
   - Go to Render dashboard
   - Connect GitHub
   - Add API keys
   - Deploy

2. 📝 **Update backend code** (10 minutes)
   - Add `cognitive_api_client.py`
   - Update `sessions.py`
   - Commit and push

3. 🚀 **Deploy backend** (Choose one: Render/Railway/Fly.io) (10 minutes)

4. 🌐 **Deploy frontends** (If not already deployed) (5 minutes each)

5. ✅ **Test end-to-end** (5 minutes)

**Total time: ~45 minutes to have everything working together!**

---

## 🆘 Need Help?

Let me know which step you're on and I can help you through it!
