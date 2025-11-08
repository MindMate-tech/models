"""
Session Analyzer Service
Orchestrates cognitive analysis using Dedalus agents and memory metrics
"""
import sys
import os
from typing import Dict, List, Optional
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dedalus_labs import AsyncDedalus, DedalusRunner
from tools.cognitive_assessment import CognitiveTools
from tools.memory_metrics_engine import MemoryMetricsEngine
from config.settings import settings


class SessionAnalyzer:
    """
    Main service for analyzing patient sessions

    Integrates:
    - Dedalus AI for memory extraction
    - Cognitive assessment tools
    - Memory metrics engine
    """

    def __init__(self):
        # Initialize Dedalus
        os.environ['DEDALUS_API_KEY'] = settings.dedalus_api_key
        os.environ['ANTHROPIC_API_KEY'] = settings.anthropic_api_key

        self.client = AsyncDedalus()
        self.runner = DedalusRunner(self.client)

        # Initialize tools
        self.cognitive = CognitiveTools()
        self.memory_engine = MemoryMetricsEngine()

    async def analyze_session(
        self,
        session_data: Dict,
        patient_profile: Dict,
        previous_sessions: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Complete session analysis

        Args:
            session_data: Current session with transcript
            patient_profile: Patient info
            previous_sessions: Historical sessions for context

        Returns:
            Complete analysis with:
            - extracted_memories
            - cognitive_test_scores
            - memory_metrics
            - overall_score
            - doctor_alerts
        """

        transcript = session_data.get('transcript', '')
        patient_id = session_data.get('patient_id')

        print(f"\n{'='*60}")
        print(f"🧠 Analyzing Session for Patient: {patient_profile.get('name', patient_id)}")
        print(f"{'='*60}\n")

        # Step 1: Extract memories using Dedalus
        print("📝 Extracting memories from conversation...")
        extracted_memories = await self._extract_memories_with_ai(
            transcript,
            patient_profile
        )

        # Step 2: Run cognitive assessments
        print("🧪 Running cognitive assessments...")
        cognitive_scores = self._run_cognitive_tests(
            transcript,
            patient_profile
        )

        # Step 3: Calculate memory metrics
        print("📊 Calculating memory metrics...")
        memory_metrics = self.memory_engine.analyze_session_for_memory_metrics(
            transcript=transcript,
            patient_profile=patient_profile,
            extracted_memories=extracted_memories,
            previous_sessions=previous_sessions or []
        )

        # Step 4: Calculate overall score
        overall_score = self._calculate_overall_score(
            cognitive_scores,
            memory_metrics
        )

        # Step 5: Generate doctor alerts
        print("⚠️  Checking for risk factors...")
        doctor_alerts = self._generate_alerts(
            overall_score,
            cognitive_scores,
            memory_metrics,
            patient_profile
        )

        print(f"✅ Analysis complete! Overall score: {overall_score:.1%}\n")

        return {
            'session_id': session_data.get('session_id'),
            'patient_id': patient_id,
            'analyzed_at': datetime.utcnow().isoformat(),
            'transcript': transcript,
            'memories': extracted_memories,
            'cognitive_test_scores': cognitive_scores,
            'memory_metrics': memory_metrics,
            'overall_score': overall_score,
            'doctor_alerts': doctor_alerts,
            'notable_events': self._extract_notable_events(doctor_alerts),
            'requires_doctor_review': any(
                alert['severity'] in ['high', 'critical']
                for alert in doctor_alerts
            )
        }

    async def _extract_memories_with_ai(
        self,
        transcript: str,
        patient_profile: Dict
    ) -> List[Dict]:
        """
        Use Dedalus to extract structured memories from conversation
        """
        try:
            result = await self.runner.run(
                input=f"""Analyze this conversation with a dementia patient and extract any personal memories they discuss.

Patient: {patient_profile.get('name', 'Unknown')}

Conversation:
{transcript}

For each memory mentioned, extract:
- title: Brief title (2-5 words)
- description: What happened (1-2 sentences)
- dateapprox: Approximate date if mentioned (YYYY-MM-DD format, or null)
- location: Where it happened (or null)
- peopleinvolved: List of people mentioned (or empty array)
- emotional_tone: happy, sad, neutral, anxious, etc.
- tags: Relevant tags like "family", "travel", "childhood"
- significance_level: 1-5 (how important this memory seems to the patient)

Return as JSON array. If no clear memories discussed, return empty array.""",
                model="anthropic/claude-sonnet-4-20250514",
                stream=False
            )

            # Parse AI response (expecting JSON)
            import json
            try:
                memories = json.loads(result.final_output)
                if isinstance(memories, list):
                    return memories
            except:
                # Fallback: extract from response
                return self._fallback_memory_extraction(transcript)

        except Exception as e:
            print(f"⚠️  AI extraction failed: {e}")
            return self._fallback_memory_extraction(transcript)

    def _fallback_memory_extraction(self, transcript: str) -> List[Dict]:
        """Simple rule-based memory extraction if AI fails"""
        # Look for past-tense narrative patterns
        import re

        memories = []

        # Simple heuristic: sentences with past tense and personal references
        sentences = re.split(r'[.!?]+', transcript)

        past_indicators = ['was', 'were', 'went', 'visited', 'saw', 'remember', 'used to']

        for sentence in sentences:
            if any(word in sentence.lower() for word in past_indicators):
                if len(sentence.strip()) > 20:  # Meaningful length
                    memories.append({
                        'title': 'Past Event',
                        'description': sentence.strip()[:200],
                        'dateapprox': None,
                        'location': None,
                        'peopleinvolved': [],
                        'emotional_tone': 'neutral',
                        'tags': ['conversation'],
                        'significance_level': 2
                    })

        return memories[:5]  # Limit to 5

    def _run_cognitive_tests(
        self,
        transcript: str,
        patient_profile: Dict
    ) -> List[Dict]:
        """
        Run standard cognitive tests
        """
        now = datetime.now()
        current_date = {
            "year": str(now.year),
            "month": now.strftime("%B"),
            "day": now.strftime("%A")
        }

        # Use existing cognitive tools
        temporal_score = self.cognitive.score_temporal(transcript, current_date)
        recall_score = self.cognitive.score_recall(
            transcript,
            patient_profile.get('expected_info', {})
        )
        speech_analysis = self.cognitive.analyze_speech(transcript)

        return [
            {
                'test': 'temporal_orientation',
                'score': temporal_score * 10,
                'max_score': 10,
                'details': 'Awareness of current date/time'
            },
            {
                'test': 'personal_recall',
                'score': recall_score * 10,
                'max_score': 10,
                'details': 'Recall of personal information'
            },
            {
                'test': 'vocabulary_richness',
                'score': speech_analysis['vocabulary_richness'] * 10,
                'max_score': 10,
                'details': 'Language complexity and diversity'
            }
        ]

    def _calculate_overall_score(
        self,
        cognitive_scores: List[Dict],
        memory_metrics: Dict[str, float]
    ) -> float:
        """
        Calculate weighted overall cognitive score

        Weights:
        - Cognitive tests: 40%
        - Memory metrics: 60%
        """
        # Cognitive tests average
        if cognitive_scores:
            cog_avg = sum(
                s['score'] / s['max_score']
                for s in cognitive_scores
            ) / len(cognitive_scores)
        else:
            cog_avg = 0.5

        # Memory metrics average
        memory_avg = sum(memory_metrics.values()) / len(memory_metrics)

        # Weighted combination
        overall = (cog_avg * 0.4) + (memory_avg * 0.6)

        return round(overall, 3)

    def _generate_alerts(
        self,
        overall_score: float,
        cognitive_scores: List[Dict],
        memory_metrics: Dict[str, float],
        patient_profile: Dict
    ) -> List[Dict]:
        """
        Generate doctor alerts based on analysis
        """
        alerts = []

        # Critical overall decline
        if overall_score < 0.4:
            alerts.append({
                'type': 'critical_decline',
                'severity': 'critical',
                'message': f'Critical cognitive decline detected (score: {overall_score:.1%})',
                'score': overall_score
            })
        elif overall_score < 0.6:
            alerts.append({
                'type': 'moderate_decline',
                'severity': 'high',
                'message': f'Moderate cognitive decline (score: {overall_score:.1%})',
                'score': overall_score
            })

        # Check individual memory metrics
        for metric, score in memory_metrics.items():
            if score < 0.4:
                alerts.append({
                    'type': f'{metric}_impairment',
                    'severity': 'high',
                    'message': f'Significant {metric.replace("_", " ")} impairment (score: {score:.1%})',
                    'score': score
                })

        # Temporal disorientation (critical for dementia)
        temporal_test = next(
            (t for t in cognitive_scores if t['test'] == 'temporal_orientation'),
            None
        )
        if temporal_test and (temporal_test['score'] / temporal_test['max_score']) < 0.5:
            alerts.append({
                'type': 'temporal_disorientation',
                'severity': 'high',
                'message': 'Significant temporal disorientation detected',
                'score': temporal_test['score'] / temporal_test['max_score']
            })

        return alerts

    def _extract_notable_events(self, alerts: List[Dict]) -> List[str]:
        """Extract notable events from alerts for session summary"""
        return [alert['message'] for alert in alerts if alert['severity'] in ['high', 'critical']]
