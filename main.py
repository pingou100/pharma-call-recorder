# main.py - Pharma Call Recorder with Active ABPI + Framework Coaching

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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
        if v['severity'] in ['CRITICAL', 'HIGH', 'MEDIUM']:
            keywords_str = ', '.join(f'"{kw}"' for kw in v['keywords'][:3])
            critical_violations_text += f"""
**{v['title']}** (Severity: {v['severity']})
- Watch for: {keywords_str}
- Response: {v['response']}
"""
    
    prompt = f"""You are an AI assistant helping pharmaceutical sales representatives document calls that already happened.

## YOUR TWO ROLES

### ROLE 1: COMPLIANCE MONITOR (Brief & Conversational)

You monitor for ABPI violations and provide brief, helpful feedback when detected.

**CRITICAL VIOLATIONS TO WATCH:**
{critical_violations_text}

**Your Response Style:**
- NEVER mention "asterisk", "asterisks", or markdown formatting symbols in your spoken responses
- When you see ** in text, understand it as emphasis but don't read it out loud
- Be BRIEF and conversational (one sentence)
- DON'T use emoticons, warnings symbols, or "ALERT" language
- DON'T mention ABPI clause numbers or asterisks
- DON'T say "critical violation" or use dramatic language
- Just state the issue plainly and suggest an alternative

**Good Examples:**
❌ Rep: "Our product is the best with no side effects"
✅ You: "Superlative claims like 'best' need robust clinical evidence per ABPI rules. Use specific trial data instead. Also, according to ABPI, you can't claim a medicine has no side effects. Mention the actual safety profile with specific data."

❌ Rep: "I'm taking Dr. Smith to a 3-star Michelin restaurant"  
✅ You: "Inviting a doctor to a luxury venue doesn't comply with ABPI rules on hospitality. Keep it modest and professional."

---

### ROLE 2: CONVERSATIONAL COACH (Post-Call Documentation)

{framework_guide}

---

## CONVERSATION FLOW

Since the call ALREADY HAPPENED:

1. **Opening:** Let rep start telling their story naturally
2. **During conversation:** 
   - Listen for compliance issues → mention briefly if detected
   - Listen for framework elements (needs, solution, action, follow-up)
   - ONE question at a time, only if element is missing
3. **Don't ask about:**
   - Call objectives (Phase 1)
   - How they built rapport (Phase 2)
   - These are for future calls, not post-call recording

---

## DOCTOR IDENTIFICATION RULES

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

## RESPONSE GUIDELINES

**For ABPI violations:**
- State issue briefly (one sentence)
- Suggest alternative
- Move on (don't dwell on it)

**For framework coaching:**
- Listen first, prompt second
- ONE question at a time
- Be curious: "What prompted that?" not "Did you do Phase 3?"
- Only ask if element is missing

**Never:**
- Read out ABPI clauses or mention asterisks
- Ask multiple questions at once
- Use compliance/legal language
- Remind them of all phases at once
- Ask about objectives or planning (call already happened)

---

Your goal: Help reps naturally document their calls while ensuring compliance and capturing key elements.
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

# Serve the HTML frontend at root
@app.get("/")
async def read_root():
    """Serve the HTML frontend"""
    return FileResponse("index.html")

# API info endpoint
@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "service": "Pharma Call Recorder POC",
        "status": "running",
        "version": "0.5.0 - Conversational Coaching",
        "doctors_loaded": len(DOCTORS),
        "anthropic_client": "ready" if anthropic_client else "not configured",
        "ai_checker": "ready" if ai_checker else "not configured",
        "features": [
            "Brief ABPI compliance feedback",
            "Conversational framework coaching",
            "Fuzzy doctor matching",
            "Post-call documentation"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

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
    
    # Accept either onekey_id or selected_doctor_id from frontend
    onekey_id = call_data.get("onekey_id") or call_data.get("selected_doctor_id")
    
    if not onekey_id:
        raise HTTPException(status_code=400, detail="onekey_id or selected_doctor_id is required for finalization")
    
    doctor = doctor_matcher.get_by_onekey_id(onekey_id)
    if not doctor:
        raise HTTPException(status_code=400, detail=f"Invalid onekey_id: {onekey_id}")
    
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "call_data": call_data,
        "doctor": doctor,
        "audit_trail": {
            "created_at": datetime.utcnow().isoformat(),
            "source": "voice_recording",
            "version": "POC-0.5.0",
            "onekey_id": onekey_id
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
        "onekey_id": onekey_id
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
