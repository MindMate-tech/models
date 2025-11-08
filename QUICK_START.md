# MindMate - Quick Start Guide

## 🎯 Goal
Get your complete system working end-to-end in 30 minutes.

---

## 📊 Where Everything Lives

| Component | Repository | Status | Deploy To |
|-----------|------------|--------|-----------|
| **Cognitive API** | `models` | ✅ Ready | **Render** ← DO THIS FIRST |
| **Main Backend** | `backend` | ⚠️ Needs update | Railway/Render/Fly.io |
| **Doctor Dashboard** | `doctor-frontend` | ? | Vercel/Netlify |
| **Patient App** | `stellar-mind-companion` | ? | Vercel/Netlify |

---

## ⚡ 30-Minute Setup

### **STEP 1: Deploy Cognitive API (5 min)** 🚀

Your cognitive analysis code is already pushed to GitHub. Now deploy it:

1. **Open:** https://dashboard.render.com
2. **Sign in** with GitHub
3. **Click:** "New +" → "Blueprint"
4. **Select:** `MindMate-tech/models` repository
5. **Add Environment Variables:**
   ```
   DEDALUS_API_KEY = dsk_live_e6adeae3ea9a_4aaaa9f9bca6165a640b92e6af9b2026
   ANTHROPIC_API_KEY = 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
   ```
6. **Click:** "Apply"
7. **Wait** 5-10 minutes for build
8. **Copy URL:** `https://mindmate-cognitive-api-xxxxx.onrender.com`

**Test it:**
```bash
curl https://your-url.onrender.com/health
```

Should return:
```json
{
  "status": "healthy",
  "dedalus": true,
  "anthropic": true
}
```

---

### **STEP 2: Update Backend Code (10 min)** 💻

Update your `backend` repository to call the Cognitive API:

1. **Create new file:** `NewMindmate/services/cognitive_api_client.py`
   - Copy from: `INTEGRATION_FILES_FOR_BACKEND/cognitive_api_client.py`
   - **Update line 12:** Replace with your Render URL from Step 1

2. **Replace file:** `NewMindmate/routes/sessions.py`
   - Copy from: `INTEGRATION_FILES_FOR_BACKEND/updated_sessions_routes.py`

3. **Add to requirements:**
   ```bash
   cd /home/lucas/mindmate-backend
   echo "httpx==0.28.1" >> requirements.txt
   ```

4. **Commit and push:**
   ```bash
   git add .
   git commit -m "Integrate cognitive analysis API"
   git push origin main
   ```

---

### **STEP 3: Deploy Backend (10 min)** 🚀

**Option A: Render (Easiest)**

1. Create `render.yaml` in backend repo:
```yaml
services:
  - type: web
    name: mindmate-backend
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn NewMindmate.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: SUPABASE_URL
        value: your-supabase-url
      - key: SUPABASE_KEY
        value: your-supabase-key
      - key: PORT
        value: 8000
```

2. Push to GitHub
3. Deploy to Render (same process as Step 1)

**Option B: Railway**
```bash
cd /home/lucas/mindmate-backend/NewMindmate
railway init
railway up
```

**Get your backend URL:** `https://mindmate-backend.onrender.com` (or Railway URL)

---

### **STEP 4: Test Integration (5 min)** ✅

Test the complete flow:

```bash
# 1. Create a patient
curl -X POST https://your-backend-url.com/patients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Patient",
    "dob": "1955-01-01"
  }'

# 2. Create a session
curl -X POST https://your-backend-url.com/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "YOUR_PATIENT_ID",
    "transcript": "Patient discussed their family and memories of childhood."
  }'

# 3. Trigger AI analysis (calls Cognitive API)
curl -X POST https://your-backend-url.com/sessions/analyze/YOUR_SESSION_ID

# Wait 60 seconds, then check:

# 4. Get dashboard (uses Cognitive API)
curl https://your-backend-url.com/sessions/patient/YOUR_PATIENT_ID/dashboard
```

