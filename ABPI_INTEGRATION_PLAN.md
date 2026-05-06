# ABPI Compliance Framework Integration Plan
## Pharma Call Recorder POC - Phase 2 Enhancement

**Version:** 1.0  
**Date:** 2026-05-05  
**Author:** Claude AI Assistant  
**Project:** Pharma Call Recorder with ABPI Compliance

---

## Executive Summary

This plan integrates the comprehensive ABPI Code of Practice 2024 compliance framework into the existing pharma call recorder application. The integration will enable real-time compliance checking during call recording and post-call compliance auditing specific to UK pharmaceutical regulations.

**Key Objectives:**
1. Add ABPI-specific compliance checking to existing EU compliance checker
2. Enable real-time ABPI violation detection during call recording
3. Provide representative guidance on compliant vs. non-compliant language
4. Generate compliance reports aligned with ABPI Code requirements
5. Support multi-region compliance (EU + UK ABPI)

---

## Current Architecture Assessment

### Existing Components

```
pharma-call-recorder/
├── compliance/
│   ├── EU_Compliance_Guidelines.docx
│   └── EU_Compliance_Guidelines.md
├── frameworks/
│   ├── CardioMax_Selling_Framework.docx
│   └── CardioMax_Selling_Framework.md
├── main.py                      # FastAPI backend with Claude integration
├── compliance_checker.py         # Basic keyword-based compliance
├── ai_compliance_checker.py      # AI-powered EU compliance
├── doctor_matcher.py             # Fuzzy doctor matching
└── doctors.json                  # Doctor database (5000 records)
```

### Existing Capabilities
✅ Natural conversation flow with Claude Sonnet 4  
✅ Doctor disambiguation (fuzzy matching)  
✅ Call data extraction  
✅ EU compliance checking (AI-powered)  
✅ Brand framework integration  
✅ JSON audit trail  

### Gap Analysis
❌ No ABPI-specific compliance rules  
❌ No UK-specific regulatory checks  
❌ No verbatim language guidance (what to say vs. not say)  
❌ No ABPI clause-specific violation detection  
❌ No ABPI disclosure requirements tracking  

---

## Integration Architecture

### New Directory Structure

```
pharma-call-recorder/
├── compliance/
│   ├── EU_Compliance_Guidelines.docx
│   ├── EU_Compliance_Guidelines.md
│   ├── ABPI_Compliance_Framework.md          # NEW ⭐
│   └── ABPI_Compliance_Framework_Summary.md  # NEW (extracted key rules)
├── compliance_rules/                          # NEW directory
│   ├── abpi_rules.json                       # NEW (structured ABPI rules)
│   ├── abpi_verbatim_examples.json           # NEW (what to say/not say)
│   └── abpi_clause_mapping.json              # NEW (clause → violation mapping)
├── frameworks/
│   ├── CardioMax_Selling_Framework.docx
│   └── CardioMax_Selling_Framework.md
├── main.py                                    # ENHANCED
├── compliance_checker.py                      # ENHANCED
├── ai_compliance_checker.py                   # ENHANCED
├── abpi_compliance_checker.py                 # NEW ⭐
├── doctor_matcher.py
└── doctors.json
```

---

## Implementation Plan

### Phase 1: Document Preparation & Data Structuring (Day 1)

#### 1.1 Copy ABPI Framework to Project
**Task:** Move the comprehensive ABPI framework into compliance directory

**Actions:**
```bash
# Copy main framework
cp /mnt/user-data/outputs/ABPI_Compliance_Framework_HCP_Interactions.md \
   /Users/Olivier/AI_Workspace/pharma-call-recorder/compliance/ABPI_Compliance_Framework.md

# Commit to git
cd /Users/Olivier/AI_Workspace/pharma-call-recorder
git add compliance/ABPI_Compliance_Framework.md
git commit -m "Add ABPI Code of Practice 2024 compliance framework"
git push origin main
```

**Deliverables:**
- ✅ ABPI_Compliance_Framework.md in compliance/
- ✅ Version controlled in GitHub
- ✅ Available for AI-powered analysis

---

#### 1.2 Extract Structured ABPI Rules
**Task:** Create machine-readable JSON of ABPI rules for fast lookup

**File:** `compliance_rules/abpi_rules.json`

