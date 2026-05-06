# Pharma Call Recorder POC

**Version:** 0.4.0 - ABPI Compliance + Framework Validation  
**Status:** MVP Ready for Demo

FastAPI-based pharmaceutical sales call documentation system with AI-powered compliance checking and selling framework validation.

---

## 🎯 Key Features

### ✅ Core Functionality (Phase 1)
- **Natural conversation flow** with Claude Sonnet 4
- **Fuzzy doctor matching** (handles typos, partial names, multiple candidates)
- **Doctor disambiguation** from database (currently 20 doctors, expandable to 5000+)
- **JSON audit trail** with complete call metadata

### ⭐ NEW: ABPI Compliance + Framework Validation (Phase 2)
- **ABPI Code of Practice 2024** compliance checking (UK regulations)
- **Generic 6-Phase Selling Framework** validation
- **Hybrid checking:** Rules-based (fast keyword detection) + AI-powered (contextual analysis)
- **Multi-brand/multi-region architecture** (ready for EU, US expansion)
- **Automatic compliance blocking** (critical violations prevent finalization)

---

## 🚀 Quick Deploy to Replit

### Method 1: Import from GitHub (Easiest)
1. Go to https://replit.com
2. Click **"Import from GitHub"**
3. Paste: `https://github.com/pingou100/pharma-call-recorder`
4. Click **"Import"**
5. Add `ANTHROPIC_API_KEY` in Secrets (🔒 icon)
6. Click **Run ▶️**

### Method 2: Manual Upload
See `QUICK_START.md` for detailed instructions

**Deployment URL:** https://pharma-call-recorder.delannoyolivier.repl.co  
*(Auto-updates when you push to GitHub)*

---

## 📡 API Endpoints

### Core Endpoints
- `GET /health` - Service status + feature list
- `GET /doctors` - List all doctors in database
- `POST /search_doctors` - Fuzzy search doctors by name/specialty/hospital
- `POST /conversation` - Main conversation endpoint (doctor matching + call recording)

### NEW: Compliance Endpoints
- **`POST /check_abpi_compliance`** - Standalone ABPI + framework check
- **`POST /finalize`** - Finalize call with automatic compliance check (ENHANCED)

---

## 🔍 ABPI Compliance Checking (NEW)

### What Gets Checked

**ABPI Code 2024 Violations:**
- 🔴 **Critical:** Pre-marketing promotion, off-label promotion, gifts/inducements
- 🟠 **High Risk:** Unqualified safety claims, competitor disparagement, inappropriate hospitality
- 🟡 **Medium Risk:** Inappropriate audience, misuse of "new"

**Selling Framework Validation:**
- ✅ Purposeful Planning: Specific call objective documented?
- ✅ Uncovering Needs: HCP needs discovered?
- ✅ Call to Action: Voluntary & Active commitment secured? (action + timeline + agreement)

### How It Works

```
Call Data
    ↓
Phase 1: Quick Rules Scan (keyword detection)
    ↓
Phase 2: Framework Validation (6-phase structure)
    ↓
Phase 3: AI Deep Analysis (implicit violations + context)
    ↓
Merged Report (violations + gaps + recommendations)
```

### Example Request

```bash
curl -X POST http://localhost:5000/check_abpi_compliance \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "GenericProduct",
    "onekey_id": "BE-HCP-00001",
    "doctor": {"name": "Dr. Marie Dubois", "specialty": "Cardiology"},
    "call_objectives": ["Get Dr. Dubois to trial product with 5 HFrEF patients in 4 weeks"],
    "key_discussion_points": [
      "Dr. Dubois mentioned compliance issues with twice-daily dosing",
      "Discussed PROGRESS trial: 20% CV event reduction (p<0.001)",
      "Safety profile consistent with SPC"
    ],
    "agreements_reached": [
      "Trial with 5 HFrEF patients starting next week"
    ],
    "next_actions": ["Follow up in 2 weeks"]
  }'
```

### Example Response

```json
{
  "overall_assessment": "COMPLIANT",
  "risk_score": 15,
  "framework_score": 100,
  "abpi_violations": {
    "critical": [],
    "high_risk": [],
    "medium_risk": [],
    "warnings": []
  },
  "framework_issues": [],
  "strengths": [
    "Specific call objective with measurable outcome",
    "Voluntary & Active commitment secured with timeline",
    "Framework phases executed well: Purposeful Planning, Uncovering Needs, Call to Action"
  ],
  "recommended_actions": []
}
```

---

## 🛡️ Compliance Blocking Feature

### Automatic Finalization Block

When you call `/finalize`, the system automatically:
1. **Runs ABPI + framework check**
2. **Blocks finalization** if critical violations found
3. **Returns detailed violation report** with recommendations

**Example: Blocked Finalization**

