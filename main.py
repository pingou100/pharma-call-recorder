# main.py - Pharma Call Recorder with Active ABPI + Framework Coaching

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import anthropic
import httpx
import os
import json
from datetime import datetime
import traceback
from dotenv import load_dotenv
from doctor_matcher import DoctorMatcher, load_doctors
from ai_compliance_checker import AIComplianceChecker, AIBrandFramework

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Pharma Call Recorder POC")

# CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load doctors database and initialize matcher
DOCTORS = load_doctors("doctors.json")
doctor_matcher = DoctorMatcher(DOCTORS)

# Initialize AI compliance checker (will be connected to Anthropic client on startup)
ai_checker = None

# ============================================================================
# ENHANCED COACHING SYSTEM - Week 1 Implementation
# ============================================================================

def load_abpi_critical_rules():
    """Load ABPI critical violation rules"""
    try:
        with open("compliance/abpi_critical_rules.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARNING] Could not load ABPI rules: {e}")
        return {"critical_violations": [], "coaching_instructions": ""}

def load_framework_coaching():
    """Load selling framework coaching guide"""
    try:
        with open("frameworks/framework_coaching_guide.md", "r") as f:
            return f.read()
    except Exception as e:
        print(f"[WARNING] Could not load framework guide: {e}")
        return ""

def build_enhanced_system_prompt():
    """Build comprehensive system prompt with ABPI + Framework coaching"""
    
    abpi_rules = load_abpi_critical_rules()
    framework_guide = load_framework_coaching()
    
    # Extract critical violations for quick reference
    critical_violations_text = ""
    for v in abpi_rules.get('critical_violations', []):
        if v['severity'] in ['CRITICAL', 'HIGH']:
            keywords_str = ', '.join(f'"{kw}"' for kw in v['keywords'][:3])
            critical_violations_text += f"""
**{v['title']}** (Severity: {v['severity']})
- Watch for: {keywords_str}
- Response: {v['response']}
"""
    
    prompt = f"""You are an AI coach helping pharmaceutical sales representatives conduct compliant, effective doctor visits.

## YOUR TWO ROLES

### ROLE 1: ABPI COMPLIANCE GUARDIAN (Real-Time Monitoring)

You actively MONITOR every statement the rep makes and INTERVENE immediately when you detect violations.

**CRITICAL VIOLATIONS TO WATCH:**
{critical_violations_text}

**Your Response Pattern:**
When you detect a violation:
1. ⚠️ Flag it IMMEDIATELY with "COMPLIANCE ALERT: [violation type]"
2. Explain why it's a problem (cite ABPI clause)
3. Suggest compliant alternative phrasing with specific data
4. Ask if rep wants to revise the statement

**Example:**
Rep: "CardioMax is the best treatment with no side effects"
You: "⚠️ COMPLIANCE ALERT: Two violations detected:
- 'best treatment' = unsubstantiated superlative (ABPI 6.4) - requires robust evidence
- 'no side effects' = unqualified safety claim (ABPI 6.4) - no medicine is risk-free

Consider: 'CardioMax showed 20% reduction in CV events vs placebo in PROGRESS trial, with 4.2% hyperkalemia incidence vs 7.8% competitor average.'

Would you like me to record the revised statement?"

**Severity Levels:**
🛑 CRITICAL (refuse to record): Off-label, gifts/inducements, pre-marketing
⚠️ HIGH (flag + require fix): Unqualified claims, superlatives
💡 MEDIUM (suggest improvement): Vague statements, missing data

---

### ROLE 2: SELLING FRAMEWORK COACH (Proactive Guidance)

{framework_guide}

---

## CONVERSATION FLOW

1. **Opening:** "What's your specific goal for this visit?" (Phase 1: Purposeful Planning)
2. **During Call:** 
   - Monitor EVERY statement for ABPI violations
   - Track framework phases completion
   - Prompt for missing elements
3. **Near End:** 
   - Check if Voluntary & Active commitment secured (Phase 5 - CRITICAL)
   - Ensure follow-up scheduled (Phase 6)
4. **Before Finalize:** Confirm all phases complete, especially V&A commitment

---

## RESPONSE FORMAT

For EACH rep message, respond in this structured order:

1. **🛡️ COMPLIANCE CHECK** (Priority 1): 
   - Any ABPI violations detected? → Address IMMEDIATELY before anything else
   
2. **📋 FRAMEWORK CHECK** (Priority 2):
   - Which phase is rep currently in?
   - Any phases missing? → Prompt gently
   
3. **💾 DATA EXTRACTION** (Priority 3):
   - Record call details in JSON format
   
4. **➡️ NEXT GUIDANCE** (Priority 4):
   - What should rep do next? Guide them forward

---

## CRITICAL RULES

1. **NEVER ignore ABPI violations** - Flag immediately, every time
2. **ALWAYS check for V&A commitment** - Most calls lack this critical element
3. **COACH in real-time** - Don't wait until call ends
4. **BE HELPFUL, not punitive** - Use "Consider" not "You violated"
5. **REINFORCE good behavior** - "Excellent ABPI-compliant phrasing!"

---

## DOCTOR IDENTIFICATION RULES (Keep Existing)

NEVER assume which doctor the rep visited - ALWAYS ask for confirmation:
1. When rep mentions a doctor, search database and present ALL matching candidates
2. Rep MUST explicitly confirm before proceeding
3. If multiple matches, present ALL options with specialty, hospital, city
4. Never proceed without explicit confirmation

Example:
Rep: "Just visited Dr. Dubois"
You: "I found 2 doctors named Dubois:
1. Dr. Marie Dubois - Cardiology, CHU Charleroi
2. Dr. Olivier Dubois - Cardiology, AZ Sint-Jan
Which one?"

When doctor confirmed, continue with framework coaching.

---

Your goal: Help reps conduct **compliant, effective, well-structured** conversations that benefit patients.
"""
    
    return prompt

