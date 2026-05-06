"""
ABPI Code of Practice 2024 Compliance Checker + Selling Framework Validator
MVP Version for Phase 2 Demo

Features:
- ABPI compliance checking (critical + high risk violations)
- Selling framework validation (6-phase structure)
- Multi-brand/multi-region architecture (ready for scaling)
- AI-powered contextual analysis
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import anthropic


class ABPIComplianceChecker:
    """
    Checks pharmaceutical sales calls against:
    1. ABPI Code of Practice 2024 (UK regulations)
    2. Generic 6-Phase Selling Framework
    3. Brand-specific frameworks (future: pass brand name to load specific framework)
    """
    
    def __init__(self,
                 rules_file: str = "compliance_rules/abpi_rules.json",
                 framework_file: str = "frameworks/Generic_Selling_Framework.md",
                 anthropic_client: anthropic.Anthropic = None):
        
        # Load ABPI rules
        with open(rules_file, 'r') as f:
            self.rules = json.load(f)
        
        # Load selling framework (generic for MVP, brand-specific in future)
        with open(framework_file, 'r') as f:
            self.framework_text = f.read()
        
        self.client = anthropic_client
        
        # Multi-region support (future expansion)
        self.supported_regions = ["UK"]  # MVP: UK only, future: EU, US
        self.current_region = "UK"
    
    def check_compliance(self, 
                        call_data: dict, 
                        region: str = "UK",
                        brand: Optional[str] = None) -> Dict:
        """
        Comprehensive compliance check: ABPI + Selling Framework
        
        Args:
            call_data: Call record with objectives, discussion points, agreements
            region: Regulatory region (UK, EU, US - MVP supports UK only)
            brand: Brand name for brand-specific framework (future feature)
        
        Returns:
            Complete compliance report with ABPI violations + framework gaps
        """
        
        # Validate region support
        if region not in self.supported_regions:
            return {
                "error": f"Region '{region}' not supported. MVP supports: {self.supported_regions}",
                "overall_assessment": "ERROR"
            }
        
        # Phase 1: Quick ABPI scan (rules-based)
        abpi_quick_scan = self._quick_abpi_scan(call_data)
        
        # Phase 2: Selling framework validation
        framework_check = self._validate_framework_structure(call_data)
        
        # Phase 3: AI-powered deep analysis (ABPI + Framework)
        ai_analysis = self._ai_deep_analysis(call_data, brand)
        
        # Phase 4: Merge findings
        final_report = self._merge_findings(abpi_quick_scan, framework_check, ai_analysis)
        
        # Add metadata
        final_report.update({
            "region": region,
            "brand": brand or "Generic",
            "framework_used": "Generic 6-Phase" if not brand else f"{brand} Framework"
        })
        
        return final_report
    
    def _quick_abpi_scan(self, call_data: dict) -> Dict:
        """
        Fast keyword-based ABPI scan
        Catches obvious violations before AI analysis
        """
        violations = {
            "critical": [],
            "high_risk": [],
            "medium_risk": [],
            "warnings": []
        }
        
        # Extract all text from call
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
                        "evidence": f"Keyword detected: '{keyword}'",
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
                        "evidence": f"Keyword detected: '{keyword}'",
                        "severity": "HIGH",
                        "sanctions": rule["sanctions"],
                        "compliant_alternative": rule.get("compliant_alternative", "")
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
                        "evidence": f"Keyword detected: '{keyword}'",
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
    
    def _validate_framework_structure(self, call_data: dict) -> Dict:
        """
        Validate call against 6-phase selling framework
        Checks for required phases and quality of execution
        """
        
        framework_reqs = self.rules.get("selling_framework_requirements", {})
        required_phases = framework_reqs.get("required_phases", [])
        phase_validation = framework_reqs.get("phase_validation", {})
        
        gaps = []
        compliant_phases = []
        
        # Check Phase 1: Purposeful Planning (must have clear objective)
        if not call_data.get("call_objectives") or len(call_data.get("call_objectives", [])) == 0:
            gaps.append({
                "phase": "Purposeful Planning",
                "issue": "No clear call objective documented",
                "severity": "HIGH",
                "recommendation": "Define specific, measurable call objective (e.g., 'Get Dr. X to trial product with 5 patients in 4 weeks')"
            })
        else:
            # Check if objective is specific (not generic like "introduce product")
            objectives = call_data.get("call_objectives", [])
            if any(obj.lower() in ["introduce", "discuss", "present"] for obj in objectives):
                gaps.append({
                    "phase": "Purposeful Planning",
                    "issue": "Call objective too generic (e.g., 'introduce' or 'discuss')",
                    "severity": "MEDIUM",
                    "recommendation": "Make objective specific and measurable (SMART criteria)"
                })
            else:
                compliant_phases.append("Purposeful Planning")
        
        # Check Phase 6: Call to Action (must have Voluntary & Active commitment)
        if not call_data.get("agreements_reached") or len(call_data.get("agreements_reached", [])) == 0:
            gaps.append({
                "phase": "Call to Action",
                "issue": "No Voluntary & Active commitment secured",
                "severity": "CRITICAL",
                "recommendation": "Secure specific action + timeline + HCP explicit agreement (e.g., 'Trial with 5 patients starting next clinic')"
            })
        else:
            # Check if commitment is specific (has action + timeline)
            agreements = call_data.get("agreements_reached", [])
            has_timeline = any(
                any(word in agr.lower() for word in ["week", "month", "date", "next", "by"])
                for agr in agreements
            )
            if not has_timeline:
                gaps.append({
                    "phase": "Call to Action",
                    "issue": "Commitment lacks specific timeline",
                    "severity": "HIGH",
                    "recommendation": "Add explicit timeline (e.g., 'in 2 weeks', 'by end of month')"
                })
            else:
                compliant_phases.append("Call to Action")
        
        # Check Phase 3: Uncovering Needs (should have discussion points)
        if not call_data.get("key_discussion_points") or len(call_data.get("key_discussion_points", [])) == 0:
            gaps.append({
                "phase": "Uncovering Needs",
                "issue": "No needs uncovered or discussion points documented",
                "severity": "MEDIUM",
                "recommendation": "Document HCP's stated challenges, patient population needs, barriers"
            })
        else:
            compliant_phases.append("Uncovering Needs")
        
        # Check Phase 4: Tailored Solutions (agreements should tie to discussion points)
        if call_data.get("key_discussion_points") and call_data.get("agreements_reached"):
            # AI will validate if solutions tie to needs in deep analysis
            compliant_phases.append("Tailored Solutions")
        
        return {
            "framework_gaps": gaps,
            "compliant_phases": compliant_phases,
            "framework_score": len(compliant_phases) / len(required_phases) * 100 if required_phases else 0
        }
    
    def _ai_deep_analysis(self, call_data: dict, brand: Optional[str]) -> Dict:
        """
        AI-powered contextual analysis
        Detects implicit ABPI violations + framework quality issues
        """
        
        if not self.client:
            return {
                "error": "Anthropic client not available",
                "overall_assessment": "ERROR"
            }
        
        # Build comprehensive analysis prompt
        prompt = f"""You are a pharmaceutical compliance officer expert in:
