# MindMate Cognitive Analysis API - Deployment Guide

## Overview

This service provides AI-powered cognitive analysis using Dedalus agents. It's designed to be called by your main backend after video call sessions.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Your Main Backend (Supabase)                  │
│  - Video calls (LiveKit)                                         │
│  - Session storage                                               │
│  - ChromaDB conversations                                        │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      │ HTTP POST
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│        MindMate Cognitive Analysis API (This Service)            │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Session Analyzer (Dedalus)                                 │ │
│  │  - Memory extraction                                       │ │
│  │  - Cognitive assessments                                   │ │
│  │  - 5 memory metrics                                        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ MRI Brain Mapper                                           │ │
│  │  - 6 brain regions from CSV                                │ │
│  │  - Atrophy detection                                       │ │
│  │  - Progression tracking                                    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Patient Cache (In-Memory)                                  │ │
│  │  - 24-hour TTL                                             │ │
│  │  - Dashboard data                                          │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                      │
                      │ Returns analysis
                      │
                      ▼
         Your Backend stores results in Supabase
                      │
                      ▼
                   Frontend
```

## API Endpoints

### 1. Analyze Session (Main Endpoint)
**POST /analyze/session**

Called after each video call to analyze the conversation.

```json
{
  "session_id": "uuid",
  "patient_id": "uuid",
  "transcript": "full conversation text...",
  "exercise_type": "memory_recall",
  "session_date": "2025-11-08T10:00:00",
  "patient_profile": {
    "name": "Margaret",
    "age": 68,
    "expected_info": {
      "family_members": ["Lucas"],
      "profession": "teacher"
    }
  },
  "previous_sessions": []
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "uuid",
    "patient_id": "uuid",
    "overall_score": 0.65,
    "memories": [
      {
        "title": "Visit to Boston",
        "description": "Patient recalled visiting grandson",
        "emotional_tone": "happy"
      }
    ],
    "cognitive_test_scores": [
      {"test": "temporal_orientation", "score": 7, "max_score": 10},
      {"test": "personal_recall", "score": 6, "max_score": 10}
    ],
    "memory_metrics": {
      "shortTermRecall": 0.65,
      "longTermRecall": 0.58,
      "semanticMemory": 0.72,
      "episodicMemory": 0.55,
      "workingMemory": 0.68
    },
    "doctor_alerts": [
      {
        "type": "moderate_decline",
        "severity": "high",
        "message": "Moderate cognitive decline (score: 65%)"
      }
    ],
    "requires_doctor_review": true
  }
}
```

### 2. Patient Dashboard
**POST /patient/dashboard**

Generate complete dashboard data for frontend.

```json
{
  "patient_id": "uuid",
  "patient_name": "Margaret Smith",
  "sessions": [...historical sessions...],
  "mri_csv_path": "/path/to/mri.csv",
  "days_back": 30
}
```

**Response:** Returns data in PatientData format for frontend

### 3. MRI Analysis
**POST /mri/analyze**

Analyze MRI volumetric data.

```json
{
  "patient_id": "uuid",
  "mri_csv_path": "/path/to/current_mri.csv",
  "baseline_mri_path": "/path/to/baseline_mri.csv"
}
```

## Deployment to Render

### Step 1: Prepare Repository

1. Ensure all files are committed:
```bash
git add .
git commit -m "Add cognitive analysis API"
git push origin main
```

### Step 2: Create Render Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will detect `render.yaml` automatically
5. Click **"Apply"**

### Step 3: Set Environment Variables

In Render dashboard, add these environment variables:

```
DEDALUS_API_KEY=dsk_live_xxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxx
PORT=8000
BACKEND_API_URL=https://your-main-backend.com (optional)
```

### Step 4: Deploy

Render will automatically:
- Install dependencies from `requirements.txt`
- Start the server with `python api_server.py`
- Set up health checks at `/health`

Your API will be available at: `https://mindmate-cognitive-api.onrender.com`

## Integration with Your Backend

### After Video Call Ends:

1. Your backend transcribes the conversation
2. Create session in Supabase
3. **Call this API:**

