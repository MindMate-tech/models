# 🧠 Complete MindMate Workflow Integration

## Overview: How Everything Fits Together

MindMate has **3 main data sources** that feed into **1 AI-powered query system**:

```
┌─────────────────────────────────────────────────────────────────┐
│                        MINDMATE SYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────────┐  │
│  │  VIDEO CALL   │  │  MRI UPLOAD   │  │  MANUAL ENTRY    │  │
│  │   SESSIONS    │  │   (IMAGING)   │  │   (NOTES, ETC)   │  │
│  └───────┬───────┘  └───────┬───────┘  └────────┬─────────┘  │
│          │                  │                    │             │
│          ▼                  ▼                    ▼             │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              SUPABASE DATABASE                           │ │
│  │  • patients table                                        │ │
│  │  • sessions table (with AI analysis)                     │ │
│  │  • mri_scans table (brain region data)                   │ │
│  └──────────────────────┬───────────────────────────────────┘ │
│                         │                                      │
│                         ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │         COGNITIVE API (mindmate-demo)                    │ │
│  │  • Doctor Query Agent (Natural Language)                 │ │
│  │  • Session Analysis                                      │ │
│  │  • Risk Assessment                                       │ │
│  │  • Predictive Scoring                                    │ │
│  └──────────────────────┬───────────────────────────────────┘ │
│                         │                                      │
│                         ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              DOCTOR DASHBOARD                             │ │
│  │  • Patient lists                                         │ │
│  │  • Brain region visualizations                           │ │
│  │  • Session history & trends                              │ │
│  │  • AI-powered insights                                   │ │
│  │  • Natural language queries                              │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎬 Complete User Journey

### **Scenario: New Patient with Memory Concerns**

---

### **Step 1: Patient Enrollment**

**Frontend → Backend**
```javascript
POST /patients
{
  "name": "Alice Example",
  "dob": "1980-06-15",
  "gender": "Female",
  "diagnosis": "MCI",
  "interests": ["gardening", "cooking"]
}
```

**Result:** Patient created in database with `patient_id`

---

### **Step 2: MRI Upload (Brain Imaging)**

**Frontend → Backend → MRI Service**

```javascript
// 1. Frontend uploads MRI file
const formData = new FormData();
formData.append('file', mriFile);
formData.append('age', '45');
formData.append('sex', 'Female');

// 2. Backend forwards to MRI service
POST http://3.143.242.154/upload
→ Returns: { job_id: "abc-123" }

// 3. Backend polls for results (30-60 seconds)
GET http://3.143.242.154/status/abc-123
→ Returns: { status: "processing" }

// 4. When complete, get results
GET http://3.143.242.154/results/abc-123
→ Returns: {
  "Left-Hippocampus": { "volume": 3200.5, "normalized": 0.00213 },
  "Right-Hippocampus": { "volume": 3100.2, "normalized": 0.00207 },
  "Temporal-Lobe": { "volume": 45000.0, "normalized": 0.03000 },
  ...
}

// 5. Store MRI results in database
INSERT INTO mri_scans (patient_id, brain_regions, scan_date)
VALUES (patient_id, {...}, NOW())
```

**Database After MRI Upload:**
```sql
mri_scans table:
┌────────────┬─────────────────────────────────┬─────────────┐
│ patient_id │ brain_regions                   │ scan_date   │
├────────────┼─────────────────────────────────┼─────────────┤
│ alice-456  │ {"hippocampus": 0.82, ...}     │ 2025-11-09  │
└────────────┴─────────────────────────────────┴─────────────┘
```

---

### **Step 3: Video Call Session (Memory Exercise)**

**Frontend Video Call → Backend → Cognitive API**

```javascript
// 1. Patient completes video call with memory recall exercise
// Transcript captured: "Patient remembered 3 out of 5 family members..."

// 2. Frontend sends session data to backend
POST /sessions
{
  "patient_id": "alice-456",
  "transcript": "Doctor: Tell me about your family...",
  "exercise_type": "memory_recall",
  "cognitive_test_scores": [
    { "test_name": "Memory Recall", "score": 8, "max_score": 10 }
  ]
}

// 3. Backend calculates overall_score
overall_score = (8/10) * 100 = 80%

// 4. Backend saves session, then calls Cognitive API for AI analysis
POST https://mindmate-cognitive-api.onrender.com/analyze/session
{
  "session_id": "session-789",
  "patient_id": "alice-456",
  "transcript": "...",
  "patient_profile": { "name": "Alice", "age": 45, ... },
  "previous_sessions": [...]
}

// 5. Cognitive API (Dedalus AI) analyzes:
→ Extracts memories mentioned
→ Calculates memory metrics (5 types)
→ Detects patterns and trends
→ Generates doctor alerts
→ Returns comprehensive analysis