**Structure:**
```json
{
  "version": "2024.1",
  "effective_date": "2025-01-01",
  "source": "ABPI Code of Practice 2024",
  "rules": {
    "critical_violations": [
      {
        "rule_id": "ABPI-CRIT-001",
        "clause": "3.1",
        "title": "Pre-Marketing Authorization Promotion",
        "description": "Promoting medicine before marketing authorisation granted",
        "keywords": ["pre-approval", "coming soon", "pending approval", "awaiting license"],
        "severity": "CRITICAL",
        "sanctions": ["Public reprimand", "Breach of Clause 2", "Audit required"],
        "detection_patterns": [
          "mentioned product without marketing authorisation",
          "discussed timeline for approval",
          "suggested prescribing before license"
        ]
      },
      {
        "rule_id": "ABPI-CRIT-002",
        "clause": "11.2",
        "title": "Off-Label Promotion",
        "description": "Promoting indications not in marketing authorisation",
        "keywords": ["off-label", "unapproved indication", "not licensed for"],
        "severity": "CRITICAL",
        "sanctions": ["Breach of Clause 2", "Corrective statement", "Public reprimand"],
        "detection_patterns": [
          "discussed use outside SPC",
          "mentioned unapproved indication",
          "suggested off-label use"
        ]
      },
      {
        "rule_id": "ABPI-CRIT-003",
        "clause": "3.5",
        "title": "Personal Gifts Prohibited",
        "description": "Gifts for personal benefit are prohibited",
        "keywords": ["gift", "entertainment tickets", "cash", "personal benefit"],
        "severity": "CRITICAL",
        "sanctions": ["Breach of inducement rules", "Public reprimand"],
        "detection_patterns": [
          "offered tickets",
          "mentioned gift",
          "promised cash",
          "entertainment offer"
        ]
      }
    ],
    "high_risk_violations": [
      {
        "rule_id": "ABPI-HIGH-001",
        "clause": "6.4",
        "title": "Unqualified Safety Claims",
        "description": "Cannot state 'no adverse reactions' or 'safe' unqualified",
        "keywords": ["no side effects", "safe", "no adverse reactions", "perfectly safe"],
        "severity": "HIGH",
        "sanctions": ["Breach of Clause 6.4", "Corrective statement"],
        "detection_patterns": [
          "claimed no adverse reactions",
          "stated product is safe without qualification",
          "said no side effects"
        ]
      },
      {
        "rule_id": "ABPI-HIGH-002",
        "clause": "6.6",
        "title": "Competitor Disparagement",
        "description": "Cannot disparage competitors' medicines or activities",
        "keywords": ["outdated", "inferior", "worse than", "old technology"],
        "severity": "HIGH",
        "sanctions": ["Breach of Clause 6.6", "Corrective action"],
        "detection_patterns": [
          "disparaged competitor product",
          "called competitor outdated",
          "claimed competitor inferior"
        ]
      },
      {
        "rule_id": "ABPI-HIGH-003",
        "clause": "10.1",
        "title": "Inappropriate Hospitality",
        "description": "Lavish/extravagant venues prohibited, hospitality must be secondary",
        "keywords": ["luxury", "5-star", "resort", "entertainment", "spouse"],
        "severity": "HIGH",
        "sanctions": ["Breach of hospitality rules", "Audit"],
        "detection_patterns": [
          "offered extravagant venue",
          "mentioned spouse attendance",
          "entertainment as primary purpose"
        ]
      }
    ],
    "medium_risk_violations": [
      {
        "rule_id": "ABPI-MED-001",
        "clause": "6.1",
        "title": "Unsubstantiated Claims",
        "description": "Claims must be accurate, balanced, fair, capable of substantiation",
        "keywords": ["best in class", "most effective", "guaranteed results"],
        "severity": "MEDIUM",
        "sanctions": ["Request for substantiation", "Corrective action"],
        "detection_patterns": [
          "made superlative claim without evidence",
          "claimed superiority without trial data",
          "unbalanced presentation"
        ]
      },
      {
        "rule_id": "ABPI-MED-002",
        "clause": "10.8",
        "title": "Subsistence Limit Exceeded",
        "description": "Subsistence must not exceed £75 per person excluding VAT",
        "keywords": ["dinner", "lunch", "meal", "subsistence"],
        "severity": "MEDIUM",
        "sanctions": ["Breach of hospitality limits"],
        "detection_patterns": [
          "mentioned subsistence over £75",
          "expensive restaurant",
          "Michelin-starred"
        ]
      }
    ],
    "documentation_requirements": [
      {
        "rule_id": "ABPI-DOC-001",
        "clause": "28",
        "title": "Disclosure of Transfers of Value",
        "description": "Must disclose transfers of value to HCPs, ORDMs, healthcare orgs",
        "required_data": [
          "HCP OneKey ID",
          "Transfer of value amount",
          "Nature of transfer (registration, travel, accommodation)",
          "Date of transfer"
        ]
      },
      {
        "rule_id": "ABPI-DOC-002",
        "clause": "10.4",
        "title": "Written Agreement Required",
        "description": "Support for HCP event attendance requires written agreement",
        "required_data": [
          "Categories of cost (registration, accommodation, travel)",
          "Event details",
          "Educational rationale"
        ]
      }
    ]
  }
}
```

**Implementation:**
```python
# abpi_rules_loader.py
import json
from typing import Dict, List

class ABPIRulesLoader:
    def __init__(self, rules_file: str = "compliance_rules/abpi_rules.json"):
        with open(rules_file, 'r') as f:
            self.rules_data = json.load(f)
    
    def get_critical_violations(self) -> List[Dict]:
        return self.rules_data["rules"]["critical_violations"]
    
    def get_high_risk_violations(self) -> List[Dict]:
        return self.rules_data["rules"]["high_risk_violations"]
    
    def get_rule_by_id(self, rule_id: str) -> Dict:
        for category in self.rules_data["rules"].values():
            if isinstance(category, list):
                for rule in category:
                    if rule.get("rule_id") == rule_id:
                        return rule
        return None
```

**Deliverables:**
- ✅ compliance_rules/abpi_rules.json with all critical/high/medium violations
- ✅ abpi_rules_loader.py for fast rule lookup
- ✅ Version controlled in GitHub

---

#### 1.3 Create Verbatim Examples Database
**Task:** Extract "what to say vs. not say" examples for real-time guidance

**File:** `compliance_rules/abpi_verbatim_examples.json`