```python
import httpx

async def process_session_with_ai(session_id, patient_id, transcript):
    """Call MindMate API for cognitive analysis"""

    api_url = "https://mindmate-cognitive-api.onrender.com"

    payload = {
        "session_id": str(session_id),
        "patient_id": str(patient_id),
        "transcript": transcript,
        "patient_profile": {
            "name": patient.name,
            "age": patient.age,
            "expected_info": {...}
        },
        "previous_sessions": get_recent_sessions(patient_id, limit=5)
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{api_url}/analyze/session",
            json=payload,
            timeout=60.0
        )

        analysis = response.json()["data"]

        # Store results back in Supabase
        supabase.table("sessions").update({
            "ai_extracted_data": analysis,
            "cognitive_test_scores": analysis["cognitive_test_scores"],
            "overall_score": analysis["overall_score"],
            "memory_metrics": analysis["memory_metrics"]
        }).eq("session_id", session_id).execute()

        return analysis
```

### Frontend Dashboard Request:

```python
async def get_patient_dashboard(patient_id):
    """Get dashboard data for frontend"""

    # Fetch sessions from Supabase
    sessions = supabase.table("sessions")\
        .select("*")\
        .eq("patient_id", patient_id)\
        .order("session_date", desc=True)\
        .limit(30)\
        .execute()

    # Call MindMate API
    api_url = "https://mindmate-cognitive-api.onrender.com"

    payload = {
        "patient_id": str(patient_id),
        "patient_name": patient.name,
        "sessions": sessions.data,
        "mri_csv_path": f"/data/mri/{patient_id}.csv",
        "days_back": 30
    }

    response = await client.post(
        f"{api_url}/patient/dashboard",
        json=payload
    )

    return response.json()["data"]  # Ready for frontend
```

## Local Testing

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
export DEDALUS_API_KEY=dsk_live_xxxxx
export ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### 3. Run Server
```bash
python api_server.py
```

Server runs at `http://localhost:8000`

### 4. Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Test analysis (requires API keys)
curl -X POST http://localhost:8000/analyze/session \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

### 5. Run Integration Test
```bash
python test_api_integration.py
```

## Data Format Reference

### Brain Region Scores
```typescript
interface BrainRegionScores {
  hippocampus: number;        // 0.0 - 1.0
  prefrontalCortex: number;
  temporalLobe: number;
  parietalLobe: number;
  amygdala: number;
  cerebellum: number;
}
```

### Memory Metrics
```typescript
interface MemoryMetrics {
  shortTermRecall: TimeSeriesDataPoint[];
  longTermRecall: TimeSeriesDataPoint[];
  semanticMemory: TimeSeriesDataPoint[];
  episodicMemory: TimeSeriesDataPoint[];
  workingMemory: TimeSeriesDataPoint[];
}
```

### Recent Sessions
```typescript
interface RecentSession {
  date: string;             // ISO 8601
  score: number;            // 0.0 - 1.0
  exerciseType: string;     // "memory_recall", etc.
  notableEvents: string[];  // ["Memory difficulty detected"]
}
```

## Monitoring

### Health Check
```bash
curl https://mindmate-cognitive-api.onrender.com/health
```

### Cache Stats
```bash
curl https://mindmate-cognitive-api.onrender.com/cache/stats
```

### Logs
View logs in Render dashboard under "Logs" tab

## Troubleshooting

### Issue: Analysis timing out
- Increase timeout in your backend to 60-120 seconds
- Dedalus AI calls can take 20-40 seconds

### Issue: Cache not updating
- Call `POST /cache/invalidate/{patient_id}` after new MRI
- Cache TTL is 24 hours by default

### Issue: Missing brain regions
- Ensure MRI CSV has required columns
- Mapper will estimate missing regions from available data

### Issue: Low memory scores
- Check that previous_sessions are provided for long-term recall
- Ensure transcript has meaningful content (>50 words)

## Cost Estimation

### Render (Starter Plan - Free)
- 750 hours/month free
- Sleeps after 15 min inactivity
- Good for MVP/development

### Render (Standard Plan - $7/month)
- Always on
- Better for production
- No sleep

### API Costs
- Dedalus API: ~$0.01-0.05 per session
- Anthropic Claude: ~$0.02-0.10 per session

**Estimated:** ~$20-50/month for 500 sessions

## Next Steps

1. ✅ Deploy to Render
2. ✅ Test health endpoint
3. ✅ Update your backend to call this API
4. ✅ Test with real video call session
5. ✅ Monitor logs and performance
6. ✅ Upgrade Render plan if needed

## Support

For issues, check:
- Render logs: Dashboard → Logs
- API health: `/health` endpoint
- Test locally first with `python test_api_integration.py`
