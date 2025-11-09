# Real Call Chain - What Actually Exists vs What Needs to Happen

## 🔍 Current State (What EXISTS Now)

### **Backend (mindmate-backend)**

**Existing Endpoints:**
```python
GET  /health                                    ✅ Working
GET  /patients                                  ✅ Working - returns list from Supabase
POST /patients                                  ✅ Working - creates in Supabase
GET  /sessions                                  ✅ Working - returns list from Supabase
POST /sessions                                  ✅ Working - creates in Supabase
POST /sessions/analyze/{session_id}             ⚠️  STUB - just returns mock response
GET  /memories                                  ✅ Working - returns list from Supabase
POST /memories                                  ✅ Working - creates in Supabase
GET  /doctors                                   ✅ Working
POST /doctors                                   ✅ Working
GET  /doctor-records/{patient_id}               ✅ Working
POST /doctor-records                            ✅ Working
GET  /patients/{patient_id}/analytics           ⚠️  HARDCODED - returns fake brain regions
```

**What's Hardcoded in `/patients/{patient_id}/analytics`:**
```python
# routes/sessions.py line 261-268
brain_regions = BrainRegionScores(
    hippocampus=82.5,          # ❌ FAKE
    prefrontalCortex=77.3,     # ❌ FAKE
    temporalLobe=85.2,         # ❌ FAKE
    parietalLobe=79.0,         # ❌ FAKE
    amygdala=88.4,             # ❌ FAKE
    cerebellum=83.0            # ❌ FAKE
)

memory_metrics = MemoryMetrics(
    shortTermRecall=[...],     # ✅ Uses session data
    longTermRecall=[],         # ❌ EMPTY
    semanticMemory=[],         # ❌ EMPTY
    episodicMemory=[],         # ❌ EMPTY
    workingMemory=[]           # ❌ EMPTY
)
```

### **Frontend (doctor-frontend)**

**API Calls Frontend Makes:**
```typescript
// lib/api/client.ts

api.health()                               ✅ Calls: GET /health
api.patients.list()                        ✅ Calls: GET /patients
api.patients.get(id)                       ✅ Calls: GET /patients/{id}
api.patients.create(data)                  ✅ Calls: POST /patients
api.patients.getCognitiveData(id)          ❌ Calls: GET /patients/{id}/cognitive-data (DOESN'T EXIST!)
api.sessions.list()                        ✅ Calls: GET /sessions
api.sessions.create(data)                  ✅ Calls: POST /sessions
api.memories.list()                        ✅ Calls: GET /memories
api.memories.create(data)                  ✅ Calls: POST /memories
```

**PROBLEM:** Frontend calls `/patients/{id}/cognitive-data` but backend has `/patients/{id}/analytics`!

---

## 🎯 Real Data Flow (Current Implementation)

### **1. Doctor Opens Dashboard**

```
Doctor opens doctor-frontend
  ↓
Frontend calls: api.patients.getCognitiveData(patient_id)
  ↓
GET /patients/{patient_id}/cognitive-data
  ↓
❌ 404 NOT FOUND - This endpoint doesn't exist!
  ↓
Frontend shows error or uses mock data
```

**Alternative (if they fix the endpoint name):**
```
Frontend calls: GET /patients/{patient_id}/analytics
  ↓
Backend (routes/sessions.py:252)
  ↓
Fetches from Supabase:
  - patient data
  - sessions data
  ↓
Returns HARDCODED brain regions + basic session scores
  ↓
Frontend displays fake brain region data
```

### **2. Patient Has Video Call** (stellar-mind-companion)

```
User opens stellar-mind-companion
  ↓
LiveKit video call
  ↓
Transcript generated
  ↓
Frontend calls: POST /sessions
  {
    patient_id: "uuid",
    transcript: "conversation text...",
    exercise_type: "memory_recall"
  }
  ↓
Backend stores in Supabase
  ↓
Returns session_id
```

**Then (if analysis is triggered):**
```
Frontend (or timer) calls: POST /sessions/analyze/{session_id}
  ↓
Backend (routes/sessions.py:89)
  ↓
Just returns: {"status": "Analysis started in background.", "session_id": "..."}
  ↓
❌ NO ACTUAL ANALYSIS HAPPENS - It's a stub!
```

---

## 🚀 What SHOULD Happen (After Integration)

### **Complete Integration Flow:**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. VIDEO CALL ENDS                                           │
└─────────────────────────────────────────────────────────────┘
                         │
stellar-mind-companion → POST /sessions
                         │ {patient_id, transcript}
                         ↓
                    Supabase stores
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. TRIGGER ANALYSIS (automatic or manual)                    │
└─────────────────────────────────────────────────────────────┘
                         │
Frontend/Cron → POST /sessions/analyze/{session_id}
                         ↓