**Structure:**
```json
{
  "version": "2024.1",
  "categories": {
    "clinical_efficacy": [
      {
        "scenario": "Presenting Phase III trial data",
        "prohibited": {
          "statement": "Our drug is the best in its class and has no side effects.",
          "violations": ["ABPI-HIGH-001", "ABPI-MED-001"],
          "why_prohibited": "Unsubstantiated superlative + prohibited safety claim"
        },
        "compliant": {
          "statement": "In the APEX Phase III head-to-head trial versus standard of care, Drug X demonstrated a statistically significant 25% reduction in primary endpoint symptoms (p<0.001, n=1,247). The safety profile was consistent with the SPC, with the most common adverse reactions being [list from SPC].",
          "why_compliant": "Specific trial cited, quantified efficacy, balanced with safety, references SPC"
        }
      },
      {
        "scenario": "Discussing dosing",
        "prohibited": {
          "statement": "You can dose this however you want - it's very flexible.",
          "violations": ["ABPI-CRIT-002"],
          "why_prohibited": "Encourages off-label dosing, not per SPC"
        },
        "compliant": {
          "statement": "According to the SPC, the recommended dose for [indication] is [X mg/day], administered [route/frequency]. Dose adjustments may be required for patients with [specific conditions as per SPC].",
          "why_compliant": "Explicitly references SPC, specific dosing per authorisation"
        }
      }
    ],
    "off_label_handling": [
      {
        "scenario": "HCP asks about unapproved indication",
        "prohibited": {
          "statement": "While it's not approved for pediatric use yet, many of your colleagues are finding great results with it in kids.",
          "violations": ["ABPI-CRIT-002"],
          "why_prohibited": "Proactive off-label promotion"
        },
        "compliant": {
          "statement": "I cannot proactively discuss the use of this medicine outside of its licensed indications. The marketing authorisation for Drug X currently covers [list approved indications]. If you have a specific unsolicited clinical question, I can refer you to our Medical Information department.",
          "why_compliant": "States limitation, identifies approved indications, offers appropriate channel"
        }
      }
    ],
    "competitor_comparisons": [
      {
        "scenario": "Comparing to competitor",
        "prohibited": {
          "statement": "The competitor's product is old technology and far less safe than ours.",
          "violations": ["ABPI-HIGH-002"],
          "why_prohibited": "Disparages competitor, inflammatory language"
        },
        "compliant": {
          "statement": "In head-to-head trial COMPARE-123, Drug X demonstrated [specific endpoint result] compared to Competitor Y [specific result], with p-value of [X]. When comparing safety profiles, the incidence of [specific AE] was [X%] for Drug X versus [Y%] for Competitor Y.",
          "why_compliant": "Specific trial cited, quantified data for both, no disparagement"
        }
      }
    ],
    "hospitality_meetings": [
      {
        "scenario": "Inviting HCP to dinner",
        "prohibited": {
          "statement": "Let's grab dinner at that Michelin-starred restaurant so I can tell you about our new data.",
          "violations": ["ABPI-HIGH-003", "ABPI-MED-002"],
          "why_prohibited": "Extravagant venue, exceeds subsistence limit"
        },
        "compliant": {
          "statement": "I would like to invite you to a scientific meeting regarding [Therapeutic Area]. We will provide a modest meal during the session in line with ABPI requirements (within £75). The educational agenda will begin at 7:00 PM.",
          "why_compliant": "Educational focus primary, modest meal mentioned, within limits"
        }
      }
    ],
    "adverse_events": [
      {
        "scenario": "HCP mentions possible adverse event",
        "prohibited": {
          "statement": "That doesn't sound related to the drug - probably just coincidence.",
          "violations": ["Pharmacovigilance violation"],
          "why_prohibited": "Discourages reporting, makes inappropriate causality assessment"
        },
        "compliant": {
          "statement": "Thank you for sharing this. All suspected adverse events should be reported. I need to collect information for our pharmacovigilance team and will report this immediately. The event should also be reported through the Yellow Card Scheme.",
          "why_compliant": "Encourages reporting, follows PV requirements, provides Yellow Card info"
        }
      }
    ]
  }
}
```

**Deliverables:**
- ✅ compliance_rules/abpi_verbatim_examples.json with 20+ scenarios
- ✅ Real-time guidance system for representatives
- ✅ Version controlled in GitHub

---

### Phase 2: Backend Integration (Days 2-3)

#### 2.1 Create ABPI Compliance Checker Module
**Task:** Build dedicated ABPI compliance checker with AI + rules hybrid approach

**File:** `abpi_compliance_checker.py`

