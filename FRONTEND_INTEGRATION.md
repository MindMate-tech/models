# 🎨 Frontend Integration Guide

## Quick Start: How to Call the Doctor Query API

### Production API Endpoint
```
https://mindmate-cognitive-api.onrender.com
```

---

## 1️⃣ Simple AI Query (Recommended for MVP)

### JavaScript/TypeScript Example

```typescript
// Basic query function
async function queryDoctorAI(userQuery: string) {
  try {
    const response = await fetch(
      'https://mindmate-cognitive-api.onrender.com/doctor/query',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userQuery
        })
      }
    );

    const data = await response.json();

    if (data.success) {
      return {
        success: true,
        analysis: data.response,  // AI-generated markdown text
        toolsUsed: data.tools_used
      };
    } else {
      return {
        success: false,
        error: data.error || 'Unknown error'
      };
    }
  } catch (error) {
    console.error('API Error:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

// Usage
const result = await queryDoctorAI("Show me at-risk patients");
console.log(result.analysis);
```

### React Component Example

```tsx
import { useState } from 'react';

function DoctorQueryPanel() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch(
        'https://mindmate-cognitive-api.onrender.com/doctor/query',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query })
        }
      );

      const data = await res.json();

      if (data.success) {
        setResponse(data.response);
      } else {
        setResponse(`Error: ${data.error}`);
      }
    } catch (error) {
      setResponse(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="doctor-query-panel">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Analyzing...' : 'Query'}
        </button>
      </form>

      {response && (
        <div className="response">
          <ReactMarkdown>{response}</ReactMarkdown>
        </div>
      )}
    </div>
  );
}
```

---

## 2️⃣ Fast Endpoints (No AI, Instant Results)

### Get At-Risk Patients (Fast)

```typescript
async function getAtRiskPatients(threshold: number = 0.5) {
  const response = await fetch(
    `https://mindmate-cognitive-api.onrender.com/doctor/at-risk?threshold=${threshold}`
  );

  const data = await response.json();

  return {
    success: data.success,
    count: data.count,
    patients: data.patients  // Array of patient objects with risk details
  };
}

// Usage
const atRisk = await getAtRiskPatients(0.5);
console.log(`Found ${atRisk.count} at-risk patients`);
```

### Get Patient Details (Fast)

```typescript
async function getPatientDetails(patientId: string) {
  const response = await fetch(
    `https://mindmate-cognitive-api.onrender.com/doctor/patient/${patientId}`
  );

  const data = await response.json();

  return {
    success: data.success,
    patient: data.patient
  };
}
```

---

## 3️⃣ Response Format

### AI Query Response (`POST /doctor/query`)

```typescript
interface QueryResponse {
  success: boolean;
  query: string;
  response: string;  // Markdown-formatted AI analysis
  tools_used: string[];  // e.g., ["get_at_risk_patients"]
  raw_data?: any;  // Optional: underlying data used
}
```

### At-Risk Response (`GET /doctor/at-risk`)

```typescript
interface AtRiskResponse {
  success: boolean;
  count: number;
  threshold: number;
  patients: AtRiskPatient[];
}

interface AtRiskPatient {
  patient_id: string;
  name: string;
  age: number;
  average_score: number;  // 0-1 scale
  latest_score: number;
  risk_level: "critical" | "high" | "medium";
  sessions_analyzed: number;
  risk_reasons: string[];  // Detailed explanations
  trend: "improving" | "declining" | "stable";
}
```

---

## 4️⃣ Pre-built Query Buttons for UI

Create quick action buttons in your UI:

```tsx
const QUICK_QUERIES = [
  {
    label: "At-Risk Patients",
    query: "Show me all at-risk patients and explain why they are flagged",
    icon: "⚠️"
  },
  {
    label: "Today's Summary",
    query: "Give me a summary of patients that need attention today",
    icon: "📋"
  },
  {
    label: "Declining Trends",
    query: "Which patients are showing declining cognitive trends?",
    icon: "📉"
  },
  {
    label: "Patient Count",
    query: "How many patients are in the system?",
    icon: "👥"
  }
];

// Render as buttons
<div className="quick-queries">
  {QUICK_QUERIES.map(q => (
    <button
      key={q.label}
      onClick={() => handleQuery(q.query)}
    >
      <span>{q.icon}</span>
      {q.label}
    </button>
  ))}