1. ABPI Code of Practice 2024 (UK pharmaceutical regulations)
2. Generic 6-Phase Selling Framework (Purposeful Planning → Bold Opening → Uncovering Needs → Tailored Solutions → Handling Objections → Call to Action)

CRITICAL TASK: Analyze this pharmaceutical sales call for:
A) ABPI violations (explicit and IMPLICIT)
B) Selling framework gaps (did rep follow the 6 phases properly?)

CALL RECORD:
Brand: {call_data.get('brand', 'N/A')}
HCP: {call_data.get('doctor', {}).get('name', 'N/A')}
Specialty: {call_data.get('doctor', {}).get('specialty', 'N/A')}

Call Objectives: {json.dumps(call_data.get('call_objectives', []), indent=2)}
Key Discussion Points: {json.dumps(call_data.get('key_discussion_points', []), indent=2)}
Agreements Reached: {json.dumps(call_data.get('agreements_reached', []), indent=2)}
Next Actions: {json.dumps(call_data.get('next_actions', []), indent=2)}

ABPI CRITICAL VIOLATIONS TO CHECK (cite clause if found):
- Pre-marketing promotion (Clause 3.1)
- Off-label promotion (Clause 11.2)
- Personal gifts/inducements (Clause 3.5)
- Unqualified safety claims (Clause 6.4) - e.g., "no side effects"
- Competitor disparagement (Clause 6.6) - e.g., "competitor X is outdated"
- Unsubstantiated claims (Clause 6.1) - e.g., "best in class" without trial data
- Inappropriate hospitality (Clause 10.1) - e.g., luxury venues, spouse attendance

SELLING FRAMEWORK QUALITY CHECKS:
1. Planning: Is call objective SPECIFIC & measurable? (❌ "introduce product" ✅ "get trial in 5 patients")
2. Needs: Were HCP needs explicitly uncovered? Or did rep assume/jump to pitch?
3. Solutions: Are agreements clearly TIED to stated needs?
4. Action: Is commitment Voluntary & Active? (specific action + timeline + explicit HCP agreement)

RESPOND IN JSON:
```json
{{
  "abpi_violations": [
    {{
      "clause": "X.X",
      "title": "Violation name",
      "evidence": "Exact quote or description",
      "severity": "CRITICAL/HIGH/MEDIUM",
      "explanation": "Why this violates ABPI Code",
      "compliant_alternative": "What should have been said"
    }}
  ],
  "framework_quality_issues": [
    {{
      "phase": "Phase name",
      "issue": "What was wrong",
      "severity": "CRITICAL/HIGH/MEDIUM",
      "recommendation": "How to fix"
    }}
  ],
  "strengths": ["What was done well per ABPI + Framework"],
  "overall_assessment": "COMPLIANT" or "NEEDS_REVIEW" or "CRITICAL_VIOLATIONS",
  "risk_score": 0-100,
  "required_actions": ["What must be done before finalizing"]
}}
```