// 6. Backend stores AI analysis in session.ai_extracted_data
UPDATE sessions
SET ai_extracted_data = {...}
WHERE session_id = "session-789"
```

**Database After Session:**
```sql
sessions table:
┌─────────────┬────────────┬───────┬────────────────────────────┐
│ session_id  │ patient_id │ score │ ai_extracted_data          │
├─────────────┼────────────┼───────┼────────────────────────────┤
│ session-789 │ alice-456  │ 80    │ {"memories": [...],        │
│             │            │       │  "alerts": [...],          │
│             │            │       │  "trends": [...]}          │
└─────────────┴────────────┴───────┴────────────────────────────┘
```

---

### **Step 4: Doctor Views Patient Dashboard**

**Frontend → Backend → Cognitive API**

```javascript
// 1. Doctor opens Alice's dashboard
GET /patients/alice-456/analytics

// 2. Backend calls Cognitive API for dashboard data
POST https://mindmate-cognitive-api.onrender.com/patient/dashboard
{
  "patient_id": "alice-456",
  "patient_name": "Alice Example",
  "sessions": [...],
  "mri_csv_path": null,
  "days_back": 30
}

// 3. Cognitive API generates:
→ Brain region scores (from MRI in database)
→ Memory metrics time series (from sessions)
→ Recent sessions summary
→ Overall cognitive score
→ Memory retention rate

// 4. Frontend displays:
```

**Dashboard Shows:**
```
┌─────────────────────────────────────────────────────────────┐
│  Alice Example (Age 45) - Patient Dashboard                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🧠 Brain Regions (from MRI):                              │
│     Hippocampus:      ████████░░ 82%                       │
│     Temporal Lobe:    ████████░░ 85%                       │
│     Frontal Cortex:   ███████░░░ 78%                       │
│                                                             │
│  📊 Memory Metrics (from Sessions):                        │
│     Short-term:  [Chart showing trend over time]          │
│     Long-term:   [Chart showing trend over time]          │
│                                                             │
│  📝 Recent Sessions:                                       │
│     Nov 9:  Score 80% ✅                                   │
│     Nov 2:  Score 75% ⚠️                                   │
│     Oct 26: Score 78% ✅                                   │
│                                                             │
│  ⚡ Overall Score: 77.6%                                   │
│  💾 Memory Retention: 84%                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### **Step 5: Doctor Asks Natural Language Question**

**Frontend Chat → Backend → Cognitive API Doctor Query Agent**

```javascript
// 1. Doctor types in chat: "Is Alice at risk?"

POST /doctor/query
{
  "query": "Is Alice at risk?",
  "context": { "patient_id": "alice-456", "doctor_id": "dr-smith" }
}

// 2. Doctor Query Agent (Dedalus AI):
→ Detects patient_id in context
→ Calls tools.get_patient_by_id("alice-456")
→ Calls tools.analyze_patient_decline("alice-456")
→ Uses Claude Sonnet 4 (complex medical query)
→ Generates response with reasoning

// 3. Response returned:
{
  "success": true,
  "response": "Alice shows moderate concern. Her current
              average score (77.6%) is above the risk threshold,
              but there's a declining trend of -2.5% per session
              over the past month. Key concerns:
              - Hippocampal volume at 82% (slightly below normal)
              - Inconsistent performance (75%-80% range)
              - Working memory shows 15% decline

              Recommendations:
              - Increase session frequency to weekly
              - Consider cognitive exercises targeting working memory
              - Monitor for further decline over next 2 weeks",
  "tools_used": ["get_patient_by_id", "analyze_patient_decline"],
  "model_info": {
    "model": "claude-sonnet-4",
    "complexity": "complex"
  }
}
```

---

### **Step 6: Doctor Queries About Sessions**

**Using Session Integration We Just Built**

```javascript
// Doctor asks: "What happened in her last session?"

POST /doctor/query
{
  "query": "Analyze her last session",
  "context": { "session_id": "session-789" }  // ← session_id detected!
}

// Doctor Query Agent:
→ Detects session_id in context
→ Routes to: tools.analyze_session_performance("session-789")
→ Retrieves session with patient context
→ Compares to patient's average
→ Identifies concerns

// Response:
{
  "response": "Session analysis for Alice's Nov 9 session:

              Performance: 80% (Above her average of 77.6%)

              Key Findings:
              • Memory Recall: 8/10 (Strong performance)
              • Above patient's typical level (+2.4%)
              • No critical concerns identified

              Notable Events:
              • Successfully recalled family members
              • Slight hesitation on recent events

              Recommendations:
              • Continue current exercise routine
              • Monitor consistency in next session",
  "tools_used": ["analyze_session_performance"],
  "raw_data": {
    "score": 80,
    "comparison_to_average": "Above average",
    "findings": [...]
  }
}
```

