# 🔧 Pharma Call Recorder - Critical Gaps Remediation Plan

**Date Created:** May 5, 2026  
**Status:** Ready for Implementation  
**Total Effort:** 12-18 hours across 3 parallelizable tracks  

---

## Overview

Three gaps identified that should be addressed before pilot phase (week 2-3):

1. **Doctor Database Scale** — 20 → 5000 records (2-4 hrs)
2. **Compliance Module Integration** — Enforce EU guidelines (4-6 hrs)
3. **Brand Framework Integration** — Add selling methodology (6-8 hrs)

This document provides step-by-step remediation for each.

---

## Gap 1: Scale Doctor Database to 5000 Records

**Timeline:** 2-4 hours  
**Priority:** HIGH (blocks pilot scaling)  
**Owner:** Data team or backend dev  

### Problem
Current: 20 hardcoded Belgian HCPs  
Needed: 5000+ records for realistic matching

### Solution: Generate Seed Data

```python
# generate_doctors.py
import json
import random

HOSPITALS = [
    "CHU Charleroi", "CHU Brugmann", "AZ Sint-Jan", "Clinique Saint-Luc",
    "Hôpital Erasme", "CHR Liège", "AZ Groeninge", "UZ Leuven",
    "UZ Gent", "AZ Delta", "Sint-Camillus", "Chirec"
]

CITIES = ["Brussels", "Charleroi", "Bruges", "Liège", "Antwerp", "Ghent", "Leuven",
          "Tournai", "Mons", "Namur", "Waterloo", "Ostend"]

SPECIALTIES = ["Cardiology", "Oncology", "Neurology", "Rheumatology",
               "Gastroenterology", "Endocrinology", "Dermatology"]

FIRST_NAMES = ["Marie", "Jean", "Sophie", "Pierre", "Emma", "Marc", "Anne"]
LAST_NAMES = ["Dubois", "Martin", "Laurent", "Vandenberg", "Lefèvre"]

def generate_doctors(count=5000):
    doctors = []
    for i in range(1, count + 1):
        doctor = {
            "onekey_id": f"BE-HCP-{i:05d}",
            "first_name": random.choice(FIRST_NAMES),
            "last_name": random.choice(LAST_NAMES),
            "specialty": random.choice(SPECIALTIES),
            "hospital": random.choice(HOSPITALS),
            "city": random.choice(CITIES)
        }
        doctors.append(doctor)
    return doctors

if __name__ == "__main__":
    doctors = generate_doctors(5000)
    with open("doctors.json", "w") as f:
        json.dump(doctors, f, indent=2)
    print(f"✅ Generated {len(doctors)} doctors")
```

### Test Performance

```bash
python generate_doctors.py
python test_fuzzy_performance.py  # Verify <50ms per query
```

### Acceptance Criteria
- ✅ doctors.json has 5000 unique records
- ✅ Fuzzy search returns results in <100ms
- ✅ Batch search (100 queries) averages <50ms
- ✅ /conversation endpoint handles 5000 records

---

## Gap 2: Integrate Compliance Module

**Timeline:** 4-6 hours  
**Priority:** MEDIUM (required before pilot)  
**Owner:** Backend developer  

### Problem
File exists: compliance_checker.py  
Not used: Not imported or called in main.py  
Needed: Real-time enforcement

### Solution: Integrate into FastAPI

Update main.py /conversation endpoint:

```python
from compliance_checker import ComplianceChecker

compliancer = ComplianceChecker()

@app.post("/conversation")
async def conversation(request):
    # ... existing code ...
    
    # NEW: Run compliance check
    compliance_result = compliant.audit_call(
        request.message + " " + assistant_message,
        extracted_data
    )
    
    return ConversationResponse(
        assistant_message=assistant_message,
        compliance_status=compliance_result  # NEW FIELD
    )
```

### Test Cases
- ✅ Compliant: Trial-backed claims pass
- ✅ Violation: Unsubstantiated claims flagged
- ✅ Violation: Medical advice detected
- ✅ Violation: Off-label use prevented

### Acceptance Criteria
- ✅ ComplianceChecker integrated into /conversation
- ✅ Real-time checks on each message
- ✅ Violations logged with rule_id
- ✅ Response includes compliance_status field

---

## Gap 3: Integrate Brand Frameworks

**Timeline:** 6-8 hours  
**Priority:** MEDIUM (required before pilot)  
**Owner:** Backend developer + product team  

### Problem
File exists: CardioMax_Selling_Framework.md  
Not used: Not parsed or available to Claude  
Needed: AI-powered coaching through 6 phases

### Solution: Parse to JSON & Integrate

```python
# frameworks.json
{
  "CardioMax": {
    "phases": [
      {
        "number": 1,
        "name": "Purposeful Planning",
        "duration_min": 5,
        "focus": "Define specific objective"
      },
      {
        "number": 2,
        "name": "Bold Opening",
        "duration_min": 3,
        "focus": "Build trust"
      },
      {
        "number": 3,
        "name": "Uncovering Needs",
        "duration_min": 8,
        "focus": "Ask questions, listen 70%"
      },
      {
        "number": 4,
        "name": "Tailored Solutions",
        "duration_min": 8,
        "focus": "Connect benefits to needs"
      },
      {
        "number": 5,
        "name": "Handling Objections",
        "duration_min": 4,
        "focus": "Understand root cause"
      },
      {
        "number": 6,
        "name": "Call to Action",
        "duration_min": 5,
        "focus": "Secure commitment"
      }
    ]
  }
}
```

Update main.py:
```python
from framework_coach import FrameworkCoach

coach = FrameworkCoach()

@app.post("/conversation")
async def conversation(request):
    # ... existing code ...
    
    # NEW: Detect phase and get guidance
    current_phase = coach.detect_phase(conversationHistory, extracted_data)
    
    return ConversationResponse(
        assistant_message=assistant_message,
        current_phase=current_phase,  # NEW FIELD
        coaching_guidance=coach.get_phase_guidance(brand, current_phase)  # NEW
    )
```

### Test Cases
- ✅ Phase detection: Turn 1 = Opening, Turn 5 = Solutions, etc.
- ✅ Guidance: Each phase has actionable coaching
- ✅ Claude integration: System prompt includes framework

### Acceptance Criteria
- ✅ frameworks.json parses 6-phase structure
- ✅ FrameworkCoach detects current phase
- ✅ /conversation returns current_phase and coaching_guidance
- ✅ Phase progression follows 6-phase methodology

---

## Implementation Timeline

### Week 2 (Parallelizable)

**Day 1-2: Gap 1 (Doctor scaling)**
- Generate 5000 doctors
- Test fuzzy matching performance
- Validate data

**Day 2-3: Gap 2 (Compliance)**
- Integrate compliance_checker.py into main.py
- Add compliance_status to response
- Test with 5+ compliance scenarios

**Day 3-4: Gap 3 (Frameworks)**
- Parse CardioMax framework to JSON
- Implement FrameworkCoach
- Update Claude system prompt
- Test phase detection

**Day 5: Integration**
- Test all 3 gaps together
- Run end-to-end call simulation
- Verify no regressions

---

## Success Metrics

| Metric | Target | How to Validate |
|--------|--------|----------------|
| Doctor search | <50ms/query | Run performance test |
| Compliance accuracy | 90%+ detection | Test 20 scenarios |
| Phase detection | 95%+ accuracy | Test 30 call simulations |
| Integration | Zero errors | Run full call flow |

---

Detailed code templates available in full REMEDIATION_PLAN.md
