# main.py - Pharma Call Recorder with Fuzzy Doctor Disambiguation

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

# Request/Response models
class ConversationRequest(BaseModel):
    message: str
    conversation_history: Optional[List[dict]] = []
    confirmed_onekey_id: Optional[str] = None  # Rep confirms this specific doctor

class ConversationResponse(BaseModel):
    assistant_message: str
    extracted_data: Optional[dict] = None
    doctor_candidates: Optional[List[dict]] = None  # Multiple possible matches
    needs_doctor_confirmation: bool = False
    is_complete: bool = False

# System prompt for Claude - CRITICAL: Never auto-select doctors
SYSTEM_PROMPT = """You are an AI assistant helping pharmaceutical sales representatives document their doctor visits.

CRITICAL RULES FOR DOCTOR IDENTIFICATION:
1. NEVER assume which doctor the rep visited - ALWAYS ask for confirmation
2. When the rep mentions a doctor, search the database and present ALL matching candidates
3. The rep MUST explicitly confirm "Yes, that's the one" or select from options before proceeding
4. If multiple doctors match (e.g., multiple "Dr. Dubois"), present ALL options and ask which one
5. Never proceed to finalize a call without explicit doctor confirmation

Your role:
1. Have a natural conversation to extract call details (brand discussed, key points, next actions)
2. When doctor info is mentioned, find matching candidates and ask for confirmation
3. Present doctor options clearly: "I found X doctors matching that description: [list with specialty, hospital, city]"
4. Wait for explicit confirmation before marking doctor as confirmed
5. Once doctor is confirmed AND all call details collected, mark as ready to finalize

When you have doctor candidates, respond with:
- Your conversational message asking for confirmation
- JSON block with extracted data
- DOCTOR_CANDIDATES section listing all matches

Response format:
```json
{
  "brand": "string or null",
  "call_objectives": ["list"],
  "key_discussion_points": ["list"],
  "agreements_reached": ["list"],
  "next_actions": ["list"],
  "doctor_info": {
    "mentioned_name": "what the rep said",
    "mentioned_hospital": "if mentioned",
    "mentioned_city": "if mentioned",
    "confirmed_onekey_id": null  // Only set after explicit confirmation
  }
}
```

DOCTOR_CANDIDATES: [list onekey_id values of matches, e.g., BE-HCP-00001, BE-HCP-00002]

Example conversation:
Rep: "Just visited Dr. Dubois in Charleroi"
You: "I found 2 doctors named Dubois in Charleroi:
1. Dr. Marie Dubois - Cardiology, CHU Charleroi
2. Dr. Olivier Dubois - Cardiology, AZ Sint-Jan
Which one was it?"

Rep: "The cardiologist at CHU Charleroi"
You: "Got it - Dr. Marie Dubois, Cardiology at CHU Charleroi. Is that correct?"

Rep: "Yes"
You: [NOW mark as confirmed] "Perfect! What did you discuss about [brand]?"
"""

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
except Exception as e:
    print(f"❌ Failed to initialize: {e}")
    anthropic_client = None
    ai_checker = None

@app.get("/")
async def root():
    return {
        "service": "Pharma Call Recorder POC",
        "status": "running",
        "version": "0.3.0 - ABPI Compliance + Framework Validation",
        "doctors_loaded": len(DOCTORS),
        "anthropic_client": "ready" if anthropic_client else "not configured",
        "ai_checker": "ready" if ai_checker else "not configured",
        "features": [
            "Fuzzy doctor matching",
            "ABPI Code 2024 compliance checking",
            "6-phase selling framework validation"
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
    """
    Search for doctors using fuzzy matching
    Can use free text query OR specific criteria
    """
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
    """
    Main conversation endpoint with fuzzy doctor matching
    """
    
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
        
        # Call Claude API
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
            
            # Get full doctor info for each candidate
            doctor_candidates = []
            for onekey_id in onekey_ids:
                doctor = doctor_matcher.get_by_onekey_id(onekey_id)
                if doctor:
                    doctor_candidates.append(doctor)
            
            needs_confirmation = len(doctor_candidates) > 0
        
        # Alternatively, use doctor info from extracted data to search
        if extracted_data and extracted_data.get("doctor_info") and not doctor_candidates:
            doctor_info = extracted_data["doctor_info"]
            
            # Search using mentioned info
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
        
        # Check if complete (has brand, doctor confirmed, and call details)
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
    """
    Check call data against ABPI Code of Practice 2024 + Selling Framework
    
    Request body:
    {
        "brand": "ProductName",
        "onekey_id": "BE-HCP-00001",
        "doctor": {"name": "Dr. X", "specialty": "Cardiology"},
        "call_objectives": ["..."],
        "key_discussion_points": ["..."],
        "agreements_reached": ["..."],
        "next_actions": ["..."]
    }
    
    Returns:
    {
        "abpi_violations": {"critical": [], "high_risk": [], ...},
        "framework_issues": [...],
        "overall_assessment": "COMPLIANT" | "NEEDS_REVIEW" | "CRITICAL_VIOLATIONS",
        "risk_score": 0-100,
        "framework_score": 0-100,
        "recommended_actions": [...]
    }
    """
    
    if not ai_checker:
        raise HTTPException(
            status_code=500, 
            detail="AI compliance checker not initialized"
        )
    
    try:
        # Run compliance check
        result = ai_checker.check_compliance(
            call_data=call_data,
            region="UK",  # MVP: UK only, future: pass as parameter
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
    """
    Finalize and save call record
    Requires confirmed OneKey ID
    """
    
    # Validate that doctor is confirmed
    if not call_data.get("onekey_id"):
        raise HTTPException(status_code=400, detail="onekey_id is required for finalization")
    
    # Verify OneKey ID exists
    doctor = doctor_matcher.get_by_onekey_id(call_data["onekey_id"])
    if not doctor:
        raise HTTPException(status_code=400, detail=f"Invalid onekey_id: {call_data['onekey_id']}")
    
    # Add metadata
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "call_data": call_data,
        "doctor": doctor,  # Full doctor info for reference
        "audit_trail": {
            "created_at": datetime.utcnow().isoformat(),
            "source": "voice_recording",
            "version": "POC-0.2.0",
            "onekey_id": call_data["onekey_id"]
        }
    }
    
    # POC: Print to console
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
