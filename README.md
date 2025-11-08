# MindMate Cognitive Analysis API

AI-powered cognitive analysis microservice for dementia patient monitoring. Integrates Dedalus agents with your existing backend to provide comprehensive cognitive assessments, memory metrics, and brain region analysis.

## 🎯 What This Service Does

- **Analyzes video call transcripts** using Dedalus AI to extract memories and assess cognitive function
- **Calculates 5 memory metrics**: Short-term recall, long-term recall, semantic, episodic, and working memory
- **Maps MRI scans** to 6 brain regions with health scores and atrophy detection
- **Generates doctor alerts** for cognitive decline and risk factors
- **Provides dashboard data** formatted exactly for your frontend

## 🏗️ Architecture

This is a **standalone microservice** that your existing backend calls via HTTP:

```
Your Backend (Supabase + LiveKit)
           ↓
    [HTTP POST /analyze/session]
           ↓
MindMate Cognitive API (This Service)
    - Dedalus AI analysis
    - Memory metrics calculation
    - MRI brain mapping
           ↓
    [Returns structured data]
           ↓
Your Backend (stores in Supabase)
           ↓
Frontend (receives PatientData format)
```

## 📦 What's Included

### Core Services
- **`api_server.py`** - FastAPI server with all endpoints
- **`services/session_analyzer.py`** - Dedalus-powered session analysis
- **`services/patient_cache.py`** - In-memory caching (24hr TTL)

### Analysis Tools
- **`tools/brain_region_mapper.py`** - MRI to 6 brain regions with rule-based estimates
- **`tools/memory_metrics_engine.py`** - 5 memory metrics from cognitive tests
- **`tools/cognitive_assessment.py`** - Existing cognitive tests (temporal, recall, speech)
- **`tools/mri_analysis.py`** - MRI CSV parsing

### Configuration
- **`requirements.txt`** - All Python dependencies
- **`render.yaml`** - Render deployment configuration
- **`.env`** - Environment variables (API keys)
- **`config/settings.py`** - Service settings

### Documentation
- **`DEPLOYMENT.md`** - Complete deployment guide
- **`INTEGRATION_EXAMPLE.py`** - Code examples for your backend
- **`test_api_integration.py`** - Integration tests

## 🚀 Quick Start

### 1. Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DEDALUS_API_KEY=dsk_live_xxxxx
export ANTHROPIC_API_KEY=sk-ant-xxxxx

# Run server
python api_server.py

# Test health check
curl http://localhost:8000/health
```

### 2. Deploy to Render

```bash
# Commit and push
git add .
git commit -m "Add cognitive analysis API"
git push origin main

# Go to Render Dashboard
# → New → Blueprint
# → Connect GitHub repo
# → Set environment variables
# → Deploy!
```

**Your API will be at:** `https://mindmate-cognitive-api.onrender.com`

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

### 3. Integrate with Your Backend

```python
import httpx

# After video call ends
async def process_session(session_id, patient_id, transcript):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://mindmate-cognitive-api.onrender.com/analyze/session",
            json={
                "session_id": str(session_id),
                "patient_id": str(patient_id),
                "transcript": transcript,
                "patient_profile": {...}
            },
            timeout=120.0
        )

        analysis = response.json()["data"]

        # Store in Supabase
        supabase.table("sessions").update({
            "ai_extracted_data": analysis,
            "overall_score": analysis["overall_score"]
        }).eq("session_id", session_id).execute()

        return analysis
```

See [INTEGRATION_EXAMPLE.py](INTEGRATION_EXAMPLE.py) for complete examples.

## 📊 API Endpoints

### Core Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/analyze/session` | POST | Analyze video call transcript |
| `/patient/dashboard` | POST | Generate frontend dashboard data |
| `/mri/analyze` | POST | Analyze MRI scan |
| `/health` | GET | Health check |

### Analysis Response Format

```json
{
  "overall_score": 0.65,
  "memory_metrics": {
    "shortTermRecall": 0.65,
    "longTermRecall": 0.58,
    "semanticMemory": 0.72,
    "episodicMemory": 0.55,
    "workingMemory": 0.68
  },
  "cognitive_test_scores": [...],
  "memories": [...],
  "doctor_alerts": [...]
}
```

### Dashboard Data Format

Matches your frontend TypeScript interfaces:

```typescript
interface PatientData {
  patientId: string;
  patientName: string;
  brainRegions: BrainRegionScores;  // 6 regions
  memoryMetrics: MemoryMetrics;      // 5 types with time series
  recentSessions: RecentSession[];
  overallCognitiveScore: number;
  memoryRetentionRate: number;
}
```

## 🧠 Brain Region Mapping

Converts MRI CSV data to 6 brain regions using rule-based logic:

| Region | Source |
|--------|--------|
| **Hippocampus** | Direct from CSV (avg L/R) |
| **Temporal Lobe** | Direct from CSV (avg L/R) |
| **Prefrontal Cortex** | Estimated from gray matter (25%) |
| **Parietal Lobe** | Estimated from gray matter (20%) |
| **Amygdala** | Estimated from hippocampus (3%) |
| **Cerebellum** | Estimated from brain volume (10%) |

