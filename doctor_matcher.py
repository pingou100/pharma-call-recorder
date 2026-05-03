"""
Doctor disambiguation module with fuzzy matching
Handles partial names, typos, and multi-criteria matching
"""

from rapidfuzz import fuzz, process
from typing import List, Dict, Optional, Tuple
import json


class DoctorMatcher:
    """
    Fuzzy matching for doctor disambiguation
    Matches on: first name, last name, specialty, hospital, city
    Returns ranked candidates with confidence scores
    """
    
    def __init__(self, doctors_data: List[Dict]):
        self.doctors = doctors_data
        
    def match(self, 
              query: str = None,
              first_name: str = None,
              last_name: str = None,
              specialty: str = None,
              hospital: str = None,
              city: str = None,
              min_confidence: float = 60.0,
              max_results: int = 5) -> List[Dict]:
        """
        Fuzzy match doctors based on available criteria
        
        Args:
            query: Free-form text (e.g., "Dr. Dubois from Charleroi")
            first_name: First name to match
            last_name: Last name to match
            specialty: Specialty to match
            hospital: Hospital to match
            city: City to match
            min_confidence: Minimum confidence score (0-100)
            max_results: Maximum number of results to return
            
        Returns:
            List of doctors with confidence scores, sorted by relevance
        """
        
        if not any([query, first_name, last_name, specialty, hospital, city]):
            return []
        
        # Score each doctor
        scored_doctors = []
        for doctor in self.doctors:
            score = self._calculate_match_score(
                doctor, query, first_name, last_name, specialty, hospital, city
            )
            
            if score >= min_confidence:
                doctor_with_score = doctor.copy()
                doctor_with_score['confidence'] = round(score, 2)
                doctor_with_score['full_name'] = f"Dr. {doctor['first_name']} {doctor['last_name']}"
                scored_doctors.append(doctor_with_score)
        
        # Sort by confidence (highest first)
        scored_doctors.sort(key=lambda x: x['confidence'], reverse=True)
        
        return scored_doctors[:max_results]
    
    def get_by_onekey_id(self, onekey_id: str) -> Optional[Dict]:
        """
        Get doctor by exact OneKey ID
        Used when rep confirms a specific doctor
        """
        for doctor in self.doctors:
            if doctor['onekey_id'] == onekey_id:
                result = doctor.copy()
                result['full_name'] = f"Dr. {doctor['first_name']} {doctor['last_name']}"
                return result
        return None
    
    def _calculate_match_score(self, 
                               doctor: Dict,
                               query: str,
                               first_name: str,
                               last_name: str,
                               specialty: str,
                               hospital: str,
                               city: str) -> float:
        """
        Calculate weighted match score for a doctor
        """
        
        scores = []
        weights = []
        
        # Last name matching (highest weight - 40%)
        if last_name:
            score = fuzz.ratio(last_name.lower(), doctor['last_name'].lower())
            scores.append(score)
            weights.append(0.40)
        
        # First name matching (30%)
        if first_name:
            score = fuzz.ratio(first_name.lower(), doctor['first_name'].lower())
            scores.append(score)
            weights.append(0.30)
        
        # Hospital matching (15%)
        if hospital:
            score = fuzz.partial_ratio(hospital.lower(), doctor['hospital'].lower())
            scores.append(score)
            weights.append(0.15)
        
        # City matching (10%)
        if city:
            score = fuzz.ratio(city.lower(), doctor['city'].lower())
            scores.append(score)
            weights.append(0.10)
        
        # Specialty matching (5%)
        if specialty:
            score = fuzz.partial_ratio(specialty.lower(), doctor['specialty'].lower())
            scores.append(score)
            weights.append(0.05)
        
        # Free-form query matching (if provided)
        if query:
            # Match against full name
            full_name = f"{doctor['first_name']} {doctor['last_name']}"
            name_score = fuzz.partial_ratio(query.lower(), full_name.lower())
            
            # Match against hospital
            hospital_score = fuzz.partial_ratio(query.lower(), doctor['hospital'].lower())
            
            # Match against city
            city_score = fuzz.partial_ratio(query.lower(), doctor['city'].lower())
            
            # Take the best match from query
            query_score = max(name_score, hospital_score, city_score)
            scores.append(query_score)
            weights.append(0.20)
        
        # Calculate weighted average
        if not scores:
            return 0.0
        
        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        # Weighted score
        final_score = sum(s * w for s, w in zip(scores, normalized_weights))
        
        return final_score


def load_doctors(filepath: str = "doctors.json") -> List[Dict]:
    """Load doctors from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)
