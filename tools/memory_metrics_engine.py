"""
Memory Metrics Engine
Transforms cognitive assessments into 5 memory metric types with time-series data
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import re


@dataclass
class MemoryTestResult:
    """Individual memory test result"""
    test_type: str
    score: float  # 0.0 - 1.0
    max_score: float
    timestamp: datetime
    details: Optional[Dict] = None


class MemoryMetricsEngine:
    """
    Converts cognitive assessments and conversation analysis into 5 memory metrics:
    1. Short-term recall (0-5 minutes)
    2. Long-term recall (hours to days)
    3. Semantic memory (general knowledge)
    4. Episodic memory (personal events with context)
    5. Working memory (manipulation and sequencing)
    """

    def analyze_session_for_memory_metrics(
        self,
        transcript: str,
        patient_profile: Dict,
        extracted_memories: List[Dict],
        previous_sessions: Optional[List[Dict]] = None
    ) -> Dict[str, float]:
        """
        Comprehensive analysis of a session to extract all 5 memory scores

        Args:
            transcript: Conversation text
            patient_profile: Patient info with expected_info
            extracted_memories: Memories extracted by AI from conversation
            previous_sessions: Historical sessions for long-term recall

        Returns:
            Dict with scores for each memory type (0.0 - 1.0)
        """

        # 1. Short-term recall - Can they remember what was just discussed?
        short_term_score = self._test_short_term_recall(transcript)

        # 2. Long-term recall - Can they remember previous conversations?
        long_term_score = self._test_long_term_recall(
            transcript,
            previous_sessions or []
        )

        # 3. Semantic memory - General knowledge and facts
        semantic_score = self._test_semantic_memory(transcript)

        # 4. Episodic memory - Personal events with context (where, when, who)
        episodic_score = self._test_episodic_memory(
            extracted_memories,
            patient_profile
        )

        # 5. Working memory - Following conversation flow and complex tasks
        working_score = self._test_working_memory(transcript)

        return {
            'shortTermRecall': round(short_term_score, 3),
            'longTermRecall': round(long_term_score, 3),
            'semanticMemory': round(semantic_score, 3),
            'episodicMemory': round(episodic_score, 3),
            'workingMemory': round(working_score, 3)
        }

    def _test_short_term_recall(self, transcript: str) -> float:
        """
        Test ability to remember recent information (0-5 minutes ago in conversation)

        Indicators:
        - References to things just mentioned
        - Coherent follow-up responses
        - Not repeating same questions
        """
        score = 0.5  # Baseline

        # Check for repetitive questions (indicates poor short-term)
        questions = re.findall(r'\?[^\?]*\?', transcript.lower())
        if len(questions) > 1:
            # Check for duplicates
            unique_ratio = len(set(questions)) / len(questions)
            score += unique_ratio * 0.3
        else:
            score += 0.3

        # Check for coherent follow-ups (responding appropriately to previous statement)
        lines = [l.strip() for l in transcript.split('\n') if l.strip()]
        coherent_responses = 0
        for i in range(1, min(len(lines), 10)):
            if self._is_coherent_response(lines[i-1], lines[i]):
                coherent_responses += 1

        if len(lines) > 1:
            coherence_ratio = coherent_responses / (len(lines) - 1)
            score += coherence_ratio * 0.2

        return min(1.0, max(0.0, score))

    def _test_long_term_recall(
        self,
        transcript: str,
        previous_sessions: List[Dict]
    ) -> float:
        """
        Test ability to recall information from previous sessions

        Indicators:
        - References to past conversations
        - Consistent personal information across sessions
        - Memory of family members, events discussed before
        """
        if not previous_sessions:
            return 0.5  # Neutral if no history

        score = 0.5

        # Extract references to past events
        past_indicators = [
            'remember', 'last time', 'yesterday', 'last week',
            'you told me', 'we talked about', 'mentioned before'
        ]

        past_references = sum(
            1 for indicator in past_indicators
            if indicator in transcript.lower()
        )

        # Score based on past references (max 0.3)
        score += min(0.3, past_references * 0.1)

        # Check consistency with previous sessions (max 0.2)
        # Compare mentioned names, places, events
        current_entities = self._extract_entities(transcript)

        consistency_count = 0
        for prev_session in previous_sessions[-3:]:  # Last 3 sessions
            prev_transcript = prev_session.get('transcript', '')
            prev_entities = self._extract_entities(prev_transcript)

            # Count consistent entities
            overlap = len(current_entities & prev_entities)
            if overlap > 0:
                consistency_count += 1

        if previous_sessions:
            consistency_ratio = consistency_count / min(3, len(previous_sessions))
            score += consistency_ratio * 0.2

        return min(1.0, max(0.0, score))

    def _test_semantic_memory(self, transcript: str) -> float:
        """
        Test general knowledge and facts (not personal)

        Indicators:
        - Correct use of common words
        - Knowledge of current events, dates, places
        - Understanding of concepts and categories
        """
        score = 0.5

        # Check for temporal orientation
        temporal_words = ['today', 'monday', 'tuesday', 'january', 'november', '2025', '2024']
        temporal_correct = sum(1 for word in temporal_words if word in transcript.lower())
        score += min(0.2, temporal_correct * 0.05)

        # Check vocabulary richness (indicates semantic memory)
        words = re.findall(r'\b\w+\b', transcript.lower())
        if len(words) > 20:
            unique_ratio = len(set(words)) / len(words)
            score += unique_ratio * 0.3
        else:
            score += 0.1

        return min(1.0, max(0.0, score))

    def _test_episodic_memory(
        self,
        extracted_memories: List[Dict],
        patient_profile: Dict
    ) -> float:
        """
        Test personal autobiographical memory with context (who, what, where, when)

        Indicators:
        - Rich details about personal events
        - Contextual information (time, place, people)
        - Emotional associations
        """
        if not extracted_memories:
            return 0.3  # Low if no memories extracted

        score = 0.3

        for memory in extracted_memories:
            # Award points for contextual richness
            context_score = 0

            if memory.get('dateapprox'):
                context_score += 0.2
            if memory.get('location'):
                context_score += 0.2
            if memory.get('peopleinvolved'):
                context_score += 0.2
            if memory.get('emotional_tone'):
                context_score += 0.2
            if len(memory.get('description', '')) > 50:
                context_score += 0.2

            # Average across memories
            score += context_score / len(extracted_memories)

        return min(1.0, max(0.0, score))

    def _test_working_memory(self, transcript: str) -> float:
        """
        Test ability to hold and manipulate information

        Indicators:
        - Following multi-step conversations
        - Responding to complex questions
        - Maintaining topic continuity
        """
        score = 0.5

        # Check sentence complexity (longer sentences = better working memory)
        sentences = re.split(r'[.!?]+', transcript)
        if sentences:
            avg_words_per_sentence = sum(
                len(s.split()) for s in sentences
            ) / len(sentences)

            # Optimal range: 10-20 words per sentence
            if 10 <= avg_words_per_sentence <= 20:
                score += 0.3
            elif 8 <= avg_words_per_sentence < 10:
                score += 0.2
            elif avg_words_per_sentence < 5:
                score += 0.0  # Very short = poor working memory

        # Check for logical flow between statements
        lines = [l.strip() for l in transcript.split('\n') if l.strip()]
        if len(lines) > 3:
            # Simple heuristic: pronouns and conjunctions indicate connection
            connectors = ['and', 'but', 'so', 'because', 'then', 'also']
            connector_count = sum(
                1 for line in lines
                for word in connectors
                if word in line.lower()
            )
            score += min(0.2, connector_count * 0.05)

        return min(1.0, max(0.0, score))

    def _is_coherent_response(self, prev_line: str, curr_line: str) -> bool:
        """Check if current line is a coherent response to previous"""
        # Simple heuristic: look for pronouns, agreement, or topic words
        prev_words = set(re.findall(r'\b\w+\b', prev_line.lower()))
        curr_words = set(re.findall(r'\b\w+\b', curr_line.lower()))

        # Shared content words (excluding common stop words)
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'i', 'you'}
        shared = (prev_words & curr_words) - stop_words

        return len(shared) > 0

    def _extract_entities(self, text: str) -> set:
        """
        Simple entity extraction (names, places)
        For MVP - uses capitalized words as proxy for entities
        """
        # Find capitalized words (likely names/places)
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        return set(entities)

    def generate_time_series(
        self,
        sessions: List[Dict],
        days_back: int = 30
    ) -> Dict[str, List[Dict]]:
        """
        Generate time-series data for all 5 memory metrics from historical sessions

        Args:
            sessions: List of session dicts with 'cognitive_test_scores' and 'session_date'
            days_back: How many days to include

        Returns:
            Dict with 5 keys, each containing list of {timestamp, score} points
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)

        # Filter sessions within timeframe
        recent_sessions = [
            s for s in sessions
            if datetime.fromisoformat(s.get('session_date', '2000-01-01').replace('Z', ''))
            >= cutoff_date
        ]

        # Sort by date
        recent_sessions.sort(
            key=lambda s: datetime.fromisoformat(s.get('session_date', '2000-01-01').replace('Z', ''))
        )

        # Build time series for each metric
        time_series = {
            'shortTermRecall': [],
            'longTermRecall': [],
            'semanticMemory': [],
            'episodicMemory': [],
            'workingMemory': []
        }

        for session in recent_sessions:
            timestamp = session.get('session_date')
            scores = session.get('ai_extracted_data', {}).get('memory_metrics', {})

            for metric in time_series.keys():
                if metric in scores:
                    time_series[metric].append({
                        'timestamp': timestamp,
                        'score': scores[metric]
                    })

        return time_series

    def calculate_memory_retention_rate(
        self,
        sessions: List[Dict],
        days_back: int = 7
    ) -> float:
        """
        Calculate overall memory retention rate from recent sessions

        Weighted average favoring long-term and episodic memory
        """
        time_series = self.generate_time_series(sessions, days_back)

        # Weights for different memory types
        weights = {
            'shortTermRecall': 0.15,
            'longTermRecall': 0.30,
            'semanticMemory': 0.15,
            'episodicMemory': 0.30,
            'workingMemory': 0.10
        }

        weighted_scores = []

        for metric, weight in weights.items():
            scores = [point['score'] for point in time_series[metric]]
            if scores:
                avg_score = sum(scores) / len(scores)
                weighted_scores.append(avg_score * weight)

        if weighted_scores:
            return round(sum(weighted_scores), 3)
        else:
            return 0.5  # Neutral if no data


# Convenience function
def analyze_memory_from_session(
    transcript: str,
    patient_profile: Dict,
    extracted_memories: List[Dict]
) -> Dict[str, float]:
    """Quick analysis wrapper"""
    engine = MemoryMetricsEngine()
    return engine.analyze_session_for_memory_metrics(
        transcript,
        patient_profile,
        extracted_memories
    )