**Implementation:**
```python
"""
ABPI Code of Practice 2024 Compliance Checker
Hybrid approach: Rules-based + AI-powered analysis
"""

import json
import os
from typing import Dict, List, Optional
import anthropic
from datetime import datetime


class ABPIComplianceChecker:
    """
    Checks pharmaceutical sales calls against ABPI Code of Practice 2024
    Uses both structured rules and AI interpretation
    """
    
    def __init__(self, 
                 rules_file: str = "compliance_rules/abpi_rules.json",
                 verbatim_file: str = "compliance_rules/abpi_verbatim_examples.json",
                 framework_file: str = "compliance/ABPI_Compliance_Framework.md",
                 anthropic_client: anthropic.Anthropic = None):
        
        # Load structured rules
        with open(rules_file, 'r') as f:
            self.rules = json.load(f)
        
        # Load verbatim examples
        with open(verbatim_file, 'r') as f:
            self.verbatim_examples = json.load(f)
        
        # Load full framework text
        with open(framework_file, 'r') as f:
            self.framework_text = f.read()
        
        self.client = anthropic_client
    
    def check_compliance(self, call_data: dict) -> Dict:
        """
        Comprehensive ABPI compliance check
        Returns detailed violation report with severity levels
        """
        
        # Phase 1: Rules-based quick scan
        quick_violations = self._quick_scan(call_data)
        
        # Phase 2: AI-powered deep analysis
        ai_analysis = self._ai_deep_analysis(call_data)
        
        # Phase 3: Merge and prioritize
        final_report = self._merge_findings(quick_violations, ai_analysis)
        
        return final_report
    
    def _quick_scan(self, call_data: dict) -> Dict:
        """
        Fast keyword-based scan using structured rules
        """
        violations = {
            "critical": [],
            "high_risk": [],
            "medium_risk": [],
            "warnings": []
        }
        
        # Extract call text
        call_text = self._extract_call_text(call_data).lower()
        
        # Check critical violations
        for rule in self.rules["rules"]["critical_violations"]:
            for keyword in rule["keywords"]:
                if keyword.lower() in call_text:
                    violations["critical"].append({
                        "rule_id": rule["rule_id"],
                        "clause": rule["clause"],
                        "title": rule["title"],
                        "description": rule["description"],
                        "evidence": f"Keyword detected: {keyword}",
                        "severity": "CRITICAL",
                        "sanctions": rule["sanctions"]
                    })
                    break  # One match per rule is enough
        
        # Check high-risk violations
        for rule in self.rules["rules"]["high_risk_violations"]:
            for keyword in rule["keywords"]:
                if keyword.lower() in call_text:
                    violations["high_risk"].append({
                        "rule_id": rule["rule_id"],
                        "clause": rule["clause"],
                        "title": rule["title"],
                        "description": rule["description"],
                        "evidence": f"Keyword detected: {keyword}",
                        "severity": "HIGH",
                        "sanctions": rule["sanctions"]
                    })
                    break
        
        # Check medium-risk violations
        for rule in self.rules["rules"]["medium_risk_violations"]:
            for keyword in rule["keywords"]:
                if keyword.lower() in call_text:
                    violations["medium_risk"].append({
                        "rule_id": rule["rule_id"],
                        "clause": rule["clause"],
                        "title": rule["title"],
                        "description": rule["description"],
                        "evidence": f"Keyword detected: {keyword}",
                        "severity": "MEDIUM",
                        "sanctions": rule.get("sanctions", [])
                    })
                    break
        
        # Check documentation requirements
        if not call_data.get("onekey_id"):
            violations["warnings"].append({
                "rule_id": "ABPI-DOC-001",
                "title": "Missing HCP OneKey ID",
                "description": "Required for disclosure of transfers of value (Clause 28)"
            })
        
        return violations
    
    def _ai_deep_analysis(self, call_data: dict) -> Dict:
        """
        AI-powered contextual analysis using Claude
        Detects implicit violations and context-dependent issues
        """
        
        if not self.client:
            return {"error": "Anthropic client not available"}
        
        # Build analysis prompt
        prompt = f"""You are a pharmaceutical compliance officer expert in the ABPI Code of Practice 2024.

ABPI CODE OF PRACTICE 2024 (Relevant Sections):
{self._get_relevant_framework_sections()}

CALL RECORD TO ANALYZE:
Brand: {call_data.get('brand', 'N/A')}
HCP: {call_data.get('doctor', {}).get('name', 'N/A')}
Specialty: {call_data.get('doctor', {}).get('specialty', 'N/A')}

Call Objectives: {json.dumps(call_data.get('call_objectives', []), indent=2)}
Key Discussion Points: {json.dumps(call_data.get('key_discussion_points', []), indent=2)}
Agreements Reached: {json.dumps(call_data.get('agreements_reached', []), indent=2)}
Next Actions: {json.dumps(call_data.get('next_actions', []), indent=2)}

CRITICAL ANALYSIS INSTRUCTIONS:
1. Analyze for IMPLICIT violations (not just keywords)
2. Consider CONTEXT - what was implied vs. explicitly stated
3. Detect off-label promotion even if not explicitly mentioned
4. Check for inappropriate inducements or hospitality
5. Verify claims would be substantiatable
6. Check for disparagement or unbalanced comparisons
7. Review for proper documentation (OneKey ID, disclosure requirements)

For each violation found:
- Cite specific ABPI clause
- Quote evidence from call
- Explain WHY it violates (even if subtle)
- Suggest compliant alternative

Return as JSON:
```json
{{
  "critical_violations": [
    {{
      "clause": "X.X",
      "title": "Violation name",
      "evidence": "Exact quote or description from call",
      "explanation": "Why this violates ABPI Code",
      "risk_level": "CRITICAL/HIGH/MEDIUM",
      "compliant_alternative": "What should have been said instead"
    }}
  ],
  "implicit_issues": [
    {{
      "concern": "Description of subtle issue",
      "clause": "Relevant ABPI clause",
      "evidence": "What triggered the concern",
      "recommendation": "How to address"
    }}
  ],
  "compliant_aspects": [
    "What was done correctly per ABPI Code"
  ],
  "overall_assessment": "COMPLIANT" or "NEEDS_REVIEW" or "CRITICAL_VIOLATIONS",
  "risk_score": 0-100,
  "disclosure_requirements": [
    "What must be disclosed per Clauses 28-31"
  ]
}}
```

Be thorough. Catch subtle violations that keyword scanning would miss."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text
            
            # Parse JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                ai_result = json.loads(json_str)
            else:
                ai_result = json.loads(response_text)
            
            return ai_result
            
        except Exception as e:
            return {
                "error": f"AI analysis failed: {str(e)}",
                "overall_assessment": "ERROR"
            }
    
    def _get_relevant_framework_sections(self) -> str:
        """
        Extract most relevant sections from full framework
        Keep under token limit
        """
        # For now, return key sections
        # TODO: Implement smart section extraction based on call content
        return self.framework_text[:15000]  # Keep under 15k chars
    
    def _extract_call_text(self, call_data: dict) -> str:
        """Extract all text content from call data"""
        parts = []
        
        if call_data.get("brand"):
            parts.append(f"Brand: {call_data['brand']}")
        
        if call_data.get("call_objectives"):
            parts.append("Objectives: " + " ".join(call_data["call_objectives"]))
        
        if call_data.get("key_discussion_points"):
            parts.append("Discussion: " + " ".join(call_data["key_discussion_points"]))
        
        if call_data.get("agreements_reached"):
            parts.append("Agreements: " + " ".join(call_data["agreements_reached"]))
        
        if call_data.get("next_actions"):
            parts.append("Next actions: " + " ".join(call_data["next_actions"]))
        
        return " ".join(parts)
    
    def _merge_findings(self, quick_violations: Dict, ai_analysis: Dict) -> Dict:
        """
        Merge quick scan and AI analysis
        Prioritize and deduplicate
        """
        
        merged = {
            "timestamp": datetime.utcnow().isoformat(),
            "compliance_framework": "ABPI Code of Practice 2024",
            "critical_violations": [],
            "high_risk_violations": [],
            "medium_risk_violations": [],
            "warnings": [],
            "implicit_issues": ai_analysis.get("implicit_issues", []),
            "compliant_aspects": ai_analysis.get("compliant_aspects", []),
            "overall_assessment": "COMPLIANT",
            "risk_score": 0,
            "disclosure_requirements": ai_analysis.get("disclosure_requirements", []),
            "recommended_actions": []
        }
        
        # Merge critical violations
        critical_count = 0
        for v in quick_violations.get("critical", []):
            merged["critical_violations"].append(v)
            critical_count += 1
        
        for v in ai_analysis.get("critical_violations", []):
            # Avoid duplicates
            if not any(cv["clause"] == v["clause"] for cv in merged["critical_violations"]):
                merged["critical_violations"].append(v)
                critical_count += 1
        
        # Merge high-risk violations
        high_risk_count = 0
        for v in quick_violations.get("high_risk", []):
            merged["high_risk_violations"].append(v)
            high_risk_count += 1
        
        # Merge medium-risk
        for v in quick_violations.get("medium_risk", []):
            merged["medium_risk_violations"].append(v)
        
        # Merge warnings
        for v in quick_violations.get("warnings", []):
            merged["warnings"].append(v)
        
        # Calculate overall assessment
        if critical_count > 0:
            merged["overall_assessment"] = "CRITICAL_VIOLATIONS"
            merged["risk_score"] = 90 + (critical_count * 2)
        elif high_risk_count > 0:
            merged["overall_assessment"] = "NEEDS_REVIEW"
            merged["risk_score"] = 60 + (high_risk_count * 5)
        else:
            merged["overall_assessment"] = ai_analysis.get("overall_assessment", "COMPLIANT")
            merged["risk_score"] = ai_analysis.get("risk_score", 20)
        
        # Add recommended actions
        if critical_count > 0:
            merged["recommended_actions"].append("IMMEDIATE ESCALATION REQUIRED - Report to compliance officer")
            merged["recommended_actions"].append("Do not finalize call record until violations addressed")
        
        if high_risk_count > 0:
            merged["recommended_actions"].append("Review with manager before finalizing")
        
        return merged
    
    def get_verbatim_guidance(self, scenario_type: str) -> Dict:
        """
        Get verbatim examples for a scenario
        E.g., "clinical_efficacy", "off_label_handling", etc.
        """
        
        category = self.verbatim_examples.get("categories", {}).get(scenario_type, [])
        
        return {
            "scenario_type": scenario_type,
            "examples": category
        }
    
    def suggest_compliant_alternative(self, prohibited_statement: str) -> str:
        """
        Use AI to suggest compliant alternative to prohibited statement
        """
        
        if not self.client:
            return "Anthropic client not available"
        
        prompt = f"""Based on ABPI Code of Practice 2024, this statement is non-compliant:

"{prohibited_statement}"

Provide a compliant alternative that:
1. Conveys similar information appropriately
2. References SPC where needed
3. Is balanced and substantiatable
4. Follows ABPI Code requirements

Return ONLY the compliant alternative statement (no explanation)."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            return f"Error generating alternative: {str(e)}"


# Test function
if __name__ == "__main__":
    from dotenv import load_dotenv
    import httpx
    
    load_dotenv()
    
    # Create Anthropic client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        exit(1)
    
    http_client = httpx.Client(timeout=60.0)
    client = anthropic.Anthropic(api_key=api_key, http_client=http_client)
    
    print("="*60)
    print("ABPI COMPLIANCE CHECKER TEST")
    print("="*60)
    print()
    
    # Test with problematic call
    test_call = {
        "brand": "CardioMax",
        "doctor": {
            "name": "Dr. Marie Dubois",
            "specialty": "Cardiology",
            "hospital": "CHU Charleroi"
        },
        "call_objectives": ["Introduce CardioMax benefits"],
        "key_discussion_points": [
            "CardioMax is the best drug in its class with no side effects",
            "It's better than competitor X which is outdated technology",
            "I offered Dr. Dubois tickets to the football match as a thank you",
            "We discussed using it in pediatric patients even though not approved"
        ],
        "agreements_reached": [
            "Dr. Dubois will prescribe to all her hypertension patients",
            "We'll have dinner at the 5-star hotel to discuss further"
        ],
        "next_actions": ["Follow up next week"]
    }
    
    # Initialize checker
    checker = ABPIComplianceChecker(anthropic_client=client)
    
    print("Testing call with multiple ABPI violations...")
    print()
    
    # Run compliance check
    result = checker.check_compliance(test_call)
    
    # Print results
    print(json.dumps(result, indent=2))
    
    print()
    print("="*60)
    print("✅ TEST COMPLETE")
    print("="*60)
```