---

### **Step 7: Doctor Asks Predictive Question**

**Using Predictive Risk Scoring We Built**

```javascript
// Doctor asks: "Which patients will decline next month?"

POST /doctor/query
{
  "query": "Predict which patients will decline next month",
  "context": { "doctor_id": "dr-smith" }
}

// Doctor Query Agent:
→ Detects "predict" keyword
→ Routes to: tools.predict_decline_risk(min_probability=0.4)
→ Runs linear regression on score trends
→ Calculates decline probability for all patients
→ Returns predictions sorted by risk

// Response (with Sequential Thinking):
{
  "response": "## Reasoning Process

              1. ✅ Analyzed score trends for all patients
              2. ✅ Applied linear regression to predict next month
              3. ✅ Calculated decline probability (0-100%)
              4. ✅ Identified 3 high-risk patients

              ## Predictions

              🔴 Bob Smith - 85% decline probability
                 Current: 52% → Predicted: 38% (-14 points)
                 Reason: Rapid declining trend over 4 sessions
                 Action: Immediate intervention needed

              🟠 Carol Jones - 65% decline probability
                 Current: 61% → Predicted: 52% (-9 points)
                 Reason: Moderate decline with high variability
                 Action: Increase monitoring frequency

              🟡 Alice Example - 35% decline probability
                 Current: 78% → Predicted: 74% (-4 points)
                 Reason: Minor decline but stable overall
                 Action: Continue current plan",
  "tools_used": ["predict_decline_risk"],
  "raw_data": {
    "predictions": [...],
    "cache_info": { "cached": true, "age_minutes": 5 }
  }
}
```

---

## 🔄 Complete Data Flow

### **How Data Moves Through The System**

```
1. MRI UPLOAD FLOW:
   Frontend → Backend → MRI Service (http://3.143.242.154)
                                     ↓ (30-60 sec processing)
                             Brain Region Volumes
                                     ↓
                             Supabase (mri_scans)
                                     ↓
                      Cognitive API (dashboard generation)
                                     ↓
                            Frontend Dashboard

2. SESSION FLOW:
   Video Call → Backend (creates session)
                         ↓
                  Cognitive API (/analyze/session)
                  - Dedalus AI analyzes transcript
                  - Extracts memories & metrics
                         ↓
              Supabase (sessions.ai_extracted_data)
                         ↓
                Doctor Dashboard & Queries

3. DOCTOR QUERY FLOW:
   Doctor types question → Backend (/doctor/query)
                                   ↓
                          Cognitive API Doctor Agent
                          - Detects intent
                          - Routes to appropriate tool
                          - Uses patient_id/session_id context
                                   ↓
                           Tool executes:
                           • get_patient_by_id
                           • analyze_session_performance ← NEW!
                           • predict_decline_risk
                           • compare_patients
                                   ↓
                          Dedalus AI (Claude Sonnet/Haiku)
                          - Generates natural language response
                          - Shows reasoning steps
                          - Provides recommendations
                                   ↓
                            Frontend Chat Display
```

---

## 🎯 Key Integration Points

### **Where MRI Fits:**

1. **Brain Region Baseline**
   - MRI provides structural brain data
   - Used to understand patient's physical brain health
   - Combined with session data for complete picture

2. **Dashboard Visualization**
   - Brain region heatmap from MRI
   - Memory metrics from sessions
   - Together show: structure + function

3. **Doctor Queries Can Reference Both:**
   ```javascript
   "Why is Bob declining?"
   → AI checks:
     • Session scores (behavioral data)
     • MRI brain regions (structural data)
     • Responds: "Bob's hippocampus shows 15% atrophy (MRI)
                  AND his memory recall declined 20% (sessions)"
   ```

### **Where Sessions Fit:**

1. **Functional Assessment**
   - Regular cognitive testing via video calls
   - Tracks performance over time
   - Shows trends and patterns

2. **AI Analysis Input**
   - Transcript analyzed by Dedalus
   - Extracts specific memories
   - Identifies concerning patterns

3. **Doctor Queries Use Session Data:**
   - "Analyze this session" ← NEW integration!
   - "Show recent sessions for patient"
   - "Compare two sessions"

### **Where Doctor Queries Fit:**

1. **Natural Language Interface**
   - Doctors ask questions naturally
   - No SQL, no complex filtering
   - AI figures out what to do

2. **Combines All Data Sources:**
   - MRI data (brain structure)
   - Session data (cognitive function)
   - Historical trends (predictions)

3. **Contextual Understanding:**
   - Remembers previous questions (memory system)
   - Understands "them", "that patient", etc.
   - Routes to correct tools automatically

---