```bash
# Call with violations
curl -X POST http://localhost:5000/finalize \
  -H "Content-Type: application/json" \
  -d '{
    "onekey_id": "BE-HCP-00001",
    "brand": "Product",
    "key_discussion_points": [
      "Product is the best in class with no side effects"  // ❌ ABPI violation
    ],
    "agreements_reached": ["Will think about it"]  // ❌ Framework gap
  }'

# Response: HTTP 400
{
  "error": "Cannot finalize: Critical violations detected",
  "compliance_result": {
    "overall_assessment": "CRITICAL_VIOLATIONS",
    "abpi_violations": {
      "high_risk": [{
        "clause": "6.4",
        "title": "Unqualified Safety Claims",
        "evidence": "no side effects"
      }]
    },
    "framework_issues": [{
      "phase": "Call to Action",
      "issue": "No Voluntary & Active commitment",
      "severity": "CRITICAL"
    }]
  },
  "recommended_actions": [
    "IMMEDIATE ESCALATION - Critical ABPI violations detected",
    "FRAMEWORK FAILURE - Missing V&A commitment"
  ]
}
```

---

## 🏗️ Architecture

### Current Stack
```
Frontend (PWA) → FastAPI Backend → Claude Sonnet 4 → ABPI Checker
                        ↓
                  Doctor Matcher (Fuzzy)
                        ↓
                  JSON Audit Trail
```

### Multi-Brand/Multi-Region Support

**Ready for Expansion:**
```python
# Current: UK ABPI only
compliance_result = check_compliance(call_data, region="UK")

# Future: Multi-region
compliance_result = check_compliance(call_data, region="EU")  # EU rules
compliance_result = check_compliance(call_data, region="US")  # FDA rules
```

**Brand-Specific Frameworks:**
```
frameworks/
├── Generic_Selling_Framework.md       # Current (applies to all brands)
├── CardioMax_Framework.md             # Future: brand-specific rules
├── DiabetesMax_Framework.md           # Future: different brand
```

---

## 📂 Project Structure

```
pharma-call-recorder/
├── main.py                              # FastAPI app with ABPI integration
├── abpi_compliance_checker.py           # Hybrid ABPI + framework checker
├── doctor_matcher.py                    # Fuzzy doctor search
├── doctors.json                         # Doctor database (20 samples)
├── compliance_rules/
│   └── abpi_rules.json                 # ABPI violation rules (11 rules)
├── frameworks/
│   └── Generic_Selling_Framework.md    # 6-phase selling methodology
├── compliance/
│   ├── ABPI_Compliance_Framework.md    # Full ABPI Code 2024 (79KB)
│   └── EU_Compliance_Guidelines.md     # EU regulations
├── static/
│   └── index.html                      # Frontend (PWA)
└── requirements.txt                     # Python dependencies
```

---

## 🧪 Testing

### Test Compliant Call
```bash
curl -X POST http://localhost:5000/finalize \
  -H "Content-Type: application/json" \
  -d @test_data/compliant_call.json
```

### Test Non-Compliant Call
```bash
curl -X POST http://localhost:5000/check_abpi_compliance \
  -H "Content-Type: application/json" \
  -d @test_data/violation_call.json
```

---

## 📋 Roadmap

### ✅ Completed (Phase 1-2)
- [x] Natural conversation flow
- [x] Fuzzy doctor matching
- [x] ABPI compliance checking (UK)
- [x] Selling framework validation (6-phase)
- [x] Multi-brand/multi-region architecture
- [x] Automatic compliance blocking

### 🔄 Next Phase
- [ ] Frontend PWA with voice interface
- [ ] Multi-region expansion (EU, US)
- [ ] Brand-specific frameworks
- [ ] CRM integration (Salesforce/Veeva)
- [ ] Pilot with 10-100 reps

---

## 📚 Documentation

- **QUICK_START.md** - 5-minute deployment guide
- **ABPI_INTEGRATION_PLAN.md** - Detailed Phase 2 implementation plan
- **README.md** - This file (project overview)

---

## 🔧 Configuration

### Environment Variables
```bash
ANTHROPIC_API_KEY=your-api-key-here  # Required
```

### Supported Regions (MVP)
- **UK** - ABPI Code of Practice 2024 ✅
- EU - Coming soon
- US (FDA) - Coming soon

---

## 📝 License

MIT

---

## 🚨 Important Notes

### For Stakeholder Demos
- **ABPI checking is automatic** - No manual intervention needed
- **Critical violations block finalization** - Ensures regulatory compliance
- **Complete audit trail** - Every call includes compliance scores

### For Production Deployment
- Move to Azure OpenAI (EU) for data residency
- Implement CRM write with rep confirmation
- Add complete audit logging for regulatory inspection
- Scale doctor database to 5000+ records per rep

---

**Live Demo:** https://pharma-call-recorder.delannoyolivier.repl.co  
**GitHub:** https://github.com/pingou100/pharma-call-recorder
