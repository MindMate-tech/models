# 🎯 Demo Queries for Judges & Investors

## Live Production API: Ready to Test

**API Endpoint:** `https://mindmate-cognitive-api.onrender.com`

All queries below are **reproducible** and work against **live production data** with real patients from Supabase.

---

## 🚀 Quick Test (Copy & Paste into Terminal)

```bash
curl -X POST "https://mindmate-cognitive-api.onrender.com/doctor/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me at-risk patients"}'
```

---

## 📋 Demo Query Categories

### ⚠️ Category 1: At-Risk Patient Detection

**What it demonstrates:** AI identifies at-risk patients and explains WHY each is flagged

#### Query 1A: Basic At-Risk Detection
```bash
curl -X POST "https://mindmate-cognitive-api.onrender.com/doctor/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me all at-risk patients"}'
```

**Expected Output:**
- List of 5 critical-risk patients
- Detailed risk reasoning for each (low scores, declining trends, etc.)
- Immediate clinical recommendations
- Severity classifications

**Key Features Demonstrated:**
- ✅ Natural language understanding
- ✅ Risk reasoning (not just threshold checks)
- ✅ Medical-grade analysis
- ✅ Actionable recommendations

---

#### Query 1B: Detailed Risk Analysis
```bash
curl -X POST "https://mindmate-cognitive-api.onrender.com/doctor/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me at-risk patients and explain in detail why each one is flagged with specific risk factors"}'
```

**Expected Output:**
- Executive summary
- Individual patient breakdowns
- Specific risk factors with percentages
- Clinical significance explanations
- Monitoring protocol recommendations

**Key Features Demonstrated:**
- ✅ Comprehensive analysis
- ✅ Specific data points (percentages, trends)
- ✅ Medical reasoning
- ✅ Treatment planning suggestions

---

### 👥 Category 2: Patient Comparison

**What it demonstrates:** AI compares patients across multiple metrics

#### Query 2A: Simple Comparison
```bash
curl -X POST "https://mindmate-cognitive-api.onrender.com/doctor/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Compare the first two patients in the database"}'
```

**Expected Output:**
- Side-by-side patient comparison
- Score differences
- Trend analysis (improving vs declining)
- Insights on who needs attention

**Key Features Demonstrated:**
- ✅ Multi-patient analysis
- ✅ Comparative insights
- ✅ Prioritization guidance

---

### 📊 Category 3: Data Exploration

**What it demonstrates:** AI answers exploratory questions about the patient database

#### Query 3A: Patient Count
```bash
curl -X POST "https://mindmate-cognitive-api.onrender.com/doctor/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "How many patients are in the database?"}'
```

#### Query 3B: Demographics
```bash
curl -X POST "https://mindmate-cognitive-api.onrender.com/doctor/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Find all female patients"}'
```

**Expected Output:**
- Patient counts
- Demographic breakdowns
- Summary statistics

---

### 📉 Category 4: Trend Analysis

**What it demonstrates:** AI identifies patterns and declining patients

#### Query 4A: Declining Patients
```bash
curl -X POST "https://mindmate-cognitive-api.onrender.com/doctor/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Which patients are showing declining cognitive trends?"}'
```

**Expected Output:**
- List of declining patients
- Decline rates (percentages)
- Time-based analysis
- Intervention recommendations

---

### 🏥 Category 5: Clinical Decision Support

**What it demonstrates:** AI provides actionable clinical recommendations

#### Query 5A: Priority Actions
```bash
curl -X POST "https://mindmate-cognitive-api.onrender.com/doctor/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What patients need immediate attention and what should I do?"}'
```

**Expected Output:**
- Prioritized patient list
- Urgent actions (24-48 hours)
- Short-term strategy (1-2 weeks)
- Long-term monitoring plans

**Key Features Demonstrated:**
- ✅ Clinical reasoning
- ✅ Time-based prioritization
- ✅ Specific action items
- ✅ Medical best practices

---

## ⚡ Fast Endpoint Demos (No AI, Instant Results)

### Fast Query 1: At-Risk List (No AI)
```bash
curl "https://mindmate-cognitive-api.onrender.com/doctor/at-risk?threshold=0.5"
```

**Response Time:** <1 second
**Returns:** JSON array of at-risk patients with risk reasons

### Fast Query 2: Patient Details
```bash
curl "https://mindmate-cognitive-api.onrender.com/doctor/patient/1c842720-4775-427c-b5ab-f2260146191b"
```

**Response Time:** <1 second
**Returns:** Complete patient profile and session history

### Fast Query 3: Database Stats
```bash
curl "https://mindmate-cognitive-api.onrender.com/doctor/database-stats"
```

**Response Time:** <1 second
**Returns:** Patient counts, session counts, sample scores

---

## 🎬 Demo Script for Presentations

### 5-Minute Demo Flow

**1. Introduction (30 seconds)**
> "MindMate uses AI to help doctors monitor cognitive health. Let me show you our natural language query system."

**2. Live Query Demo (2 minutes)**
```bash
# Run this live:
curl -X POST "https://mindmate-cognitive-api.onrender.com/doctor/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me at-risk patients and explain why they are flagged"}'
```

> "Notice how the AI doesn't just show low scores—it explains WHY each patient is at risk with specific reasons like declining trends, data gaps, and performance deficits."

**3. Highlight Key Features (1 minute)**
- Point out the risk reasoning
- Show the clinical recommendations
- Emphasize the medical-grade analysis

