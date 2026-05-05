"""nCompliance and Framework Loader - Markdown VersionnnnnnnnnnnnnnnnnnnnnnnnReads .md files for guidelines and framework - simple, Git-friendly, no dependenciesnnn"""

import os
from typing import Dict, List, Optional


class ComplianceChecker:
    """
    Loads compliance guidelines from .md files and validates call records
    """
    
    def __init__(self, compliance_file: str = "compliance/EU_Compliance_Guidelines.md", region: str = "EU"):
        self.region = region
        self.compliance_file = compliance_file
        self.guidelines = self._load_guidelines()
        
    def _load_guidelines(self) -> str:
        """Load compliance guidelines from markdown file"""
        if not os.path.exists(self.compliance_file):
            print(f"[WARNING] Compliance file not found: {self.compliance_file}")
            return f"No compliance guidelines loaded from {self.compliance_file}"
        
        try:
            with open(self.compliance_file, 'r', encoding='utf-8') as f:
                guidelines_text = f.read()
            
            print(f"✅ Loaded {self.region} compliance guidelines: {len(guidelines_text)} chars")
            return guidelines_text
                
        except Exception as e:
            print(f"[WARNING] Error loading compliance guidelines: {e}")
            return f"Error loading guidelines: {str(e)}"
    
    def check_compliance(self, call_data: dict) -> Dict[str, List[Dict]]:
        """
        Check call data against compliance guidelines
        Returns: {
            "critical": [...],
            "high_risk": [...],
            "medium_risk": [...],
            "warnings": [...]
        }
        """
        
        violations = {
            "critical": [],
            "high_risk": [],
            "medium_risk": [],
            "warnings": []
        }
        
        # Extract call content for analysis
        brand = call_data.get("brand", "").lower()
        objectives = " ".join(call_data.get("call_objectives", [])).lower()
        discussion = " ".join(call_data.get("key_discussion_points", [])).lower()
        agreements = " ".join(call_data.get("agreements_reached", [])).lower()
        
        full_text = f"{objectives} {discussion} {agreements}"
        
        # Critical violations
        if "off-label" in full_text or "unapproved" in full_text:
            violations["critical"].append({
                "rule": "OFF-LABEL PROMOTION",
                "description": "Potential discussion of unapproved indications",
                "reference": "EU Compliance Guidelines - Critical Violations"
            })
        
        if "cash" in full_text or "payment" in full_text or "incentive" in full_text:
            violations["critical"].append({
                "rule": "MONETARY INCENTIVES",
                "description": "Potential financial inducements mentioned",
                "reference": "EU Compliance Guidelines - Critical Violations"
            })
        
        # High-risk issues
        if "versus" in full_text or "vs" in full_text or "compared to" in full_text or "better than" in full_text:
            violations["high_risk"].append({
                "rule": "COMPARATIVE CLAIMS",
                "description": "Comparison to competitor products detected",
                "reference": "EU Compliance Guidelines - High-Risk Issues",
                "action": "Verify head-to-head trial data exists"
            })
        
        if "child" in full_text or "pediatric" in full_text or "under 12" in full_text:
            violations["high_risk"].append({
                "rule": "PEDIATRIC DOSING",
                "description": "Pediatric population mentioned",
                "reference": "EU Compliance Guidelines - High-Risk Issues",
                "action": "Verify pediatric indication approval"
            })
        
        if "pregnant" in full_text or "pregnancy" in full_text or "nursing" in full_text:
            violations["high_risk"].append({
                "rule": "PREGNANCY/NURSING",
                "description": "Pregnancy or nursing mentioned",
                "reference": "EU Compliance Guidelines - High-Risk Issues",
                "action": "Ensure label warnings referenced"
            })
        
        # Medium-risk issues
        if "twice daily" in full_text or "three times" in full_text:
            violations["medium_risk"].append({
                "rule": "DOSING FREQUENCY",
                "description": "Non-standard dosing frequency mentioned",
                "reference": "EU Compliance Guidelines - Medium-Risk Issues",
                "action": "Verify matches approved dosing schedule"
            })
        
        # Documentation warnings
        if not call_data.get("onekey_id"):
            violations["warnings"].append({
                "rule": "DOCUMENTATION",
                "description": "Missing HCP OneKey ID",
                "reference": "EU Compliance Guidelines - Documentation Requirements"
            })
        
        if not call_data.get("call_objectives"):
            violations["warnings"].append({
                "rule": "DOCUMENTATION",
                "description": "No call objectives documented",
                "reference": "EU Compliance Guidelines - Documentation Requirements"
            })
        
        return violations