Backend (UPDATED routes/sessions.py)
                         │
                         ├─ Fetch session from Supabase
                         ├─ Fetch patient from Supabase
                         ├─ Fetch previous sessions
                         │
                         ↓
                    CALL COGNITIVE API
                         │
    POST https://mindmate-cognitive-api.onrender.com/analyze/session
    {
      session_id: "...",
      patient_id: "...",
      transcript: "...",
      patient_profile: {...},
      previous_sessions: [...]
    }
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ COGNITIVE API PROCESSING                                     │
└─────────────────────────────────────────────────────────────┘
                         │
    services/session_analyzer.py
                         │
      ├─ Dedalus AI: Extract memories
      │  └─ Returns: [{title, description, emotional_tone}, ...]
      │
      ├─ tools/cognitive_assessment.py
      │  └─ Returns: {temporal: 0.7, recall: 0.6, speech: 0.75}
      │
      └─ tools/memory_metrics_engine.py
         └─ Returns: {
              shortTermRecall: 0.65,
              longTermRecall: 0.58,
              semanticMemory: 0.72,
              episodicMemory: 0.55,
              workingMemory: 0.68
            }
                         │
                         ↓
        Returns to Backend:
        {
          "overall_score": 0.65,
          "memories": [...],
          "cognitive_test_scores": [...],
          "memory_metrics": {...},
          "doctor_alerts": [...]
        }
                         │
                         ↓
Backend stores in Supabase:
  - ai_extracted_data
  - cognitive_test_scores
  - memory_metrics
  - overall_score
                         │
Backend stores memories in ChromaDB
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. DOCTOR VIEWS DASHBOARD                                    │
└─────────────────────────────────────────────────────────────┘
                         │
Doctor opens dashboard → GET /patients/{id}/analytics
                         ↓
Backend (UPDATED routes/sessions.py)
                         │
                         ├─ Fetch patient from Supabase
                         ├─ Fetch all sessions from Supabase
                         │
                         ↓
                    CALL COGNITIVE API
                         │
POST https://mindmate-cognitive-api.onrender.com/patient/dashboard
{
  patient_id: "...",
  patient_name: "...",
  sessions: [...30 sessions with ai_extracted_data...],
  mri_csv_path: "data/mri/patient_001.csv"
}
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ COGNITIVE API DASHBOARD GENERATION                           │
└─────────────────────────────────────────────────────────────┘
                         │
      Check cache (24hr TTL)
                         │
                         ├─ Cache hit? Return cached
                         │
                         └─ Cache miss:
                              │
        tools/brain_region_mapper.py
          ├─ Read MRI CSV
          └─ Returns: {
                hippocampus: 0.75 (REAL from CSV),
                prefrontalCortex: 0.80 (REAL calculated),
                ...
              }
                              │
        tools/memory_metrics_engine.py
          ├─ Process 30 sessions with ai_extracted_data
          └─ Returns time series for all 5 metrics:
              {
                shortTermRecall: [{timestamp, score}, ...],
                longTermRecall: [{timestamp, score}, ...],
                semanticMemory: [{timestamp, score}, ...],
                episodicMemory: [{timestamp, score}, ...],
                workingMemory: [{timestamp, score}, ...]
              }
                              │
        Combine into PatientData format
                         │
                         ↓
        Returns to Backend:
        {
          patientId: "...",
          patientName: "...",
          brainRegions: {...REAL DATA...},
          memoryMetrics: {...REAL TIME SERIES...},
          recentSessions: [...],
          overallCognitiveScore: 0.68,
          memoryRetentionRate: 0.65
        }
                         │
                         ↓
Backend returns to Frontend
                         │
                         ↓
Frontend displays REAL charts with REAL data
```

---

## 📊 Summary: Fake vs Real

### **Currently FAKE:**

❌ Brain region scores (hardcoded to 82.5, 77.3, etc.)
❌ Memory metrics (longTerm, semantic, episodic, working all empty)
❌ Session analysis (stub that does nothing)
❌ Memory extraction (not happening)
❌ Risk alerts (not generated)

### **Currently REAL:**

✅ Supabase database connection
✅ Patient CRUD operations
✅ Session CRUD operations
✅ Memory CRUD operations
✅ Doctor records
✅ Basic session storage

### **After Integration - Will Be REAL:**

✅ Brain regions from actual MRI CSV files
✅ All 5 memory metrics with time series data
✅ Dedalus AI memory extraction
✅ Cognitive test scoring
✅ Doctor risk alerts
✅ Complete analytics pipeline

---

## 🔧 What Needs to Change

### **1. Fix Frontend Endpoint Mismatch**

Either:
- Change frontend to call `/patients/{id}/analytics` instead of `/cognitive-data`
- OR add alias in backend: `/patients/{id}/cognitive-data` → `/analytics`

### **2. Deploy Cognitive API**

- Deploy models repo to Render
- Get URL: `https://mindmate-cognitive-api.onrender.com`

### **3. Update Backend**

Add to backend repo:
- `services/cognitive_api_client.py` - Client to call Cognitive API
- Update `routes/sessions.py`:
  - `POST /sessions/analyze/{id}` - Call Cognitive API instead of stub
  - `GET /patients/{id}/analytics` - Call Cognitive API for dashboard

### **4. Update Frontend**

- Fix endpoint name mismatch
- Add loading states for analysis (60-120 seconds)
- Handle real-time data instead of mock data

---

## 🎯 Priority Order

1. **Deploy Cognitive API** (5 min) - Makes it available
2. **Fix endpoint mismatch** (2 min) - Frontend can call backend
3. **Update backend with integration** (15 min) - Connects everything
4. **Test with real data** (10 min) - Verify it works
5. **Deploy updated backend** (5 min) - Make it live

**Total: ~40 minutes to go from fake data to real AI-powered analysis**
