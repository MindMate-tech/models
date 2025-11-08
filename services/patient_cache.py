"""
Patient Data Cache
Simple in-memory cache for quick dashboard retrieval
"""
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import threading


@dataclass
class CachedPatientData:
    """Cached patient dashboard data"""
    patient_id: str
    patient_name: str
    last_updated: datetime
    brain_regions: Dict[str, float]
    memory_metrics: Dict[str, List[Dict]]
    recent_sessions: List[Dict]
    overall_cognitive_score: float
    memory_retention_rate: float
    cached_at: datetime
    ttl_expires_at: datetime


class PatientDataCache:
    """
    Thread-safe in-memory cache for patient dashboard data

    Features:
    - TTL-based expiration (default 24 hours)
    - Thread-safe operations
    - Automatic cleanup of expired entries
    """

    def __init__(self, default_ttl_hours: int = 24):
        self._cache: Dict[str, CachedPatientData] = {}
        self._lock = threading.Lock()
        self.default_ttl_hours = default_ttl_hours

    def get(self, patient_id: str) -> Optional[Dict]:
        """
        Retrieve patient data from cache

        Returns:
            Patient data dict or None if not found/expired
        """
        with self._lock:
            if patient_id not in self._cache:
                return None

            cached_data = self._cache[patient_id]

            # Check if expired
            if datetime.utcnow() > cached_data.ttl_expires_at:
                del self._cache[patient_id]
                return None

            # Convert to dict for API response
            data_dict = asdict(cached_data)

            # Convert datetime objects to ISO strings
            data_dict['last_updated'] = data_dict['last_updated'].isoformat()
            data_dict['cached_at'] = data_dict['cached_at'].isoformat()
            del data_dict['ttl_expires_at']  # Internal field

            return data_dict

    def set(
        self,
        patient_id: str,
        patient_data: Dict,
        ttl_hours: Optional[int] = None
    ) -> None:
        """
        Store patient data in cache

        Args:
            patient_id: Patient UUID
            patient_data: Complete dashboard data
            ttl_hours: Custom TTL in hours (uses default if None)
        """
        ttl = ttl_hours or self.default_ttl_hours
        now = datetime.utcnow()

        # Ensure datetime fields are datetime objects
        if isinstance(patient_data.get('last_updated'), str):
            patient_data['last_updated'] = datetime.fromisoformat(
                patient_data['last_updated'].replace('Z', '')
            )

        cached_entry = CachedPatientData(
            patient_id=patient_id,
            patient_name=patient_data['patient_name'],
            last_updated=patient_data['last_updated'],
            brain_regions=patient_data['brain_regions'],
            memory_metrics=patient_data['memory_metrics'],
            recent_sessions=patient_data['recent_sessions'],
            overall_cognitive_score=patient_data['overall_cognitive_score'],
            memory_retention_rate=patient_data['memory_retention_rate'],
            cached_at=now,
            ttl_expires_at=now + timedelta(hours=ttl)
        )

        with self._lock:
            self._cache[patient_id] = cached_entry

    def invalidate(self, patient_id: str) -> bool:
        """
        Remove patient data from cache

        Returns:
            True if entry was removed, False if not found
        """
        with self._lock:
            if patient_id in self._cache:
                del self._cache[patient_id]
                return True
            return False

    def clear_all(self) -> int:
        """
        Clear entire cache

        Returns:
            Number of entries cleared
        """
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries

        Returns:
            Number of entries removed
        """
        now = datetime.utcnow()
        removed = 0

        with self._lock:
            expired_keys = [
                patient_id
                for patient_id, data in self._cache.items()
                if now > data.ttl_expires_at
            ]

            for key in expired_keys:
                del self._cache[key]
                removed += 1

        return removed

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with self._lock:
            now = datetime.utcnow()

            active_entries = sum(
                1 for data in self._cache.values()
                if now <= data.ttl_expires_at
            )

            expired_entries = len(self._cache) - active_entries

            return {
                'total_entries': len(self._cache),
                'active_entries': active_entries,
                'expired_entries': expired_entries,
                'default_ttl_hours': self.default_ttl_hours
            }

    def update_session_data(
        self,
        patient_id: str,
        new_session: Dict,
        new_analysis: Dict
    ) -> bool:
        """
        Update cached data with new session analysis

        Appends new session to recent_sessions and updates scores

        Returns:
            True if updated, False if not in cache
        """
        with self._lock:
            if patient_id not in self._cache:
                return False

            cached_data = self._cache[patient_id]

            # Add new session to recent_sessions
            session_summary = {
                'date': new_session.get('session_date', datetime.utcnow().isoformat()),
                'score': new_analysis.get('overall_score', 0.5),
                'exerciseType': new_session.get('exercise_type', 'memory_recall'),
                'notableEvents': new_analysis.get('notable_events', [])
            }

            cached_data.recent_sessions.insert(0, session_summary)

            # Keep only last 10 sessions
            cached_data.recent_sessions = cached_data.recent_sessions[:10]

            # Update scores (simple average - can be more sophisticated)
            recent_scores = [s['score'] for s in cached_data.recent_sessions]
            if recent_scores:
                cached_data.overall_cognitive_score = sum(recent_scores) / len(recent_scores)

            # Update timestamp
            cached_data.last_updated = datetime.utcnow()

            return True


# Global cache instance
_global_cache = None


def get_cache() -> PatientDataCache:
    """Get global cache instance (singleton)"""
    global _global_cache
    if _global_cache is None:
        _global_cache = PatientDataCache(default_ttl_hours=24)
    return _global_cache