**Deliverables:**
- ✅ abpi_compliance_checker.py with hybrid checking
- ✅ Rules-based quick scan for performance
- ✅ AI-powered deep analysis for context
- ✅ Verbatim guidance system
- ✅ Version controlled in GitHub

---

#### 2.2 Enhance Main FastAPI Application
**Task:** Integrate ABPI compliance into existing conversation flow

**File Modifications:** `main.py`

**Key Changes:**
```python
# Add ABPI checker import
from abpi_compliance_checker import ABPIComplianceChecker

# Initialize at startup
abpi_checker = ABPIComplianceChecker(anthropic_client=anthropic_client)

# Add new endpoint: /check_abpi_compliance
@app.post("/check_abpi_compliance")
async def check_abpi_compliance(call_data: dict):
    """
    Check completed call against ABPI Code of Practice 2024
    """
    try:
        result = abpi_checker.check_compliance(call_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ABPI check failed: {str(e)}")

# Add new endpoint: /get_verbatim_guidance
@app.post("/get_verbatim_guidance")
async def get_verbatim_guidance(request: dict):
    """
    Get ABPI-compliant verbatim examples for a scenario
    
    Request: {"scenario_type": "clinical_efficacy"}
    """
    scenario_type = request.get("scenario_type")
    if not scenario_type:
        raise HTTPException(status_code=400, detail="scenario_type required")
    
    guidance = abpi_checker.get_verbatim_guidance(scenario_type)
    return guidance

# Add new endpoint: /suggest_compliant_alternative
@app.post("/suggest_compliant_alternative")
async def suggest_compliant_alternative(request: dict):
    """
    Get compliant alternative to a prohibited statement
    
    Request: {"statement": "Our drug has no side effects"}
    """
    statement = request.get("statement")
    if not statement:
        raise HTTPException(status_code=400, detail="statement required")
    
    alternative = abpi_checker.suggest_compliant_alternative(statement)
    return {"original": statement, "compliant_alternative": alternative}

# Modify /finalize endpoint to include ABPI check
@app.post("/finalize")
async def finalize_call(call_data: dict):
    """
    Finalize call with automatic ABPI compliance check
    """
    
    # ... existing validation ...
    
    # Run ABPI compliance check
    print("\n[INFO] Running ABPI compliance check...")
    abpi_result = abpi_checker.check_compliance(call_data)
    
    # Add to record
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "call_data": call_data,
        "doctor": doctor,
        "abpi_compliance": abpi_result,  # NEW ⭐
        "audit_trail": {
            "created_at": datetime.utcnow().isoformat(),
            "source": "voice_recording",
            "version": "POC-0.3.0-ABPI",
            "onekey_id": call_data["onekey_id"],
            "compliance_framework": "ABPI Code of Practice 2024"
        }
    }
    
    # ... rest of finalization ...
    
    return {
        "status": "success",
        "message": "Call record saved with ABPI compliance check",
        "record_id": f"CALL-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
        "onekey_id": call_data["onekey_id"],
        "abpi_compliance_status": abpi_result["overall_assessment"],
        "risk_score": abpi_result["risk_score"]
    }
```

