# Quick Start Guide - Deploy in 5 Minutes

## Import from GitHub to Replit

### Step 1: Go to Replit (30 seconds)
1. Visit https://replit.com
2. Sign up or log in (free account)

### Step 2: Import Repository (1 minute)
1. Click **"Import from GitHub"** or **"Create"** → **"Import from GitHub"**
2. Paste this URL:
   ```
   https://github.com/pingou100/pharma-call-recorder
   ```
3. Click **"Import"**
4. Wait ~20 seconds for import to complete

### Step 3: Add API Key (1 minute)
1. Click 🔒 **"Secrets"** in left sidebar
2. Add new secret:
   - Key: `ANTHROPIC_API_KEY`
   - Value: `sk-ant-api03-xxxxx` (your actual Anthropic API key)
3. Click **"Add new secret"**

### Step 4: Run (30 seconds)
1. Click the green ▶️ **"Run"** button at top
2. Wait ~30 seconds for dependencies to install
3. Look for: ✅ `Anthropic client initialized successfully`
4. Look for: ✅ `Loaded 20 doctors from database`

### Done! 🎉

Your API is now live at:
```
https://pharma-call-recorder.your-username.repl.co
```

## Test Your Deployment

Open Replit Shell and test:

```bash
# Health check
curl http://localhost:8000/

# View doctors
curl http://localhost:8000/doctors

# Search doctors
curl "http://localhost:8000/search_doctors?query=Dubois%20Charleroi"
```

## Share with Stakeholders

Send them this URL:
```
https://pharma-call-recorder.your-username.repl.co/docs
```

This gives them an interactive API playground (Swagger UI) to test all endpoints.

## Troubleshooting

### "ANTHROPIC_API_KEY not configured"
- Add the key in Secrets (🔒 icon)
- Restart the Repl

### "doctors.json not found"
- The file should auto-import from GitHub
- If missing, manually upload doctors.json

### Import failed
- Try manual upload method instead
- See full DEPLOYMENT_CHECKLIST.md

## Next Steps

✅ Backend deployed
🔄 Test with stakeholders
🔄 Enable "Always On" ($20/month) for demos
🔄 Add compliance checking
🔄 Build frontend