**4. Speed Comparison (1 minute)**
```bash
# Fast endpoint (no AI)
curl "https://mindmate-cognitive-api.onrender.com/doctor/at-risk?threshold=0.5"
```

> "We also offer fast endpoints without AI for real-time dashboards. Same data, instant response."

**5. Q&A Prep (30 seconds)**
> "All this runs on live production data with 38 patients and 22 sessions. Every query you saw is reproducible right now."

---

## 🧪 Testing in Browser DevTools

Open browser console on any webpage:

```javascript
// Test 1: At-Risk Query
fetch('https://mindmate-cognitive-api.onrender.com/doctor/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'Show me at-risk patients'
  })
})
.then(r => r.json())
.then(data => console.log(data.response));

// Test 2: Fast Endpoint
fetch('https://mindmate-cognitive-api.onrender.com/doctor/at-risk?threshold=0.5')
.then(r => r.json())
.then(console.table);
```

---

## 📱 Demo on Mobile/Tablet

Use a REST API testing app like:
- **iOS**: RestKit, HTTP Client
- **Android**: REST API Client, HTTP Request

**Endpoint:** `https://mindmate-cognitive-api.onrender.com/doctor/query`
**Method:** POST
**Body:**
```json
{
  "query": "Show me at-risk patients"
}
```

---

## 🎯 Judge-Specific Questions & Answers

### "How does this differ from a simple database query?"

**Run this comparison:**

1. Simple database filter:
```bash
curl "https://mindmate-cognitive-api.onrender.com/doctor/at-risk?threshold=0.5"
```
→ Returns patients below 50% (rule-based)

2. AI-powered analysis:
```bash
curl -X POST "https://mindmate-cognitive-api.onrender.com/doctor/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me at-risk patients"}'
```
→ Returns patients below 50% **PLUS** explains WHY, analyzes trends, gives recommendations

**The difference:**
- ❌ Database: "Score is 0.5%"
- ✅ Our AI: "Score is 0.5% (104x below threshold), latest session critically low, declining 30% from earlier, insufficient data for trend analysis, recommend immediate evaluation"

---

### "Can it handle complex multi-step reasoning?"

**Yes! Try this:**
```bash
curl -X POST "https://mindmate-cognitive-api.onrender.com/doctor/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Find declining patients, identify the most critical ones, and tell me what actions to take immediately"}'
```

**Expected:** Multi-step analysis with prioritized action plan

---

### "What's the data source?"

**Live Supabase database with:**
- 38 real patients
- 22 clinical sessions
- Real cognitive scores (0-100 scale)
- Session dates, transcripts, test results

**Verify live:**
```bash
curl "https://mindmate-cognitive-api.onrender.com/doctor/database-stats"
```

---

## 🏆 Key Differentiators to Highlight

| Feature | Traditional Systems | MindMate AI |
|---------|-------------------|------------|
| **Query Input** | SQL or structured forms | Natural language |
| **Risk Detection** | Simple threshold | Detailed reasoning with WHY |
| **Analysis** | Basic stats | Medical-grade insights |
| **Recommendations** | Generic alerts | Specific clinical actions |
| **Flexibility** | Fixed queries | Any question in plain English |
| **Speed** | Fast | 3-5s (or <1s for fast endpoints) |

---

## 💡 Advanced Demo Queries (Show Off)

### Complex Query 1: Multi-Factor Analysis
```bash
curl -X POST "https://mindmate-cognitive-api.onrender.com/doctor/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze all patients, identify patterns, prioritize by risk, and create a weekly monitoring plan"}'
```

### Complex Query 2: Comparative Cohort Analysis
```bash
curl -X POST "https://mindmate-cognitive-api.onrender.com/doctor/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Compare male vs female patients and tell me if there are any concerning trends"}'
```

---

## 📊 Expected Response Times

| Query Type | Time | Notes |
|------------|------|-------|
| Simple questions | 3-4s | "How many patients?" |
| At-risk analysis | 4-5s | Full risk reasoning |
| Complex multi-step | 5-7s | Multiple tools called |
| Fast endpoints | <1s | No AI processing |

---

## 🎥 Video Demo Script (60 seconds)

**[0:00-0:10]** "Doctors ask questions in plain English..."
*Show typing: "Show me at-risk patients"*

**[0:10-0:25]** "Our AI analyzes the database..."
*Show loading state*

**[0:25-0:50]** "And returns medical-grade analysis with specific reasoning..."
*Show response with risk factors, recommendations*

**[0:50-0:60]** "All running on live production data. Try it yourself!"
*Show API endpoint URL*

---

## 🔗 Links for Judges

- **Live API:** `https://mindmate-cognitive-api.onrender.com`
- **Health Check:** `https://mindmate-cognitive-api.onrender.com/health`
- **API Docs:** See `DOCTOR_QUERY_API.md` in repo
- **Frontend Guide:** See `FRONTEND_INTEGRATION.md`

---

## ✅ Pre-Demo Checklist

Before presenting to judges:

- [ ] Test health endpoint: `curl https://mindmate-cognitive-api.onrender.com/health`
- [ ] Run sample query to verify responses
- [ ] Check response times (should be <5s)
- [ ] Prepare backup queries in case one fails
- [ ] Have database stats ready: `curl .../doctor/database-stats`
- [ ] Test on judge's device/browser if possible

---

**🎉 Everything is production-ready and reproducible!**

All queries work right now against live data. No mock data, no fake responses—this is the real MVP in action.

**Built with ❤️ using Dedalus AI, Claude Sonnet 4, FastAPI, and Supabase**