**Deliverables:**
- ✅ Enhanced main.py with ABPI integration
- ✅ 3 new ABPI-specific endpoints
- ✅ Automatic compliance check on finalization
- ✅ Version controlled in GitHub

---

### Phase 3: Testing & Validation (Day 4)

#### 3.1 Create Test Suite
**Task:** Comprehensive test cases for ABPI compliance checking

**File:** `tests/test_abpi_compliance.py`

**Test Cases:**
```python
import pytest
import json
from abpi_compliance_checker import ABPIComplianceChecker

# Test data
CRITICAL_VIOLATION_CALL = {
    "brand": "CardioMax",
    "key_discussion_points": [
        "We can use this off-label for diabetes",
        "Not officially approved yet but coming soon",
        "I'll give you tickets to the match as thanks"
    ]
}

HIGH_RISK_VIOLATION_CALL = {
    "brand": "CardioMax",
    "key_discussion_points": [
        "This drug is completely safe with no side effects",
        "Competitor X is outdated and doesn't work well",
        "Let's have dinner at the luxury resort to discuss"
    ]
}

COMPLIANT_CALL = {
    "brand": "CardioMax",
    "onekey_id": "BE-HCP-00001",
    "call_objectives": ["Discuss clinical trial data"],
    "key_discussion_points": [
        "In the APEX trial, CardioMax demonstrated 25% reduction in primary endpoint (p<0.001)",
        "Safety profile consistent with SPC",
        "Most common adverse reactions are headache (12%) and dizziness (8%)"
    ],
    "agreements_reached": ["Trial in 5 patients per protocol"],
    "next_actions": ["Follow up in 2 weeks"]
}

def test_critical_violations_detected():
    """Test that critical ABPI violations are caught"""
    checker = ABPIComplianceChecker()
    result = checker.check_compliance(CRITICAL_VIOLATION_CALL)
    
    assert result["overall_assessment"] == "CRITICAL_VIOLATIONS"
    assert len(result["critical_violations"]) > 0
    assert any("off-label" in str(v).lower() for v in result["critical_violations"])

def test_high_risk_violations_detected():
    """Test that high-risk violations are caught"""
    checker = ABPIComplianceChecker()
    result = checker.check_compliance(HIGH_RISK_VIOLATION_CALL)
    
    assert result["overall_assessment"] in ["CRITICAL_VIOLATIONS", "NEEDS_REVIEW"]
    assert len(result["high_risk_violations"]) > 0

def test_compliant_call_passes():
    """Test that compliant call passes"""
    checker = ABPIComplianceChecker()
    result = checker.check_compliance(COMPLIANT_CALL)
    
    assert result["overall_assessment"] == "COMPLIANT"
    assert len(result["critical_violations"]) == 0

def test_verbatim_guidance_available():
    """Test that verbatim guidance works"""
    checker = ABPIComplianceChecker()
    guidance = checker.get_verbatim_guidance("clinical_efficacy")
    
    assert "examples" in guidance
    assert len(guidance["examples"]) > 0

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Deliverables:**
- ✅ Comprehensive test suite
- ✅ Test coverage >80%
- ✅ CI/CD integration ready
- ✅ Version controlled in GitHub

---

### Phase 4: Documentation (Day 5)

#### 4.1 Update README
**Task:** Document ABPI integration in main README

**Addition to README.md:**
```markdown
## ABPI Compliance Integration (Phase 2)

### Features
✅ Real-time ABPI Code of Practice 2024 compliance checking  
✅ Hybrid rules-based + AI-powered violation detection  
✅ Verbatim guidance ("what to say" vs. "what not to say")  
✅ Automatic compliance reporting on call finalization  
✅ Multi-region support (EU + UK ABPI)  

### ABPI-Specific Endpoints

#### `POST /check_abpi_compliance`
Check call data against ABPI Code of Practice 2024

**Request:**
```json
{
  "brand": "CardioMax",
  "doctor": {"name": "Dr. Dubois", "specialty": "Cardiology"},
  "call_objectives": ["..."],
  "key_discussion_points": ["..."],
  "agreements_reached": ["..."]
}
```

