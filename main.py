# main.py - Pharma Call Recorder with ABPI Compliance + Framework Validation

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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
from abpi_compliance_checker import ABPIComplianceChecker

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

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load doctors database and initialize matcher
DOCTORS = load_doctors("doctors.json")
doctor_matcher = DoctorMatcher(DOCTORS)

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
    confirmed_onekey_id: Optional[str] = None

# System prompt for Claude
SYSTEM_PROMPT = """You are an AI assistant helping pharmaceutical sales representatives document their doctor visits.

CRITICAL RULES FOR DOCTOR IDENTIFICATION:
1. NEVER assume which doctor the rep visited - ALWAYS ask for confirmation
2. When the rep mentions a doctor, search the database and present ALL matching candidates
3. The rep MUST explicitly confirm "Yes, that's the one" or select from options before proceeding
4. If multiple doctors match (e.g., multiple "Dr. Dubois"), present ALL options and ask which one
5. Never proceed to finalize a call without explicit doctor confirmation
6. **CRITICAL**: Once a doctor is confirmed, ALWAYS refer to THAT EXACT DOCTOR by name throughout the rest of the conversation - NEVER switch to a different doctor
7. **CRITICAL**: If you see "[SYSTEM: Rep confirmed doctor: Dr. X...]" in the context, that is THE ONLY doctor for this call - do not mention any other doctor names

CRITICAL FORMATTING FOR CHOICES:
When presenting choices to the user (doctor disambiguation, brand selection, framework options), ALWAYS use numbered lists for clarity:

Example for doctor disambiguation:
"I found 4 doctors named Dubois in the database:

1. Dr. Marie Dubois - Cardiology at CHU Charleroi, Charleroi
2. Dr. Jean Dubois - Neurology at Hôpital Erasme, Brussels  
3. Dr. Pierre Dubois - Cardiology at AZ Sint-Jan, Bruges
4. Dr. Sophie Dubois - Rheumatology at CHR Liège, Liège

Which one did you visit? Please tell me the number or describe which doctor."

Your role:
1. Have a natural conversation to extract call details (brand discussed, key points, next actions)
2. When doctor info is mentioned, find matching candidates and ask for confirmation
3. Present doctor options clearly with numbered lists
4. Wait for explicit confirmation before marking doctor as confirmed
5. **Once doctor is confirmed, ALWAYS use that doctor's name in all subsequent responses**
6. Once doctor is confirmed AND all call details collected, mark as ready to finalize

When you have doctor candidates, respond with:
- Your conversational message asking for confirmation (use numbered lists!)
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
"""

# Create Anthropic client once at startup
def create_anthropic_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not configured")
    
    http_client = httpx.Client(timeout=60.0)
    return anthropic.Anthropic(api_key=api_key, http_client=http_client)

# Initialize clients
try:
    anthropic_client = create_anthropic_client()
    abpi_checker = ABPIComplianceChecker(anthropic_client=anthropic_client)
    print("✅ Anthropic client initialized successfully")
    print("✅ ABPI compliance checker initialized")
    print(f"✅ Loaded {len(DOCTORS)} doctors from database")
except Exception as e:
    print(f"❌ Failed to initialize: {e}")
    anthropic_client = None
    abpi_checker = None

@app.get("/")
async def serve_frontend():
    """Serve the main frontend"""
    return FileResponse("static/index.html")

@app.get("/favicon.ico")
async def favicon():
    """Return empty favicon to prevent 404 errors"""
    return FileResponse("static/favicon.ico") if os.path.exists("static/favicon.ico") else ""

