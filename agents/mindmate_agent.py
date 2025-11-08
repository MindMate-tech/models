"""Main MindMate agent"""
import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dedalus_labs import AsyncDedalus, DedalusRunner
from tools.cognitive_assessment import CognitiveTools
from tools.mri_analysis import MRIAnalyzer

class MindMateAgent:
    
    def __init__(self):
        self.client = AsyncDedalus()
        self.runner = DedalusRunner(self.client)
        self.cognitive = CognitiveTools()
        self.mri = MRIAnalyzer()
    
    async def daily_checkin(self, patient_id: str, transcript: str, patient_profile: Dict) -> Dict:
        print(f"\n{'='*60}")
        print(f"🧠 Daily Check-in: {patient_profile.get('name', 'Patient')}")
        print(f"{'='*60}\n")
        
        # Cognitive assessment
        print("📊 Running cognitive assessment...")
        now = datetime.now()
        current_date = {
            "year": str(now.year),
            "month": now.strftime("%B"),
            "day": now.strftime("%A")
        }
        
        assessment = {
            'temporal_orientation': self.cognitive.score_temporal(transcript, current_date),
            'personal_recall': self.cognitive.score_recall(transcript, patient_profile.get('expected_info', {})),
            'speech_analysis': self.cognitive.analyze_speech(transcript),
            'timestamp': now.isoformat()
        }
        
        assessment['overall_score'] = (
            assessment['temporal_orientation'] * 0.4 +
            assessment['personal_recall'] * 0.4 +
            assessment['speech_analysis']['vocabulary_richness'] * 0.2
        )
        
        # Risk detection
        print("⚠️  Checking for risk factors...")
        risk_alerts = []
        
        if assessment['overall_score'] < 0.5:
            risk_alerts.append({
                'type': 'cognitive_decline',
                'severity': 'high',
                'message': 'Significant cognitive decline detected'
            })
        
        if assessment['temporal_orientation'] < 0.5:
            risk_alerts.append({
                'type': 'temporal_disorientation',
                'severity': 'medium',
                'message': 'Unable to recall current date/time'
            })
        
        # MRI context
        mri_context = ""
        if patient_profile.get('baseline_mri'):
            mri_context = patient_profile['baseline_mri'].get('clinical_summary', '')
        
        # Generate response
        print("💬 Generating response...")
        response = await self._generate_response(patient_profile, assessment, transcript, mri_context)
        
        print(f"\n✅ Check-in complete!")
        
        return {
            'assessment': assessment,
            'risk_alerts': risk_alerts,
            'conversation_response': response,
            'timestamp': now.isoformat()
        }
    
    async def _generate_response(self, profile: Dict, assessment: Dict, transcript: str, mri_context: str) -> str:
        try:
            result = await self.runner.run(
                input=f"""You are a compassionate AI companion for {profile.get('name')}.

Patient: Age {profile.get('age')}, Interests: {', '.join(profile.get('interests', []))}
{mri_context}

Recent conversation: {transcript[-300:]}
Cognitive score today: {assessment['overall_score']:.0%}

Generate a warm 2-3 sentence response that acknowledges what they shared and asks about their interests.""",
                model="anthropic/claude-sonnet-4-20250514",
                stream=False
            )
            return result.final_output
        except Exception as e:
            return f"Thank you for sharing, {profile.get('name')}. I enjoy our conversations. How are you feeling today?"