**Response:**
```json
{
  "overall_assessment": "COMPLIANT" | "NEEDS_REVIEW" | "CRITICAL_VIOLATIONS",
  "risk_score": 0-100,
  "critical_violations": [...],
  "high_risk_violations": [...],
  "disclosure_requirements": [...]
}
```

#### `POST /get_verbatim_guidance`
Get ABPI-compliant language examples

**Request:**
```json
{
  "scenario_type": "clinical_efficacy" | "off_label_handling" | "competitor_comparisons"
}
```

**Response:**
```json
{
  "scenario_type": "clinical_efficacy",
  "examples": [
    {
      "scenario": "Presenting trial data",
      "prohibited": {"statement": "...", "violations": [...]},
      "compliant": {"statement": "...", "why_compliant": "..."}
    }
  ]
}
```

### Compliance Frameworks Included
- ✅ EU Compliance Guidelines (existing)
- ✅ ABPI Code of Practice 2024 (new)
- ✅ Brand-specific selling frameworks (CardioMax)

### Testing ABPI Compliance

```bash
# Run ABPI compliance tests
python tests/test_abpi_compliance.py

# Test with sample call
curl -X POST http://localhost:8000/check_abpi_compliance \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "CardioMax",
    "key_discussion_points": ["In APEX trial, 25% reduction in symptoms (p<0.001)", "Safety per SPC"]
  }'
```
```

**Deliverables:**
- ✅ Updated README.md
- ✅ API documentation
- ✅ Usage examples
- ✅ Version controlled in GitHub

---

#### 4.2 Create ABPI Integration Guide
**Task:** Comprehensive guide for using ABPI compliance features

**File:** `docs/ABPI_INTEGRATION_GUIDE.md`

**Contents:**
```markdown
# ABPI Compliance Integration Guide
## Pharma Call Recorder with ABPI Code of Practice 2024

### Overview
This guide explains how to use the ABPI compliance features integrated into the pharma call recorder.

### Architecture
[Detailed architecture diagrams and explanations]

### API Reference
[Complete API documentation for all ABPI endpoints]

### Compliance Rules
[Explanation of all ABPI rules with examples]

### Verbatim Examples
[Complete list of "what to say" vs. "what not to say"]

### Integration Examples
[Step-by-step examples for common scenarios]

### Troubleshooting
[Common issues and solutions]
```

**Deliverables:**
- ✅ Comprehensive integration guide
- ✅ Examples for all scenarios
- ✅ Troubleshooting section
- ✅ Version controlled in GitHub

---

## Deployment Plan

### Local Development
```bash
# 1. Pull latest from GitHub
cd /Users/Olivier/AI_Workspace/pharma-call-recorder
git pull origin main

# 2. Install any new dependencies
pip install -r requirements.txt

# 3. Verify ABPI files exist
ls -la compliance/ABPI_Compliance_Framework.md
ls -la compliance_rules/

# 4. Run tests
python tests/test_abpi_compliance.py

