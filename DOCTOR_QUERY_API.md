# 🩺 MindMate Doctor Query API

## AI-Powered Natural Language Interface for Medical Professionals

This API allows doctors to query patient data using natural language. The AI agent uses Dedalus tool calling to intelligently select and execute the appropriate functions to answer complex medical queries.

---

## 🚀 Quick Start

### **Main Endpoint**

```bash
POST /doctor/query
Content-Type: application/json

{
  "query": "Show me all at-risk patients",
  "context": {
    "doctor_id": "optional",
    "patient_id": "optional"
  }
}
```

### **Response**

```json
{
  "success": true,
  "query": "Show me all at-risk patients",
  "response": "AI-generated analysis with data and insights",
  "tools_used": ["get_at_risk_patients"]
}
```

---

## 📋 Sample Queries (MVP Showcase)

### **1. Find At-Risk Patients**

**Query:** `"Show me all at-risk patients"`

**What the AI does:**
- Calls `get_at_risk_patients()` tool
- Analyzes scores and trends
- Returns patients with **detailed risk reasoning**

**Response includes:**
- Patient names and IDs
- Average and latest cognitive scores
- **Risk reasons** (why they're flagged):
  - "Average score (45%) below threshold (50%)"
  - "Declining trend: 30% drop from earlier sessions"
  - "Latest session critically low (25%)"
  - "High score variability (40% range)"
  - "Limited session data (2 sessions)"
- Risk level (critical/high/medium)
- Actionable recommendations

**Example response:**
```
I've identified 5 at-risk patients requiring immediate attention:

1. Alice Example (Age 45) - HIGH RISK
   - Average Score: 0.5%
   - Risk Reasons:
     * Average score (0.5%) below threshold (50%)
     * Latest session critically low (0.5%)
   - Recommendation: Immediate medical evaluation

2. Test Patient (Age 55) - HIGH RISK
   - Average Score: 1.0%
   - Risk Reasons:
     * Average score (1.0%) below threshold (50%)
     * Limited session data (1 session)
   - Recommendation: Increase session frequency
```

---

### **2. Explain Why a Patient is Declining**

**Query:** `"Why is patient {patient_id} declining?"`

**What the AI does:**
- Calls `analyze_patient_decline(patient_id)` tool
- Analyzes session history, score trends, gaps
- Identifies specific causes

**Response includes:**
- Decline rate percentage
- Detailed findings with severity:
  - "Rapid cognitive decline detected (35% drop)"
  - "Irregular session attendance (14 days between sessions)"
  - "High performance variability"
- Specific recommendations:
  - "Immediate medical evaluation recommended"
  - "Increase session frequency to monitor progression"
  - "Improve adherence to weekly schedule"
- Risk level assessment

---

### **3. Compare Multiple Patients**

**Query:** `"Compare patients A and B"`
*or*
`"Compare patient {id1} with patient {id2}"`

**What the AI does:**
- Calls `compare_patients([id1, id2])` tool
- Analyzes metrics across patients
- Generates insights

**Response includes:**
- Side-by-side comparison:
  - Average scores
  - Latest scores
  - Trend directions (improving/declining/stable)
  - Total sessions
  - Age and demographics
- **Key insights:**
  - "John has highest average score (75%)"
  - "Alice has lowest score (45%)"
  - "2 patients showing improvement: John, Mary"
  - "1 patient declining: Alice"
- Summary with actionable recommendations

---

### **4. Search for Patients by Criteria**

**Query:** `"Find female patients over 60"`
**Query:** `"Show me patients named John"`
**Query:** `"Who are the oldest patients?"`

**What the AI does:**
- Calls `search_patients()` with appropriate filters
- Returns matching patients
- Provides insights

**Response example:**
```
Found 18 female patients in the database:
- Alice Example (Age 45)
- [... more patients ...]

All patients are aged 45.
No patients found over age 60.
```

---

### **5. Get Patient Details**

**Query:** `"Tell me about patient {patient_id}"`
**Query:** `"Show me John Doe's complete history"`

**What the AI does:**
- Calls `get_patient_by_id()` tool
- Retrieves complete profile and session history
- Analyzes trends

**Response includes:**
- Demographics (name, age, gender)
- Total sessions
- Average score
- Last session date
- Session history
- Trend analysis

---

### **6. Complex Multi-Step Queries**

**Query:** `"Find patients declining rapidly and tell me which ones need immediate attention"`

**What the AI does:**
- Calls `get_at_risk_patients()` with low threshold
- Calls `analyze_patient_decline()` for each
- Prioritizes by severity
- Generates comprehensive report

**Response:**
```
Analyzing patient database for rapid cognitive decline...

CRITICAL PRIORITY:
1. Alice Example - 35% decline rate
   - Findings: Rapid cognitive decline, irregular attendance
   - Recommendation: Immediate neurologist consultation

HIGH PRIORITY:
2. Test Patient - 25% decline rate
   - Findings: Limited data, low scores
   - Recommendation: Increase monitoring frequency

SUMMARY:
2 patients require immediate intervention.
Recommended actions: [detailed list]
```

---

## 🛠️ Fast Endpoints (No AI, Instant Results)

For simple queries where you don't need AI reasoning:

### **Get At-Risk Patients (Fast)**

```bash
GET /doctor/at-risk?threshold=0.5
```

Returns list of at-risk patients with risk reasoning, no AI delay.

### **Get Patient Details (Fast)**

```bash
GET /doctor/patient/{patient_id}
```

Returns patient info instantly, no AI processing.

---

## 🧠 How It Works

```
Doctor Query (natural language string)
         ↓
Dedalus AI Agent
         ↓
   [Analyzes query]
         ↓
  Selects appropriate tool(s):
  ├─ get_at_risk_patients()
  ├─ compare_patients()
  ├─ analyze_patient_decline()
  ├─ search_patients()
  ├─ get_patient_by_id()
  └─ get_session_summary()
         ↓
  Executes tool(s)
         ↓
  Analyzes results with AI
         ↓
  Returns rich response with:
  ✓ Data
  ✓ Insights
  ✓ Risk reasoning
  ✓ Recommendations
```

---

## 📊 Available Tools

The AI agent has access to these tools:

| Tool | Purpose |
|------|---------|
| `get_patient_by_id` | Get detailed patient information |
| `search_patients` | Search by name, age, gender |
| `get_at_risk_patients` | Find patients below score threshold with **risk reasoning** |
| `compare_patients` | Compare multiple patients |
| `analyze_patient_decline` | Detailed analysis of why patient declining |
| `get_session_summary` | Get recent session history |

---

## 🎯 Key Features

### **1. Risk Reasoning (Why Patients Are Flagged)**

Unlike simple threshold checks, our system explains **WHY** each patient is at risk:

- Low average scores
- Declining trends with % drop
- Critically low recent sessions
- High score variability
- Session attendance issues

### **2. Multi-Patient Comparison**

Compare patients across:
- Cognitive scores (average, latest, trend)
- Demographics
- Session frequency
- Improvement vs decline

### **3. Decline Analysis**

For declining patients, get:
- Decline rate %
- Specific findings (high/medium severity)
- Contributing factors
- Actionable recommendations

### **4. Natural Language Flexibility**

Ask questions naturally:
- ✅ "Who needs attention?"
- ✅ "Why is Margaret declining?"
- ✅ "Compare John and Alice"
- ✅ "Find older patients"

---

## 🔗 Integration Example

### Python

```python
import httpx

async def query_doctor_ai(query: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://mindmate-cognitive-api.onrender.com/doctor/query",
            json={"query": query}
        )
        return response.json()

# Usage
result = await query_doctor_ai("Show me at-risk patients")
print(result["response"])
```

### JavaScript

```javascript
const queryDoctorAI = async (query) => {
  const response = await fetch(
    'https://mindmate-cognitive-api.onrender.com/doctor/query',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    }
  );
  return response.json();
};

// Usage
const result = await queryDoctorAI('Show me at-risk patients');
console.log(result.response);
```

### cURL

```bash
curl -X POST "https://mindmate-cognitive-api.onrender.com/doctor/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me all at-risk patients"
  }'
```

---

## 💡 MVP Demo Scenarios

### **Scenario 1: Daily Risk Review**

```json
{
  "query": "Show me all patients at high risk today"
}
```

**Showcases:**
- Real-time risk detection
- Detailed reasoning for each flag
- Prioritization by severity

---

### **Scenario 2: Patient Investigation**

```json
{
  "query": "Patient Alice Example has declining scores. Why is this happening and what should we do?"
}
```

**Showcases:**
- Multi-step reasoning
- Causal analysis
- Medical recommendations

---

### **Scenario 3: Comparative Analysis**

```json
{
  "query": "Compare all patients in their 40s and tell me who's improving vs declining"
}
```

**Showcases:**
- Advanced filtering
- Trend analysis
- Group insights

---

## 🚀 Try It Now

### Test Endpoint

```bash
GET https://mindmate-cognitive-api.onrender.com/
```

Returns API info and example queries.

### Test Query

```bash
curl -X POST "http://localhost:8000/doctor/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me at-risk patients and explain why they are flagged"
  }'
```

---

## 📈 Response Time

- **AI-Powered Queries:** 3-5 seconds (intelligent analysis)
- **Fast Endpoints:** <1 second (no AI reasoning)

Choose based on your needs:
- Need reasoning & insights? Use `/doctor/query`
- Need quick data? Use `/doctor/at-risk` or `/doctor/patient/{id}`

---

## 🎓 Tips for Best Results

1. **Be specific:** "Show me at-risk patients" works better than "patients"
2. **Use patient IDs for precision:** "Compare patient {id1} and {id2}"
3. **Ask follow-up questions:** "Why is that patient declining?"
4. **Request explanations:** "Explain why they're at risk"

---

## 🔒 Security Notes

- Always use HTTPS in production
- Implement authentication/authorization
- Rate limit the endpoint
- Log queries for audit trail
- Sanitize patient data in responses

---

## 📞 Support

For API issues or feature requests:
- Check `/health` endpoint for system status
- Review logs in Render dashboard
- Test locally with `python api_server.py`

---

**Built with** ❤️ **using Dedalus AI & Claude**
