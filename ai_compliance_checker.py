"""
AI-Powered Compliance and Framework Checker
Uses Claude to interpret guidelines and detect violations intelligently
"""

import subprocess
import os
from typing import Dict, List, Optional
import anthropic
import httpx


class AIComplianceChecker:
    """
    Uses Claude to intelligently check compliance against guidelines
    Not just keyword matching - actual understanding of rules
    """
    
    def __init__(self, 
                 compliance_file: str = "compliance/EU_Compliance_Guidelines.docx",
                 anthropic_client: anthropic.Anthropic = None):
        self.compliance_file = compliance_file
        self.guidelines_text = self._load_docx(compliance_file)
        self.client = anthropic_client
        
    def _load_docx(self, filepath: str) -> str:
        """Extract text from .docx file"""
        if not os.path.exists(filepath):
            return f"File not found: {filepath}"
        
        try:
            result = subprocess.run(
                ['extract-text', filepath],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Failed to extract: {result.stderr}"
                
        except FileNotFoundError:
            return "extract-text not found - install pandoc"
        except Exception as e:
            return f"Error loading: {e}"
    
    def check_compliance(self, call_data: dict) -> Dict:
        """
        AI-powered compliance check
        Claude interprets the guidelines and analyzes the call
        """
        
        if not self.client:
            return {"error": "Anthropic client not initialized"}
        
        # Build the compliance checking prompt
        prompt = f"""You are a pharmaceutical compliance officer reviewing a sales call record against official guidelines.

COMPLIANCE GUIDELINES:
{self.guidelines_text}

CALL RECORD TO REVIEW:
Brand: {call_data.get('brand', 'N/A')}
Doctor: {call_data.get('doctor', 'N/A')}
Call Objectives: {call_data.get('call_objectives', [])}
Key Discussion Points: {call_data.get('key_discussion_points', [])}
Agreements Reached: {call_data.get('agreements_reached', [])}
Next Actions: {call_data.get('next_actions', [])}

CRITICAL INSTRUCTIONS:
1. Analyze the call content against the guidelines
2. Detect violations even if not explicitly stated (e.g., off-label = discussing use outside approved indications)
3. Consider context - what was IMPLIED, not just what was literally said
4. For each violation found, cite the specific guideline rule

Return your analysis as JSON:
```json
{{
  "critical_violations": [
    {{"rule": "RULE_NAME", "evidence": "what in the call triggered this", "guideline_reference": "quote from guidelines", "requires_action": "what must be done"}}
  ],
  "high_risk_issues": [
    {{"rule": "RULE_NAME", "evidence": "what triggered this", "guideline_reference": "quote", "recommendation": "suggested action"}}
  ],
  "medium_risk_issues": [
    {{"rule": "RULE_NAME", "evidence": "what triggered this", "guideline_reference": "quote"}}
  ],
  "compliant_aspects": [
    "what was done correctly"
  ],
  "overall_assessment": "COMPLIANT" or "NEEDS_REVIEW" or "VIOLATIONS_DETECTED"
}}
```

Be thorough but fair. Only flag genuine violations based on the actual guidelines provided."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract JSON from response
            response_text = response.content[0].text
            
            # Parse JSON
            import json
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                compliance_result = json.loads(json_str)
            else:
                # Try to parse entire response as JSON
                compliance_result = json.loads(response_text)
            
            return compliance_result
            
        except Exception as e:
            return {
                "error": f"Compliance check failed: {str(e)}",
                "overall_assessment": "ERROR"
            }


class AIBrandFramework:
    """
    AI-powered framework loader and advisor
    Claude interprets the framework and provides guidance
    """
    
    def __init__(self, 
                 framework_file: str,
                 anthropic_client: anthropic.Anthropic = None):
        self.framework_file = framework_file
        self.framework_text = self._load_docx(framework_file)
        self.client = anthropic_client
        
    def _load_docx(self, filepath: str) -> str:
        """Extract text from .docx file"""
        if not os.path.exists(filepath):
            return f"File not found: {filepath}"
        
        try:
            result = subprocess.run(
                ['extract-text', filepath],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Failed to extract: {result.stderr}"
                
        except FileNotFoundError:
            return "extract-text not found - install pandoc"
        except Exception as e:
            return f"Error loading: {e}"
    
    def get_framework_text(self) -> str:
        """Get the full framework text"""
        return self.framework_text
    
    def analyze_call_vs_framework(self, call_data: dict) -> Dict:
        """
        AI-powered framework analysis
        Claude compares call to ideal framework execution
        """
        
        if not self.client:
            return {"error": "Anthropic client not initialized"}
        
        prompt = f"""You are a pharmaceutical sales coach analyzing a call against the brand's selling framework.

BRAND FRAMEWORK:
{self.framework_text}

ACTUAL CALL RECORD:
Brand: {call_data.get('brand', 'N/A')}
Doctor: {call_data.get('doctor', 'N/A')}
Call Objectives: {call_data.get('call_objectives', [])}
Key Discussion Points: {call_data.get('key_discussion_points', [])}
Agreements Reached: {call_data.get('agreements_reached', [])}
Next Actions: {call_data.get('next_actions', [])}

Analyze how well this call followed the framework:

Return as JSON:
```json
{{
  "framework_alignment_score": 0-100,
  "objectives_met": [
    {{"framework_objective": "...", "was_addressed": true/false, "evidence": "..."}}
  ],
  "missed_opportunities": [
    {{"opportunity": "what wasn't discussed but should have been", "framework_reference": "..."}}
  ],
  "strong_points": [
    "what was done well according to framework"
  ],
  "suggested_improvements": [
    {{"suggestion": "...", "framework_rationale": "why this matters per framework"}}
  ],
  "next_call_focus": [
    "priorities for follow-up based on framework"
  ]
}}
```"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text
            
            # Parse JSON
            import json
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                analysis = json.loads(json_str)
            else:
                analysis = json.loads(response_text)
            
            return analysis
            
        except Exception as e:
            return {
                "error": f"Framework analysis failed: {str(e)}"
            }


def get_framework_for_brand(brand: str, anthropic_client=None) -> Optional[AIBrandFramework]:
    """
    Load the appropriate framework for a brand
    MVP: Uses Generic_Selling_Framework.docx for all brands
    Future: Map specific brands to their frameworks
    """
    # For now, use generic framework for all brands
    generic_framework = "frameworks/Generic_Selling_Framework.docx"
    
    if os.path.exists(generic_framework):
        return AIBrandFramework(generic_framework, anthropic_client)
    
    # Fallback to .md if .docx not found
    md_framework = "frameworks/Generic_Selling_Framework.md"
    if os.path.exists(md_framework):
        return AIBrandFramework(md_framework, anthropic_client)
    
    return None


# Test function
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    # Create Anthropic client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        exit(1)
    
    http_client = httpx.Client(timeout=60.0)
    client = anthropic.Anthropic(api_key=api_key, http_client=http_client)
    
    print("="*60)
    print("AI-POWERED COMPLIANCE & FRAMEWORK TEST")
    print("="*60)
    print()
    
    # Test compliance checker
    print("1. Loading EU Compliance Guidelines...")
    checker = AIComplianceChecker(anthropic_client=client)
    print(f"   Guidelines loaded: {len(checker.guidelines_text)} chars")
    print()
    
    # Test with realistic call that has IMPLICIT off-label use
    print("2. Testing AI compliance check...")
    print("   (Call discusses product for diabetes - checking for off-label use)")
    print()
    
    test_call = {
        "brand": "GenericBrand",  # Using generic framework for POC
        "doctor": "Dr. Marie Dubois",
        "call_objectives": ["Discuss product benefits"],
        "key_discussion_points": [
            "Product helps with blood sugar control",
            "Good for diabetic patients with hypertension",
            "Trial showed 15% HbA1c reduction"
        ],
        "agreements_reached": ["Will try in 5 diabetic patients"],
        "next_actions": ["Follow up in 2 weeks"]
    }
    
    print("   Analyzing call...")
    violations = checker.check_compliance(test_call)
    
    import json
    print(json.dumps(violations, indent=2))
    
    print()
    print("="*60)
    print("✅ TEST COMPLETE")
    print("="*60)
