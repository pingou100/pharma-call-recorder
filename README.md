# Pharma Call Recorder POC

## v0.4.0 - Active ABPI & Framework Coaching

### Features
- ✅ Real-time ABPI compliance monitoring
- ✅ 6-phase selling framework coaching
- ✅ Voice input with speech-to-text
- ✅ Doctor disambiguation
- ✅ Post-call compliance validation

### Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 3. Start backend
python3 main.py

# 4. Open frontend
open index.html
```

### Architecture
- **Backend:** FastAPI + Claude Sonnet 4
- **Frontend:** Vanilla JS with Web Speech API
- **Database:** JSON file (POC only)

### Active Coaching
The assistant now provides:
- **Real-time ABPI violation detection** with compliant alternatives
- **Framework phase prompting** for complete call structure
- **V&A commitment checking** to ensure quality outcomes

### Test It
1. Start recording
2. Say: "CardioMax is the best with no side effects"
3. Assistant will immediately flag ABPI violations and suggest compliant phrasing

### Project Structure
```
├── main.py                          # FastAPI backend with enhanced coaching
├── index.html                       # Voice UI frontend
├── compliance/
│   ├── abpi_critical_rules.json     # 6 critical ABPI violations
│   └── ABPI_Compliance_Framework.md # Full framework
├── frameworks/
│   ├── framework_coaching_guide.md  # 6-phase coaching
│   └── CardioMax_Selling_Framework.md
└── doctors.json                     # Doctor database
```

### Version History
- **v0.4.0** - Active coaching with real-time ABPI + framework
- **v0.3.0** - Voice UI
- **v0.2.0** - Doctor matching
- **v0.1.0** - Initial POC