## 📊 Complete Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     MINDMATE ARCHITECTURE                      │
└────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                         │
│  • Patient Dashboard                                            │
│  • Video Call Interface                                         │
│  • MRI Upload Form                                              │
│  • Doctor Chat (Natural Language Queries)                       │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  BACKEND (mindmate-backend)                     │
│  • FastAPI Server                                               │
│  • Session CRUD endpoints                                       │
│  • Patient management                                           │
│  • cognitive_api_client.py (calls Cognitive API)                │
│                                                                 │
│  NEW ENDPOINTS:                                                 │
│  → POST /doctor/query (natural language)                        │
│  → POST /sessions/{id}/insights (session analysis)              │
│  → GET /patients/{id}/risk-assessment                           │
└─────┬───────────────────────────┬───────────────────────────────┘
      │                           │
      │                           │ (calls externally)
      │                           ▼
      │              ┌───────────────────────────────┐
      │              │   MRI SERVICE (External)      │
      │              │   http://3.143.242.154        │
      │              │  • Processes MRI scans        │
      │              │  • Returns brain regions      │
      │              │  • Async job queue            │
      │              └───────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│           COGNITIVE API (mindmate-demo on Render)               │
│                                                                 │
│  🤖 Dedalus AI Framework:                                       │
│     • SessionAnalyzer (analyze transcripts)                     │
│     • DoctorQueryAgent (natural language queries)               │
│                                                                 │
│  🔧 Doctor Tools (8 tools):                                     │
│     1. get_patient_by_id                                        │
│     2. search_patients                                          │
│     3. get_at_risk_patients                                     │
│     4. compare_patients                                         │
│     5. analyze_patient_decline                                  │
│     6. get_session_summary                                      │
│     7. get_session_by_id ← NEW!                                 │
│     8. analyze_session_performance ← NEW!                       │
│                                                                 │
│  🧠 AI Features:                                                │
│     • Intelligent model routing (Haiku/Sonnet)                  │
│     • Sequential thinking (medical reasoning)                   │
│     • Memory system (follow-up queries)                         │
│     • Predictive risk scoring (ML predictions)                  │
│                                                                 │
│  📊 Endpoints:                                                  │
│     → POST /analyze/session (transcript → AI analysis)          │
│     → POST /patient/dashboard (generate dashboard data)         │
│     → POST /doctor/query (natural language interface)           │
│     → GET /doctor/at-risk (quick risk check)                    │
│     → POST /mri/analyze (analyze MRI data)                      │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SUPABASE DATABASE                           │
│                                                                 │
│  patients table:                                                │
│    • patient_id, name, dob, gender                              │
│    • diagnosis, interests                                       │
│                                                                 │
│  sessions table:                                                │
│    • session_id, patient_id, session_date                       │
│    • transcript, overall_score                                  │
│    • ai_extracted_data (JSON):                                  │
│        - memories_extracted                                     │
│        - cognitive_test_scores                                  │
│        - memory_metrics                                         │
│        - doctor_alerts                                          │
│                                                                 │
│  mri_scans table:                                               │
│    • scan_id, patient_id, scan_date                             │
│    • brain_regions (JSON):                                      │
│        - hippocampus                                            │
│        - temporal_lobe                                          │
│        - frontal_cortex                                         │
│        - etc.                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Summary: How It All Works Together

### **3 Data Inputs:**
1. **MRI Scans** → Brain structure (physical)
2. **Video Sessions** → Cognitive function (behavioral)
3. **Manual Entry** → Notes, observations

### **1 Central Database:**
- Supabase stores everything
- patients, sessions, mri_scans tables
- Indexed for fast queries

### **1 AI-Powered API:**
- Cognitive API (mindmate-demo)
- Analyzes all data sources
- Natural language interface
- 8 specialized tools + Dedalus AI

### **1 Unified Interface:**
- Doctor dashboard shows everything
- Chat interface for questions
- All data integrated in real-time

---

**The magic is that doctors can ask questions naturally and the AI:**
1. Figures out what data is needed (MRI? Sessions? Both?)
2. Retrieves it from the right tables
3. Analyzes it with the right tools
4. Explains the reasoning
5. Provides actionable recommendations

**Example:**
```
Doctor: "Why is Bob declining?"

AI thinks:
1. Get Bob's patient data ✓
2. Get Bob's sessions ✓
3. Get Bob's MRI data ✓
4. Analyze trend ✓
5. Compare to baseline ✓

AI responds:
"Bob shows 20% decline over 3 months. Contributing factors:
- Sessions: Memory recall dropped 15% (behavioral)
- MRI: Hippocampus 18% below normal (structural)
- Pattern: Difficulty with recent events vs. old memories
Recommendation: Consider medication adjustment + weekly sessions"
```

That's the complete workflow! 🎯