If you get brain regions, memory metrics, and session data → **SUCCESS!** 🎉

---

### **STEP 5: Connect Frontends (Optional)** 🌐

Update frontend environment variables:

**Doctor Dashboard (.env):**
```
REACT_APP_API_URL=https://your-backend-url.com
```

**Patient Companion (.env):**
```
REACT_APP_API_URL=https://your-backend-url.com
REACT_APP_LIVEKIT_URL=your-livekit-url
```

Deploy to Vercel:
```bash
cd doctor-frontend
vercel deploy

cd stellar-mind-companion
vercel deploy
```

---

## 🔍 How It Works

### Complete Data Flow:

```
1. PATIENT HAS VIDEO CALL
   stellar-mind-companion → LiveKit → Transcript

2. CREATE SESSION
   POST /sessions
   {patient_id, transcript} → Supabase

3. TRIGGER AI ANALYSIS
   POST /sessions/analyze/{id}
   ↓
   Backend calls Cognitive API:
   POST https://cognitive-api.onrender.com/analyze/session
   ↓
   Returns: memories, scores, metrics, alerts
   ↓
   Store in Supabase + ChromaDB

4. DOCTOR VIEWS DASHBOARD
   GET /sessions/patient/{id}/dashboard
   ↓
   Backend calls Cognitive API:
   POST https://cognitive-api.onrender.com/patient/dashboard
   ↓
   Returns: PatientData format (brain regions, metrics, sessions)
   ↓
   Frontend displays charts
```

---

## 🐛 Troubleshooting

### "Cognitive API timeout"
- Analysis takes 60-120 seconds
- Normal for first call (cold start on Render free tier)

### "Module not found: cognitive_api_client"
- Make sure file is in `NewMindmate/services/`
- Check import path in `sessions.py`

### "Backend can't reach Cognitive API"
- Verify COGNITIVE_API_URL is correct
- Test: `curl https://your-cognitive-api.onrender.com/health`

### "Frontend gets 404"
- Check backend is deployed and running
- Verify API_URL in frontend .env

---

## 📁 File Locations

**Your machine:**
```
/home/lucas/mindmate-demo/           # Cognitive API (models repo)
/home/lucas/mindmate-backend/        # Main backend
```

**GitHub:**
```
https://github.com/MindMate-tech/models            # Cognitive API
https://github.com/MindMate-tech/backend           # Main backend
https://github.com/MindMate-tech/doctor-frontend   # Doctor dashboard
https://github.com/MindMate-tech/stellar-mind-companion  # Patient app
```

**Deployed:**
```
https://mindmate-cognitive-api.onrender.com   # Cognitive API
https://mindmate-backend.onrender.com         # Backend (you deploy)
https://doctor-dashboard.vercel.app           # Frontend (you deploy)
https://patient-app.vercel.app                # Patient app (you deploy)
```

---

## ✅ Checklist

- [ ] Deploy Cognitive API to Render
- [ ] Get Render URL
- [ ] Update backend code with integration files
- [ ] Update COGNITIVE_API_URL in cognitive_api_client.py
- [ ] Deploy backend to Render/Railway
- [ ] Test health endpoints
- [ ] Test complete flow (create patient → session → analyze → dashboard)
- [ ] Update frontend environment variables
- [ ] Deploy frontends
- [ ] Test end-to-end from UI

---

## 🎯 Next Steps After Setup

1. **Monitor logs** in Render dashboard
2. **Test with real video calls** from patient app
3. **Optimize performance** (upgrade Render plan if needed)
4. **Add authentication** to APIs
5. **Set up monitoring** (Sentry, Datadog, etc.)

---

## 🆘 Need Help?

Check these files:
- `FULL_SYSTEM_INTEGRATION.md` - Complete architecture
- `DEPLOYMENT.md` - Detailed deployment guide
- `INTEGRATION_EXAMPLE.py` - Code examples

**You're ready to deploy!** 🚀

Start with Step 1 (Deploy Cognitive API) and work through each step.