# 5. Start server
python main.py
```

### GitHub Deployment
```bash
# Commit all changes
git add .
git commit -m "Phase 2: ABPI Code of Practice 2024 integration"
git push origin main
```

### Replit Deployment
1. Sync GitHub repo to Replit
2. Replit auto-detects Python and installs dependencies
3. Set environment variables in Replit Secrets
4. Click "Run" - server starts automatically

---

## File Checklist

### New Files to Create
- [ ] `compliance/ABPI_Compliance_Framework.md` (copy from outputs)
- [ ] `compliance_rules/abpi_rules.json` (structured rules)
- [ ] `compliance_rules/abpi_verbatim_examples.json` (what to say/not say)
- [ ] `abpi_compliance_checker.py` (main ABPI checker)
- [ ] `tests/test_abpi_compliance.py` (test suite)
- [ ] `docs/ABPI_INTEGRATION_GUIDE.md` (documentation)

### Files to Modify
- [ ] `main.py` (add ABPI endpoints)
- [ ] `README.md` (document ABPI features)
- [ ] `requirements.txt` (add any new dependencies)
- [ ] `.gitignore` (if needed)

### Files to Keep As-Is
- ✅ `compliance/EU_Compliance_Guidelines.md`
- ✅ `ai_compliance_checker.py`
- ✅ `compliance_checker.py`
- ✅ `doctor_matcher.py`
- ✅ `doctors.json`

---

## Timeline Summary

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1: Document Prep | Day 1 | ABPI framework copied, JSON rules created |
| Phase 2: Backend Integration | Days 2-3 | ABPI checker built, API enhanced |
| Phase 3: Testing | Day 4 | Test suite complete, validated |
| Phase 4: Documentation | Day 5 | README, guides complete |
| **Total** | **5 days** | **Production-ready ABPI integration** |

---

## Success Criteria

✅ ABPI compliance framework accessible in project  
✅ Structured rules database created (JSON)  
✅ Verbatim examples database created (JSON)  
✅ ABPI compliance checker functional (hybrid approach)  
✅ 3 new API endpoints working  
✅ Automatic compliance check on finalization  
✅ Test coverage >80%  
✅ Documentation complete  
✅ Deployed to GitHub  
✅ Deployable to Replit  

---

## Next Steps After Integration

### Phase 3 (Future)
1. **Multi-Brand Support**: Add frameworks for other brands beyond CardioMax
2. **Real-Time Guidance**: Voice prompts during call recording
3. **Compliance Dashboard**: Visual reporting and analytics
4. **CRM Integration**: Push compliance-checked calls to CRM
5. **Multi-Language**: Support for multiple EU regions
6. **Mobile App**: Native iOS/Android with offline compliance checking

---

## Support & Maintenance

### Updating ABPI Rules
When ABPI Code is updated:
1. Update `compliance/ABPI_Compliance_Framework.md`
2. Regenerate `compliance_rules/abpi_rules.json`
3. Update `compliance_rules/abpi_verbatim_examples.json`
4. Run full test suite
5. Commit changes to GitHub

### Monitoring Compliance
- Review flagged calls weekly
- Update rules based on new violations
- Train representatives on common issues

### Escalation Process
1. **Critical violations**: Immediate manager notification
2. **High-risk**: Review within 24 hours
3. **Medium-risk**: Review within 1 week
4. **Warnings**: Batch review monthly

---

## Appendix A: File Structure After Integration

```
pharma-call-recorder/
├── compliance/
│   ├── EU_Compliance_Guidelines.docx
│   ├── EU_Compliance_Guidelines.md
│   ├── ABPI_Compliance_Framework.md          ⭐ NEW
│   └── ABPI_Compliance_Framework_Summary.md  (optional)
│
├── compliance_rules/                          ⭐ NEW DIRECTORY
│   ├── abpi_rules.json                       ⭐ NEW
│   ├── abpi_verbatim_examples.json           ⭐ NEW
│   └── abpi_clause_mapping.json              ⭐ NEW
│
├── frameworks/
│   ├── CardioMax_Selling_Framework.docx
│   └── CardioMax_Selling_Framework.md
│
├── tests/                                     ⭐ NEW DIRECTORY
│   ├── test_abpi_compliance.py               ⭐ NEW
│   └── test_integration.py                   ⭐ NEW
│
├── docs/                                      ⭐ NEW DIRECTORY
│   └── ABPI_INTEGRATION_GUIDE.md             ⭐ NEW
│
├── main.py                                    📝 MODIFIED
├── abpi_compliance_checker.py                 ⭐ NEW
├── compliance_checker.py                      (unchanged)
├── ai_compliance_checker.py                   (unchanged)
├── doctor_matcher.py                          (unchanged)
├── doctors.json                               (unchanged)
├── README.md                                  📝 MODIFIED
├── requirements.txt                           📝 MODIFIED (if needed)
├── .gitignore                                 (check)
└── .env                                       (local only, not in git)
```

**Legend:**
- ⭐ NEW = Files to be created
- 📝 MODIFIED = Existing files to be updated
- (unchanged) = Files that stay as-is

---

## Appendix B: API Contract Examples

### Example 1: Complete Call with ABPI Check

**Request to `/finalize`:**
```json
{
  "onekey_id": "BE-HCP-00001",
  "brand": "CardioMax",
  "call_objectives": ["Present APEX trial data"],
  "key_discussion_points": [
    "APEX Phase III trial showed 25% reduction in primary endpoint (p<0.001, n=1247)",
    "Safety profile consistent with SPC",
    "Most common AEs: headache (12%), dizziness (8%)",
    "Appropriate for patients with hypertension per indication"
  ],
  "agreements_reached": [
    "Trial with 5 appropriate patients per protocol"
  ],
  "next_actions": [
    "Follow up in 2 weeks",
    "Send patient education materials"
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "record_id": "CALL-20260505-143022",
  "onekey_id": "BE-HCP-00001",
  "abpi_compliance_status": "COMPLIANT",
  "risk_score": 15,
  "abpi_compliance": {
    "overall_assessment": "COMPLIANT",
    "risk_score": 15,
    "critical_violations": [],
    "high_risk_violations": [],
    "medium_risk_violations": [],
    "warnings": [],
    "compliant_aspects": [
      "Specific trial cited with quantified results",
      "Safety balanced with efficacy",
      "References SPC appropriately",
      "Within approved indication",
      "Appropriate patient selection mentioned"
    ],
    "disclosure_requirements": [
      "No transfers of value detected - no disclosure needed"
    ]
  }
}
```

### Example 2: Call with Violations

**Request to `/check_abpi_compliance`:**
```json
{
  "brand": "CardioMax",
  "doctor": {"name": "Dr. Dubois", "specialty": "Cardiology"},
  "key_discussion_points": [
    "CardioMax is the best drug in class",
    "No side effects at all",
    "Competitor X doesn't work as well",
    "Let's have dinner at the Ritz to discuss more"
  ]
}
```

**Response:**
```json
{
  "overall_assessment": "CRITICAL_VIOLATIONS",
  "risk_score": 95,
  "critical_violations": [
    {
      "rule_id": "ABPI-HIGH-001",
      "clause": "6.4",
      "title": "Unqualified Safety Claims",
      "evidence": "Stated 'No side effects at all'",
      "severity": "CRITICAL",
      "explanation": "Violates Clause 6.4 - cannot state product has no adverse reactions",
      "compliant_alternative": "Safety profile consistent with SPC, with most common adverse reactions being [list from SPC]"
    }
  ],
  "high_risk_violations": [
    {
      "rule_id": "ABPI-MED-001",
      "clause": "6.1",
      "title": "Unsubstantiated Claims",
      "evidence": "Claimed 'best drug in class'",
      "severity": "HIGH",
      "explanation": "Superlative claim without substantiation"
    },
    {
      "rule_id": "ABPI-HIGH-002",
      "clause": "6.6",
      "title": "Competitor Disparagement",
      "evidence": "Said 'Competitor X doesn't work as well'",
      "severity": "HIGH",
      "explanation": "Disparages competitor without objective evidence"
    },
    {
      "rule_id": "ABPI-HIGH-003",
      "clause": "10.1",
      "title": "Inappropriate Hospitality",
      "evidence": "Mentioned dinner at the Ritz",
      "severity": "HIGH",
      "explanation": "Extravagant venue prohibited"
    }
  ],
  "recommended_actions": [
    "IMMEDIATE ESCALATION REQUIRED - Report to compliance officer",
    "Do not finalize call record until violations addressed",
    "Representative requires retraining on ABPI Code"
  ]
}
```

---

**END OF INTEGRATION PLAN**