Be thorough. Catch IMPLICIT violations (e.g., discussing dosing outside SPC without explicit mention).
"""

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
    
    def _extract_call_text(self, call_data: dict) -> str:
        """Extract all text content from call for keyword scanning"""
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
    
    def _merge_findings(self, 
                       abpi_quick_scan: Dict, 
                       framework_check: Dict,
                       ai_analysis: Dict) -> Dict:
        """
        Merge quick scan + framework check + AI analysis
        Prioritize and deduplicate
        """
        
        merged = {
            "timestamp": datetime.utcnow().isoformat(),
            "compliance_framework": "ABPI Code of Practice 2024 + Generic Selling Framework",
            "abpi_violations": {
                "critical": [],
                "high_risk": [],
                "medium_risk": [],
                "warnings": []
            },
            "framework_issues": [],
            "strengths": [],
            "overall_assessment": "COMPLIANT",
            "risk_score": 0,
            "framework_score": framework_check.get("framework_score", 0),
            "recommended_actions": []
        }
        
        # Merge ABPI violations
        critical_count = 0
        high_risk_count = 0
        
        # Add quick scan ABPI violations
        for v in abpi_quick_scan.get("critical", []):
            merged["abpi_violations"]["critical"].append(v)
            critical_count += 1
        
        for v in abpi_quick_scan.get("high_risk", []):
            merged["abpi_violations"]["high_risk"].append(v)
            high_risk_count += 1
        
        for v in abpi_quick_scan.get("medium_risk", []):
            merged["abpi_violations"]["medium_risk"].append(v)
        
        for v in abpi_quick_scan.get("warnings", []):
            merged["abpi_violations"]["warnings"].append(v)
        
        # Add AI-detected ABPI violations (deduplicate by clause)
        for v in ai_analysis.get("abpi_violations", []):
            # Check if already detected by quick scan
            clause = v.get("clause", "")
            severity = v.get("severity", "HIGH")
            
            if severity == "CRITICAL":
                if not any(cv.get("clause") == clause for cv in merged["abpi_violations"]["critical"]):
                    merged["abpi_violations"]["critical"].append(v)
                    critical_count += 1
            elif severity == "HIGH":
                if not any(hv.get("clause") == clause for hv in merged["abpi_violations"]["high_risk"]):
                    merged["abpi_violations"]["high_risk"].append(v)
                    high_risk_count += 1
            else:
                if not any(mv.get("clause") == clause for mv in merged["abpi_violations"]["medium_risk"]):
                    merged["abpi_violations"]["medium_risk"].append(v)
        
        # Add framework issues
        merged["framework_issues"] = framework_check.get("framework_gaps", [])
        framework_critical_count = len([g for g in merged["framework_issues"] if g.get("severity") == "CRITICAL"])
        framework_high_count = len([g for g in merged["framework_issues"] if g.get("severity") == "HIGH"])
        
        # Add strengths
        merged["strengths"] = ai_analysis.get("strengths", [])
        if framework_check.get("compliant_phases"):
            merged["strengths"].append(f"Framework phases executed well: {', '.join(framework_check['compliant_phases'])}")
        
        # Calculate overall assessment
        if critical_count > 0 or framework_critical_count > 0:
            merged["overall_assessment"] = "CRITICAL_VIOLATIONS"
            merged["risk_score"] = 90 + (critical_count * 2) + (framework_critical_count * 2)
        elif high_risk_count > 0 or framework_high_count > 0:
            merged["overall_assessment"] = "NEEDS_REVIEW"
            merged["risk_score"] = 60 + (high_risk_count * 5) + (framework_high_count * 3)
        else:
            merged["overall_assessment"] = ai_analysis.get("overall_assessment", "COMPLIANT")
            merged["risk_score"] = ai_analysis.get("risk_score", 20)
        
        # Add recommended actions
        if critical_count > 0:
            merged["recommended_actions"].append("IMMEDIATE ESCALATION - Critical ABPI violations detected")
            merged["recommended_actions"].append("Do NOT finalize call record until violations addressed")
        
        if framework_critical_count > 0:
            merged["recommended_actions"].append("FRAMEWORK FAILURE - Missing critical phases (e.g., no commitment secured)")
            merged["recommended_actions"].append("Rep coaching required on 6-phase methodology")
        
        if high_risk_count > 0 or framework_high_count > 0:
            merged["recommended_actions"].append("Review with manager before finalizing")
        
        # Add AI recommendations
        for action in ai_analysis.get("required_actions", []):
            if action not in merged["recommended_actions"]:
                merged["recommended_actions"].append(action)
        
        return merged