@app.get("/health")
async def health_check():
    return {
        "service": "Pharma Call Recorder POC",
        "status": "running",
        "version": "0.4.0 - ABPI Compliance + Framework Validation",
        "doctors_loaded": len(DOCTORS),
        "anthropic_client": "ready" if anthropic_client else "not configured",
        "abpi_checker": "ready" if abpi_checker else "not configured",
        "features": [
            "Doctor disambiguation (fuzzy matching)",
            "ABPI Code 2024 compliance checking",
            "Generic 6-phase selling framework validation",
            "Multi-brand/multi-region architecture"
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
                context_message = f"\n[SYSTEM: Rep confirmed doctor: {confirmed_doctor['full_name']} ({confirmed_doctor['onekey_id']}) - {confirmed_doctor['specialty']}, {confirmed_doctor['hospital']}]"
                context_parts.append(context_message)
                print(f"[DEBUG] Adding confirmed doctor context: {confirmed_doctor['full_name']}")
        
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
        confirmed_onekey_id_from_response = None
        
        # Look for JSON block
        if "```json" in assistant_message:
            try:
                json_start = assistant_message.find("```json") + 7
                json_end = assistant_message.find("```", json_start)
                json_str = assistant_message[json_start:json_end].strip()
                extracted_data = json.loads(json_str)
                
                # Extract confirmed OneKey ID from JSON if present
                if extracted_data and extracted_data.get("doctor_info"):
                    confirmed_id = extracted_data["doctor_info"].get("confirmed_onekey_id")
                    if confirmed_id:
                        confirmed_onekey_id_from_response = confirmed_id
                        print(f"[DEBUG] Doctor confirmed in response: {confirmed_id}")
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
        if extracted_data and extracted_data.get("doctor_info") and not doctor_candidates and not confirmed_onekey_id_from_response:
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
            has_doctor = bool(confirmed_onekey_id_from_response or request.confirmed_onekey_id)
            has_call_data = bool(extracted_data.get("call_objectives") or extracted_data.get("key_discussion_points"))
            
            is_complete = has_brand and has_doctor and has_call_data
        
        return ConversationResponse(
            assistant_message=assistant_message,
            extracted_data=extracted_data,
            doctor_candidates=doctor_candidates,
            needs_doctor_confirmation=needs_confirmation,
            is_complete=is_complete,
            confirmed_onekey_id=confirmed_onekey_id_from_response
        )
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        print(f"[ERROR] Full traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/check_abpi_compliance")
async def check_abpi_compliance(call_data: dict):
    """
    Check call against ABPI Code 2024 + Selling Framework
    
    Request body:
    {
        "brand": "ProductName",
        "onekey_id": "BE-HCP-00001",
        "doctor": {"name": "Dr. X", "specialty": "Cardiology"},
        "call_objectives": ["List of objectives"],
        "key_discussion_points": ["Discussion points"],
        "agreements_reached": ["Agreements"],
        "next_actions": ["Next steps"]
    }
    
    Returns:
    {
        "overall_assessment": "COMPLIANT" | "NEEDS_REVIEW" | "CRITICAL_VIOLATIONS",
        "risk_score": 0-100,
        "framework_score": 0-100,
        "abpi_violations": {...},
        "framework_issues": [...],
        "recommended_actions": [...]
    }
    """
    
    if not abpi_checker:
        raise HTTPException(status_code=500, detail="ABPI checker not initialized")
    
    try:
        # Run compliance check
        region = call_data.get("region", "UK")  # Default to UK
        brand = call_data.get("brand")
        
        result = abpi_checker.check_compliance(
            call_data=call_data,
            region=region,
            brand=brand
        )
        
        return result
        
    except Exception as e:
        print(f"[ERROR] ABPI check failed: {str(e)}")
        print(f"[ERROR] Full traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"ABPI check failed: {str(e)}")

@app.post("/finalize")
async def finalize_call(call_data: dict):
    """
    Finalize and save call record with ABPI compliance check
    Requires confirmed OneKey ID
    
    CRITICAL: Call is automatically checked for ABPI violations + framework gaps
    If CRITICAL violations found, finalization is BLOCKED
    """
    
    # Validate that doctor is confirmed
    if not call_data.get("onekey_id"):
        raise HTTPException(status_code=400, detail="onekey_id is required for finalization")
    
    # Verify OneKey ID exists
    doctor = doctor_matcher.get_by_onekey_id(call_data["onekey_id"])
    if not doctor:
        raise HTTPException(status_code=400, detail=f"Invalid onekey_id: {call_data['onekey_id']}")
    
    # NEW: Run ABPI compliance check before finalization
    print("\n[INFO] Running ABPI compliance + framework validation...")
    
    if abpi_checker:
        try:
            compliance_result = abpi_checker.check_compliance(
                call_data=call_data,
                region=call_data.get("region", "UK"),
                brand=call_data.get("brand")
            )
            
            # BLOCK finalization if critical violations found
            if compliance_result.get("overall_assessment") == "CRITICAL_VIOLATIONS":
                print("[ERROR] Critical violations detected - finalization BLOCKED")
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Cannot finalize: Critical violations detected",
                        "compliance_result": compliance_result,
                        "recommended_actions": compliance_result.get("recommended_actions", [])
                    }
                )
            
            print(f"[INFO] Compliance check passed: {compliance_result.get('overall_assessment')}")
            print(f"[INFO] Risk score: {compliance_result.get('risk_score')}/100")
            print(f"[INFO] Framework score: {compliance_result.get('framework_score')}/100")
            
        except HTTPException:
            raise  # Re-raise HTTP exceptions (critical violations)
        except Exception as e:
            # Log compliance check failure but don't block finalization (fail-safe)
            print(f"[WARNING] Compliance check failed but allowing finalization: {str(e)}")
            compliance_result = {
                "error": f"Compliance check failed: {str(e)}",
                "overall_assessment": "ERROR"
            }
    else:
        # No ABPI checker available (fail-safe mode)
        print("[WARNING] ABPI checker not available - finalizing without compliance check")
        compliance_result = {
            "error": "ABPI checker not initialized",
            "overall_assessment": "NOT_CHECKED"
        }
    
    # Add metadata
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "call_data": call_data,
        "doctor": doctor,  # Full doctor info for reference
        "compliance_check": compliance_result,  # NEW: Include compliance results
        "audit_trail": {
            "created_at": datetime.utcnow().isoformat(),
            "source": "voice_recording",
            "version": "POC-0.4.0-ABPI",
            "onekey_id": call_data["onekey_id"],
            "compliance_framework": "ABPI Code 2024 + Generic Selling Framework",
            "overall_assessment": compliance_result.get("overall_assessment", "NOT_CHECKED"),
            "risk_score": compliance_result.get("risk_score", 0),
            "framework_score": compliance_result.get("framework_score", 0)
        }
    }
    
    # POC: Print to console
    print("\n" + "="*60)
    print("FINALIZED CALL RECORD WITH COMPLIANCE CHECK")
    print("="*60)
    print(json.dumps(record, indent=2))
    print("="*60 + "\n")
    
    return {
        "status": "success",
        "message": "Call record saved with ABPI compliance check",
        "record_id": f"CALL-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
        "onekey_id": call_data["onekey_id"],
        "compliance_summary": {
            "assessment": compliance_result.get("overall_assessment", "NOT_CHECKED"),
            "risk_score": compliance_result.get("risk_score", 0),
            "framework_score": compliance_result.get("framework_score", 0),
            "critical_violations": len(compliance_result.get("abpi_violations", {}).get("critical", [])),
            "framework_gaps": len([g for g in compliance_result.get("framework_issues", []) if g.get("severity") == "CRITICAL"])
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
