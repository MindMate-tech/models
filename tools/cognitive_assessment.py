"""Cognitive assessment tools"""
import re
from typing import Dict

class CognitiveTools:
    
    @staticmethod
    def score_temporal(response: str, current_date: Dict) -> float:
        response_lower = response.lower()
        score = 0.0
        if current_date["year"] in response_lower: score += 0.33
        if current_date["month"].lower() in response_lower: score += 0.33
        if current_date["day"].lower() in response_lower: score += 0.34
        return round(score, 2)
    
    @staticmethod
    def score_recall(response: str, expected: Dict) -> float:
        response_lower = response.lower()
        score = 0.0
        items = 0
        
        family = expected.get('family_members', [])
        if family:
            items += 1
            mentioned = sum(1 for n in family if n.lower() in response_lower)
            score += (mentioned / len(family))
        
        profession = expected.get('profession', '')
        if profession:
            items += 1
            if profession.lower() in response_lower: score += 1
        
        return round(score / items if items > 0 else 0, 2)
    
    @staticmethod
    def analyze_speech(response: str) -> Dict:
        words = re.findall(r'\b\w+\b', response.lower())
        if not words:
            return {'vocabulary_richness': 0, 'word_count': 0, 'unique_words': 0}
        unique = set(words)
        return {
            'word_count': len(words),
            'unique_words': len(unique),
            'vocabulary_richness': round(len(unique) / len(words), 3)
        }
