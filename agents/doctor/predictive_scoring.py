"""
Predictive risk scoring for cognitive decline
Uses simple linear regression on session history trends
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from db.supabase_client import get_supabase


class PredictiveRiskScorer:
    """
    Predicts future cognitive decline based on session history

    Uses linear regression on score trends + caching for performance
    """

    def __init__(self, cache_ttl_hours: int = 24):
        """
        Initialize predictor

        Args:
            cache_ttl_hours: Time-to-live for cached predictions
        """
        self.supabase = get_supabase()
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self.cache = {}
        self.last_computed = None

    def _calculate_trend(self, scores: List[float]) -> Tuple[float, str]:
        """
        Calculate trend from score history using simple linear regression

        Args:
            scores: List of scores over time

        Returns:
            Tuple of (slope, trend_label)
        """
        if len(scores) < 2:
            return 0.0, "insufficient_data"

        n = len(scores)
        x = list(range(n))  # Time points
        y = scores  # Scores

        # Simple linear regression: y = mx + b
        x_mean = sum(x) / n
        y_mean = sum(y) / n

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator

        # Classify trend
        if slope < -5:
            trend = "rapid_decline"
        elif slope < -2:
            trend = "moderate_decline"
        elif slope < -0.5:
            trend = "mild_decline"
        elif slope > 2:
            trend = "improving"
        elif slope > 0.5:
            trend = "mild_improvement"
        else:
            trend = "stable"

        return slope, trend

    def _predict_next_month_score(self, scores: List[float], slope: float) -> float:
        """
        Predict score 30 days from now based on trend

        Args:
            scores: Historical scores
            slope: Calculated slope

        Returns:
            Predicted score
        """
        if not scores:
            return 50.0  # Default assumption

        current_score = scores[-1]
        predicted_score = current_score + (slope * 4)  # ~4 sessions in a month

        # Clamp to 0-100 range
        return max(0.0, min(100.0, predicted_score))

    def _calculate_decline_probability(self, slope: float, current_score: float, sessions_count: int) -> float:
        """
        Calculate probability of significant decline (>20%)

        Args:
            slope: Trend slope
            current_score: Current average score
            sessions_count: Number of sessions for confidence

        Returns:
            Probability of decline (0-1)
        """
        # Base probability from slope
        if slope < -5:
            base_prob = 0.9
        elif slope < -2:
            base_prob = 0.7
        elif slope < -0.5:
            base_prob = 0.5
        elif slope < 0:
            base_prob = 0.3
        else:
            base_prob = 0.1

        # Adjust for current score (lower scores = higher risk)
        if current_score < 30:
            score_factor = 1.3
        elif current_score < 50:
            score_factor = 1.1
        else:
            score_factor = 0.9

        # Adjust for data confidence
        if sessions_count < 3:
            confidence_factor = 0.7  # Lower confidence
        elif sessions_count < 5:
            confidence_factor = 0.9
        else:
            confidence_factor = 1.0

        probability = base_prob * score_factor * confidence_factor

        return min(1.0, max(0.0, probability))

    def predict_patient_risk(self, patient_id: str) -> Dict:
        """
        Predict future risk for a specific patient

        Args:
            patient_id: Patient UUID

        Returns:
            Prediction details
        """
        # Get patient sessions
        sessions = (
            self.supabase.table("sessions")
            .select("overall_score, session_date")
            .eq("patient_id", patient_id)
            .order("session_date", desc=False)
            .execute()
        )

        if not sessions.data:
            return {
                "patient_id": patient_id,
                "prediction": "insufficient_data",
                "decline_probability": 0.0,
                "reasoning": "No session history available"
            }

        # Extract scores
        scores = [s.get('overall_score', 0) for s in sessions.data if s.get('overall_score') is not None]

        if not scores:
            return {
                "patient_id": patient_id,
                "prediction": "insufficient_data",
                "decline_probability": 0.0,
                "reasoning": "No score data available"
            }

        # Calculate trend
        slope, trend = self._calculate_trend(scores)
        current_score = sum(scores) / len(scores)
        predicted_score = self._predict_next_month_score(scores, slope)
        decline_prob = self._calculate_decline_probability(slope, current_score, len(scores))

        # Generate reasoning
        reasoning_parts = []

        if len(scores) < 3:
            reasoning_parts.append(f"Limited data ({len(scores)} sessions) reduces prediction confidence")

        if trend == "rapid_decline":
            reasoning_parts.append(f"Rapid declining trend ({slope:.1f} points per session)")
        elif trend == "moderate_decline":
            reasoning_parts.append(f"Moderate declining trend ({slope:.1f} points per session)")
        elif trend == "mild_decline":
            reasoning_parts.append(f"Mild declining trend ({slope:.1f} points per session)")
        elif trend == "stable":
            reasoning_parts.append("Stable performance over recent sessions")
        elif trend == "improving":
            reasoning_parts.append(f"Improving trend ({slope:.1f} points per session)")

        if current_score < 50:
            reasoning_parts.append(f"Current average score ({current_score:.1f}%) below threshold")

        reasoning = ". ".join(reasoning_parts)

        return {
            "patient_id": patient_id,
            "current_score": current_score,
            "predicted_next_month": predicted_score,
            "decline_probability": decline_prob,
            "trend": trend,
            "slope": slope,
            "sessions_analyzed": len(scores),
            "reasoning": reasoning,
            "confidence": "high" if len(scores) >= 5 else "medium" if len(scores) >= 3 else "low"
        }

    def predict_all_patients(self, min_decline_prob: float = 0.4) -> List[Dict]:
        """
        Predict decline risk for all patients

        Args:
            min_decline_prob: Minimum probability to include in results

        Returns:
            List of patients with decline predictions
        """
        # Check cache
        if self.last_computed and datetime.now() - self.last_computed < self.cache_ttl:
            print(f"✅ Using cached predictions (age: {datetime.now() - self.last_computed})")
            return [p for p in self.cache.get('predictions', []) if p['decline_probability'] >= min_decline_prob]

        print(f"🔄 Computing new predictions...")

        # Get all patients
        patients_result = self.supabase.table("patients").select("patient_id, name").execute()

        predictions = []
        for patient in patients_result.data:
            prediction = self.predict_patient_risk(patient['patient_id'])
            prediction['name'] = patient['name']

            if prediction['decline_probability'] >= min_decline_prob:
                predictions.append(prediction)

        # Sort by decline probability
        predictions.sort(key=lambda x: x['decline_probability'], reverse=True)

        # Cache results
        self.cache['predictions'] = predictions
        self.last_computed = datetime.now()

        print(f"✅ Computed {len(predictions)} predictions")

        return predictions

    def get_cache_info(self) -> Dict:
        """Get cache status information"""
        if not self.last_computed:
            return {"cached": False, "age": None}

        age = datetime.now() - self.last_computed
        is_fresh = age < self.cache_ttl

        return {
            "cached": True,
            "is_fresh": is_fresh,
            "age_minutes": age.total_seconds() / 60,
            "ttl_hours": self.cache_ttl.total_seconds() / 3600,
            "prediction_count": len(self.cache.get('predictions', []))
        }


# Global predictor instance
predictor = PredictiveRiskScorer()