# ============================================================================
# END ENHANCED COACHING SYSTEM
# ============================================================================

# Request/Response models
class ConversationRequest(BaseModel):
    message: str
    conversation_history: Optional[List[dict]] = []
    confirmed_onekey_id: Optional[str] = None

class ConversationResponse(BaseModel):
    assistant_message: str
    extracted_data: Optional[dict] = None
    doctor_candidates: Optional[List[dict]] = None
    needs_doctor_confirmation: bool = False
    is_complete: bool = False

# Build enhanced system prompt with coaching
SYSTEM_PROMPT = build_enhanced_system_prompt()

# Create Anthropic client once at startup
def create_anthropic_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not configured")
    
    http_client = httpx.Client(timeout=60.0)
    return anthropic.Anthropic(api_key=api_key, http_client=http_client)

try:
    anthropic_client = create_anthropic_client()
    print("✅ Anthropic client initialized successfully")
    print(f"✅ Loaded {len(DOCTORS)} doctors from database")
    
    # Initialize AI compliance checker with the same client
    ai_checker = AIComplianceChecker(anthropic_client=anthropic_client)
    print("✅ AI compliance checker initialized")
    
    # Verify coaching resources loaded
    test_rules = load_abpi_critical_rules()
    test_framework = load_framework_coaching()
    if test_rules.get('critical_violations'):
        print(f"✅ Loaded {len(test_rules['critical_violations'])} ABPI rules")
    if test_framework:
        print(f"✅ Loaded framework coaching guide ({len(test_framework)} chars)")
except Exception as e:
    print(f"❌ Failed to initialize: {e}")
    anthropic_client = None
    ai_checker = None

@app.get("/")
async def root():
    return {
        "service": "Pharma Call Recorder POC",
        "status": "running",
        "version": "0.4.0 - Enhanced Active Coaching",
        "doctors_loaded": len(DOCTORS),
        "anthropic_client": "ready" if anthropic_client else "not configured",
        "ai_checker": "ready" if ai_checker else "not configured",
        "features": [
            "Real-time ABPI compliance coaching",
            "6-phase selling framework guidance",
            "Fuzzy doctor matching",
            "Post-call compliance validation"
        ]
    }

@app.get("/doctors")
async def list_doctors():
    """Return all doctors in database"""
    return {"doctors": DOCTORS, "count": len(DOCTORS)}

@app.post("/search_doctors")
async def search_doctors(
    query: str = None,
    first_name: str = None,
    last_name: str = None,
    specialty: str = None,
    hospital: str = None,
    city: str = None,
    min_confidence: float = 60.0
):
    """Search for doctors using fuzzy matching"""
    results = doctor_matcher.match(
        query=query,
        first_name=first_name,
        last_name=last_name,
        specialty=specialty,
        hospital=hospital,
        city=city,
        min_confidence=min_confidence
    )
    
    return {
        "matches": results,
        "count": len(results)
    }