Returns normalized health scores (0.0-1.0) with automatic atrophy detection.

## 📈 Memory Metrics

Transforms cognitive assessments into 5 time-series metrics:

1. **Short-term recall** - 0-5 minute memory (conversation coherence)
2. **Long-term recall** - Days to weeks (references to past sessions)
3. **Semantic memory** - General knowledge (vocabulary, facts)
4. **Episodic memory** - Personal events (memories with context)
5. **Working memory** - Task manipulation (conversation flow)

Each metric calculated as 0.0-1.0 score with historical tracking.

## 🔧 Configuration

### Environment Variables

```bash
# Required
DEDALUS_API_KEY=dsk_live_xxxxx          # Dedalus API key
ANTHROPIC_API_KEY=sk-ant-xxxxx          # Anthropic Claude key

# Optional
PORT=8000                                # Server port
BACKEND_API_URL=https://your-backend.com # Your main backend URL
```

### Settings (config/settings.py)

```python
class Settings:
    run_mode: RunMode = RunMode.PRODUCTION
    default_model: str = "anthropic/claude-sonnet-4-20250514"
    use_cache: bool = True
```

## 🧪 Testing

```bash
# Run integration tests
python test_api_integration.py

# Test specific components
python -c "from tools.brain_region_mapper import analyze_mri_file; \
           print(analyze_mri_file('data/mri_outputs/report_patient_001.csv'))"

# Test API endpoints
curl -X POST http://localhost:8000/analyze/session \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

## 📁 Project Structure

```
mindmate-demo/
├── api_server.py              # Main FastAPI application
├── services/
│   ├── session_analyzer.py    # Dedalus session analysis
│   └── patient_cache.py       # In-memory cache
├── tools/
│   ├── brain_region_mapper.py # MRI → 6 brain regions
│   ├── memory_metrics_engine.py # 5 memory metrics
│   ├── cognitive_assessment.py # Cognitive tests
│   └── mri_analysis.py        # MRI CSV parsing
├── config/
│   └── settings.py            # Configuration
├── agents/                    # Dedalus agent definitions
├── data/mri_outputs/          # MRI CSV files
├── requirements.txt           # Dependencies
├── render.yaml               # Render config
├── DEPLOYMENT.md             # Deployment guide
├── INTEGRATION_EXAMPLE.py    # Integration code
└── test_api_integration.py   # Tests
```

## 💰 Cost Estimation

| Service | Plan | Cost |
|---------|------|------|
| **Render** | Starter (Free) | $0 |
| **Render** | Standard | $7/month |
| **Dedalus API** | Per session | ~$0.01-0.05 |
| **Anthropic Claude** | Per session | ~$0.02-0.10 |

**Total for 500 sessions/month:** ~$20-50

Use Render free tier for development, upgrade to Standard for production.

## 🔍 Monitoring

```bash
# Health check
curl https://mindmate-cognitive-api.onrender.com/health

# Cache stats
curl https://mindmate-cognitive-api.onrender.com/cache/stats

# View logs
# Render Dashboard → Logs tab
```

## 🛠️ Troubleshooting

### Timeouts
- Increase timeout to 60-120 seconds
- Dedalus AI calls take 20-40 seconds

### Cache Issues
- Invalidate: `POST /cache/invalidate/{patient_id}`
- Clear all: `POST /cache/clear`

### Missing Data
- Ensure MRI CSV has required columns
- Provide previous_sessions for long-term recall

See [DEPLOYMENT.md](DEPLOYMENT.md) for more troubleshooting.

## 📚 Next Steps

1. ✅ **Deploy to Render** - Follow DEPLOYMENT.md
2. ✅ **Test health endpoint** - Verify deployment
3. ✅ **Update your backend** - Add API integration
4. ✅ **Test with real session** - End-to-end verification
5. ✅ **Monitor performance** - Check logs and metrics

## 🤝 Integration Checklist

- [ ] Service deployed to Render
- [ ] Environment variables configured
- [ ] Health endpoint responding
- [ ] Your backend can reach the API
- [ ] Session analysis endpoint tested
- [ ] Dashboard endpoint tested
- [ ] MRI analysis tested (if using)
- [ ] Frontend receiving correct format
- [ ] Error handling implemented
- [ ] Monitoring set up

## 📝 Key Features

✅ **Synchronous analysis** - Returns immediately, no polling
✅ **Simple caching** - 24-hour TTL for dashboard data
✅ **Rule-based MRI** - Estimates missing brain regions
✅ **5 memory metrics** - Comprehensive cognitive tracking
✅ **Doctor alerts** - Automatic risk detection
✅ **Frontend-ready** - Data in exact TypeScript format
✅ **Render deployment** - Simple YAML configuration
✅ **Open for MVP** - No authentication required

## 🆘 Support

- **Deployment issues:** See DEPLOYMENT.md
- **Integration questions:** See INTEGRATION_EXAMPLE.py
- **API errors:** Check `/health` endpoint and Render logs
- **Test locally first:** `python api_server.py`

---

Built with Dedalus AI, FastAPI, and ❤️ for dementia patient care.
