"""Patient-facing agent for check-ins and monitoring"""
import asyncio
from typing import Dict, Optional
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dedalus_labs import AsyncDedalus, DedalusRunner
from tools.cognitive_assessment import CognitiveTools
from tools.mri_analysis import MRIAnalyzer
from config.settings import settings

class PatientAgent:
    """Agent for patient interactions and monitoring"""
    
    def __init__(self):
        # Explicitly pass API key
        os.environ['DEDALUS_API_KEY'] = settings.dedalus_api_key
        os.environ['ANTHROPIC_API_KEY'] = settings.anthropic_api_key
        
        self.client = AsyncDedalus()
        self.runner = DedalusRunner(self.client)
        self.cognitive = CognitiveTools()
        self.mri = MRIAnalyzer()
    
    async def daily_checkin(
        self,
        patient_id: str,
        transcript: str,
        patient_profile: Dict,
        include_mri: bool = True
    ) -> Dict:
        """Comprehensive daily check-in with cognitive assessment"""
        
        print(f"\n{'='*60}")
        print(f"🧠 Daily Check-in: {patient_profile.get('name', 'Patient')}")
        print(f"{'='*60}\n")
        
        print("📊 Running cognitive assessment...")
        now = datetime.now()
        current_date = {
            "year": str(now.year),
            "month": now.strftime("%B"),
            "day": now.strftime("%A")
        }
        
        assessment = {
            'temporal_orientation': self.cognitive.score_temporal(transcript, current_date),
            'personal_recall': self.cognitive.score_recall(
                transcript,
                patient_profile.get('expected_info', {})
            ),
            'speech_analysis': self.cognitive.analyze_speech(transcript),
            'timestamp': now.isoformat()
        }
        
        # Calculate overall score
        assessment['overall_score'] = (
            assessment['temporal_orientation'] * 0.4 +
            assessment['personal_recall'] * 0.4 +
            assessment['speech_analysis']['vocabulary_richness'] * 0.2
        )
        
        # 2. Risk detection
        print("⚠️  Checking for risk factors...")
        risk_alerts = self._detect_risks(assessment, patient_profile)
        
        # 3. MRI context (if available)
        mri_context = ""
        if include_mri and patient_profile.get('baseline_mri'):
            mri_context = patient_profile['baseline_mri'].get('clinical_summary', '')
            print(f"🧠 MRI Context: {mri_context}")
        
        # 4. Generate empathetic response
        print("💬 Generating personalized response...")
        response = await self._generate_response(
            patient_profile,
            assessment,
            transcript,
            mri_context
        )
        
        print(f"\n✅ Check-in complete!")
        
        return {
            'patient_id': patient_id,
            'assessment': assessment,
            'risk_alerts': risk_alerts,
            'conversation_response': response,
            'mri_context': mri_context,
            'timestamp': now.isoformat(),
            'requires_doctor_review': len([a for a in risk_alerts if a['severity'] == 'high']) > 0
        }
    
    def _detect_risks(self, assessment: Dict, profile: Dict) -> list:
        """Detect risk factors from assessment"""
        risks = []
        
        if assessment['overall_score'] < 0.5:
            risks.append({
                'type': 'cognitive_decline',
                'severity': 'high',
                'message': 'Significant cognitive decline detected',
                'score': assessment['overall_score'],
                'threshold': 0.5
            })
        
        if assessment['temporal_orientation'] < 0.5:
            risks.append({
                'type': 'temporal_disorientation',
                'severity': 'medium',
                'message': 'Unable to recall current date/time accurately',
                'score': assessment['temporal_orientation']
            })
        
        if assessment['personal_recall'] < 0.3:
            risks.append({
                'type': 'memory_impairment',
                'severity': 'high',
                'message': 'Severe difficulty recalling personal information',
                'score': assessment['personal_recall']
            })
        
        if assessment['speech_analysis']['vocabulary_richness'] < 0.4:
            risks.append({
                'type': 'speech_decline',
                'severity': 'low',
                'message': 'Reduced vocabulary diversity',
                'score': assessment['speech_analysis']['vocabulary_richness']
            })
        
        return risks
    
    async def analyze_speech(
        self,
        audio_file: Optional[str] = None,
        transcript: Optional[str] = None
    ) -> Dict:
        """Analyze speech patterns from audio or transcript"""
        
        if audio_file and not transcript:
            transcript = await self._transcribe_audio(audio_file)
        
        if not transcript:
            return {"error": "No transcript or audio provided"}
        
        analysis = self.cognitive.analyze_speech(transcript)
        
        return {
            'transcript': transcript,
            'analysis': analysis,
            'concerns': self._detect_speech_concerns(analysis),
            'processed_at': datetime.now().isoformat()
        }
    
    async def _transcribe_audio(self, audio_file: str) -> str:
        """Convert audio to text using Whisper"""
        try:
            from tools.speech_recognition import SpeechRecognizer
            recognizer = SpeechRecognizer()
            result = recognizer.transcribe(audio_file)
            return result['text']
        except:
            return "[Audio transcription pending - Whisper not loaded]"
    
    def _detect_speech_concerns(self, analysis: Dict) -> list:
        """Detect concerning speech patterns"""
        concerns = []
        
        if analysis['vocabulary_richness'] < 0.5:
            concerns.append("Low vocabulary diversity")
        
        if analysis['word_count'] < 20:
            concerns.append("Very brief responses - possible withdrawal")
        
        if analysis['word_count'] > 200 and analysis['unique_words'] < 50:
            concerns.append("Repetitive speech patterns")
        
        return concerns
    
    async def _generate_response(
        self,
        profile: Dict,
        assessment: Dict,
        transcript: str,
        mri_context: str
    ) -> str:
        """Generate empathetic, personalized response"""
        
        try:
            result = await self.runner.run(
                input=f"""You are a compassionate AI companion for {profile.get('name', 'the patient')}.

Patient Context:
- Age: {profile.get('age')}
- Interests: {', '.join(profile.get('interests', []))}
- {mri_context}

Recent Conversation: {transcript[-300:]}

Cognitive Performance Today: {assessment['overall_score']:.0%}

Generate a warm, supportive 2-3 sentence response that acknowledges what they shared.""",
                model="anthropic/claude-sonnet-4-20250514",
                stream=False
            )
            return result.final_output
            
        except Exception as e:
            print(f"⚠️  LLM Error: {e}")
            name = profile.get('name', 'friend')
            interests = profile.get('interests', ['your day'])
            return f"Thank you for sharing with me today, {name}. I always enjoy our conversations. How are your {interests[0] if interests else 'activities'} going?"