</div>
```

---

## 5️⃣ Rendering AI Responses

The AI returns **markdown-formatted text**. Use a markdown renderer:

### Install markdown renderer:
```bash
npm install react-markdown
```

### Render the response:
```tsx
import ReactMarkdown from 'react-markdown';

function ResponseDisplay({ response }: { response: string }) {
  return (
    <div className="ai-response">
      <ReactMarkdown>{response}</ReactMarkdown>
    </div>
  );
}
```

### Add styling for medical content:
```css
.ai-response {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  font-family: 'Inter', sans-serif;
}

.ai-response h1, h2, h3 {
  color: #2c3e50;
  margin-top: 20px;
}

.ai-response ul {
  list-style: none;
  padding-left: 0;
}

.ai-response li:before {
  content: "→ ";
  color: #3498db;
  font-weight: bold;
  margin-right: 8px;
}

.ai-response strong {
  color: #e74c3c;
}
```

---

## 6️⃣ Error Handling

```typescript
async function safeQuery(query: string) {
  try {
    const response = await fetch(
      'https://mindmate-cognitive-api.onrender.com/doctor/query',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
        signal: AbortSignal.timeout(30000)  // 30s timeout
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error || 'Query failed');
    }

    return data;

  } catch (error) {
    if (error.name === 'TimeoutError') {
      return { success: false, error: 'Request timed out. Please try again.' };
    }

    if (error.name === 'TypeError') {
      return { success: false, error: 'Network error. Check your connection.' };
    }

    return { success: false, error: error.message };
  }
}
```

---

## 7️⃣ Loading States & UX

```tsx
function QueryInterface() {
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState('');

  const handleQuery = async (query: string) => {
    setLoading(true);
    setProgress('Analyzing patient data...');

    // Simulate progress updates
    setTimeout(() => setProgress('Running AI analysis...'), 1000);
    setTimeout(() => setProgress('Generating recommendations...'), 2000);

    const result = await queryDoctorAI(query);

    setLoading(false);
    setProgress('');

    return result;
  };

  return (
    <>
      {loading && (
        <div className="loading-overlay">
          <Spinner />
          <p>{progress}</p>
        </div>
      )}
      {/* ... rest of UI ... */}
    </>
  );
}
```

---

## 8️⃣ Real-time Updates (Optional)

If you want to show live patient counts:

```typescript
// Poll for updates every 30 seconds
useEffect(() => {
  const fetchStats = async () => {
    const result = await getAtRiskPatients(0.5);
    setAtRiskCount(result.count);
  };

  fetchStats();  // Initial fetch
  const interval = setInterval(fetchStats, 30000);  // Every 30s

  return () => clearInterval(interval);
}, []);
```

---

## 9️⃣ Testing the Integration

### Quick test in browser console:

```javascript
// Test 1: Simple query
fetch('https://mindmate-cognitive-api.onrender.com/doctor/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: 'Show me at-risk patients' })
})
.then(r => r.json())
.then(console.log);

// Test 2: Fast endpoint
fetch('https://mindmate-cognitive-api.onrender.com/doctor/at-risk?threshold=0.5')
.then(r => r.json())
.then(console.log);
```

---

## 🎯 Best Practices

1. **Show Loading States**: AI queries take 3-5 seconds
2. **Cache Results**: Cache responses for 1-2 minutes
3. **Use Fast Endpoints**: For dashboards that update frequently
4. **Markdown Rendering**: Use `react-markdown` or similar
5. **Error Boundaries**: Wrap in React error boundaries
6. **Timeout Handling**: Set 30s timeout for queries
7. **Retry Logic**: Implement exponential backoff for failures

---

## 📊 Performance Expectations

| Endpoint | Response Time | Use Case |
|----------|---------------|----------|
| `/doctor/query` | 3-5 seconds | Natural language queries with AI analysis |
| `/doctor/at-risk` | <1 second | Dashboard displays, quick checks |
| `/doctor/patient/{id}` | <1 second | Patient detail views |

---

## 🔐 Future: Authentication (Production-Ready)

When you add authentication:

```typescript
const response = await fetch(endpoint, {
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authToken}`  // Add when ready
  },
  // ...
});
```

---

## 📞 Support & Monitoring

- **Health Check**: `GET /health` - Check if API is online
- **Database Stats**: `GET /doctor/database-stats` - Verify data connection
- **Cache Stats**: `GET /cache/stats` - Monitor cache performance

---

**Built with ❤️ using FastAPI, Dedalus AI, and Supabase**
