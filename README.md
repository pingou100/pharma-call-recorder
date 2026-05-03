# Pharma Call Recorder POC - Backend

Minimal FastAPI prototype for pharmaceutical sales call documentation with AI-powered fuzzy doctor matching.

## Features

- Natural conversation flow with Claude Sonnet 4
- Fuzzy doctor matching (handles typos, partial names)
- Doctor disambiguation from 20-doctor database (expandable to 5000+)
- JSON output with complete audit trail
- CORS-enabled for frontend integration

## Quick Deploy to Replit

### Method 1: Import from GitHub (Easiest)
1. Go to https://replit.com
2. Click "Import from GitHub"
3. Paste: `https://github.com/pingou100/pharma-call-recorder`
4. Click "Import"
5. Add ANTHROPIC_API_KEY in Secrets (🔒 icon)
6. Click Run ▶️

### Method 2: Manual Upload
See QUICK_START.md for detailed instructions

## API Endpoints

- `GET /` - Health check
- `GET /doctors` - List all doctors
- `POST /search_doctors` - Fuzzy search doctors
- `POST /conversation` - Record call conversation
- `POST /finalize` - Finalize call record

## Documentation

- **QUICK_START.md** - 5-minute deployment guide
- **README.md** - This file (project overview)

## Architecture

```
FastAPI Backend → Claude Sonnet 4 → Fuzzy Doctor Matching → JSON Output
```

## Next Steps

1. ✅ Deploy to Replit
2. 🔄 Demo with stakeholders
3. 🔄 Add compliance checking
4. 🔄 Build PWA frontend
5. 🔄 Pilot with 10-100 reps

## License

MIT