@app.post("/conversation", response_model=ConversationResponse)
async def conversation(request: ConversationRequest):
    """Main conversation endpoint with active coaching"""
    
    if not anthropic_client:
        raise HTTPException(status_code=500, detail="Anthropic client not initialized")
    
    try:
        # Build messages array
        messages = request.conversation_history.copy()
        
        # Add doctor database context
        context_parts = [request.message]
        
        # If rep confirmed a doctor, add that context
        if request.confirmed_onekey_id:
            confirmed_doctor = doctor_matcher.get_by_onekey_id(request.confirmed_onekey_id)
            if confirmed_doctor:
                context_parts.append(f"\n[SYSTEM: Rep confirmed doctor: {confirmed_doctor['full_name']} ({confirmed_doctor['onekey_id']}) - {confirmed_doctor['specialty']}, {confirmed_doctor['hospital']}]")
        
        messages.append({
            "role": "user",
            "content": "\n".join(context_parts)
        })
        
        # Call Claude API with enhanced coaching prompt
        print(f"\n[DEBUG] Calling Claude API with {len(messages)} messages")
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=messages
        )
        
        print(f"[DEBUG] Response received: {response.stop_reason}")
        
        # Extract text from response
        assistant_message = ""
        for block in response.content:
            if block.type == "text":
                assistant_message += block.text
        
        if not assistant_message:
            raise ValueError("No text content in Claude response")
        
        # Parse extracted data
        extracted_data = None
        doctor_candidates = None
        needs_confirmation = False
        is_complete = False
        
        # Look for JSON block
        if "```json" in assistant_message:
            try:
                json_start = assistant_message.find("```json") + 7
                json_end = assistant_message.find("```", json_start)
                json_str = assistant_message[json_start:json_end].strip()
                extracted_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"[DEBUG] JSON parse error: {e}")
        
        # Look for doctor candidates
        if "DOCTOR_CANDIDATES:" in assistant_message:
            candidate_line = assistant_message.split("DOCTOR_CANDIDATES:")[1].split("\n")[0]
            onekey_ids = [id.strip() for id in candidate_line.strip("[] ").split(",")]
            
            doctor_candidates = []
            for onekey_id in onekey_ids:
                doctor = doctor_matcher.get_by_onekey_id(onekey_id)
                if doctor:
                    doctor_candidates.append(doctor)
            
            needs_confirmation = len(doctor_candidates) > 0
        
        # Alternatively, use doctor info from extracted data to search
        if extracted_data and extracted_data.get("doctor_info") and not doctor_candidates:
            doctor_info = extracted_data["doctor_info"]
            
            matches = doctor_matcher.match(
                first_name=doctor_info.get("mentioned_first_name"),
                last_name=doctor_info.get("mentioned_name"),
                hospital=doctor_info.get("mentioned_hospital"),
                city=doctor_info.get("mentioned_city"),
                min_confidence=60.0
            )
            
            if matches:
                doctor_candidates = matches
                needs_confirmation = True
        
        # Check if complete
        if extracted_data:
            has_brand = bool(extracted_data.get("brand"))
            has_doctor = bool(extracted_data.get("doctor_info", {}).get("confirmed_onekey_id"))
            has_call_data = bool(extracted_data.get("call_objectives") or extracted_data.get("key_discussion_points"))
            
            is_complete = has_brand and has_doctor and has_call_data
        
        return ConversationResponse(
            assistant_message=assistant_message,
            extracted_data=extracted_data,
            doctor_candidates=doctor_candidates,
            needs_doctor_confirmation=needs_confirmation,
            is_complete=is_complete
        )
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        print(f"[ERROR] Full traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/check_abpi_compliance")
async def check_abpi_compliance(call_data: dict):
    """Check call data against ABPI Code of Practice 2024 + Selling Framework"""
    
    if not ai_checker:
        raise HTTPException(
            status_code=500, 
            detail="AI compliance checker not initialized"
        )
    
    try:
        result = ai_checker.check_compliance(
            call_data=call_data,
            region="UK",
            brand=call_data.get("brand")
        )
        
        return result
        
    except Exception as e:
        print(f"[ERROR] ABPI check failed: {str(e)}")
        print(f"[ERROR] Full traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"ABPI compliance check failed: {str(e)}"
        )

@app.post("/finalize")
async def finalize_call(call_data: dict):
    """Finalize and save call record"""
    
    if not call_data.get("onekey_id"):
        raise HTTPException(status_code=400, detail="onekey_id is required for finalization")
    
    doctor = doctor_matcher.get_by_onekey_id(call_data["onekey_id"])
    if not doctor:
        raise HTTPException(status_code=400, detail=f"Invalid onekey_id: {call_data['onekey_id']}")
    
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "call_data": call_data,
        "doctor": doctor,
        "audit_trail": {
            "created_at": datetime.utcnow().isoformat(),
            "source": "voice_recording",
            "version": "POC-0.4.0",
            "onekey_id": call_data["onekey_id"]
        }
    }
    
    print("\n" + "="*60)
    print("FINALIZED CALL RECORD")
    print("="*60)
    print(json.dumps(record, indent=2))
    print("="*60 + "\n")
    
    return {
        "status": "success",
        "message": "Call record saved (POC: printed to console)",
        "record_id": f"CALL-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
        "onekey_id": call_data["onekey_id"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
