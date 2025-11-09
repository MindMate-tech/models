"""
Lightweight memory store for doctor query sessions
Enables contextual follow-up queries like "tell me more about them"
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import hashlib


class SessionMemory:
    """
    In-memory session store for doctor queries

    Stores recent queries and results to enable follow-up questions
    """

    def __init__(self, max_sessions: int = 100, session_ttl_hours: int = 24):
        """
        Initialize memory store

        Args:
            max_sessions: Maximum number of sessions to keep in memory
            session_ttl_hours: Time-to-live for sessions in hours
        """
        self.sessions: Dict[str, Dict] = {}
        self.max_sessions = max_sessions
        self.session_ttl = timedelta(hours=session_ttl_hours)

    def _generate_session_id(self, context: Dict) -> str:
        """
        Generate session ID from context (doctor_id, IP, etc.)

        Args:
            context: Request context

        Returns:
            Session ID string
        """
        # Try to use doctor_id if available
        if context.get('doctor_id'):
            return f"doctor_{context['doctor_id']}"

        # Fall back to IP or session token
        if context.get('ip_address'):
            return f"ip_{hashlib.md5(context['ip_address'].encode()).hexdigest()[:16]}"

        if context.get('session_token'):
            return f"token_{context['session_token']}"

        # Default session
        return "default_session"

    def _cleanup_old_sessions(self):
        """Remove expired sessions"""
        current_time = datetime.now()
        expired_sessions = [
            session_id for session_id, data in self.sessions.items()
            if current_time - data['last_accessed'] > self.session_ttl
        ]

        for session_id in expired_sessions:
            del self.sessions[session_id]

        # Limit total sessions
        if len(self.sessions) > self.max_sessions:
            # Remove oldest sessions
            sorted_sessions = sorted(
                self.sessions.items(),
                key=lambda x: x[1]['last_accessed']
            )
            for session_id, _ in sorted_sessions[:len(self.sessions) - self.max_sessions]:
                del self.sessions[session_id]

    def remember(self, context: Dict, query: str, result: Dict):
        """
        Store query and result in session memory

        Args:
            context: Request context
            query: The query string
            result: Query result with data
        """
        self._cleanup_old_sessions()

        session_id = self._generate_session_id(context)

        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'queries': [],
                'last_accessed': datetime.now(),
                'created_at': datetime.now()
            }

        # Store last 5 queries
        self.sessions[session_id]['queries'].append({
            'query': query,
            'timestamp': datetime.now(),
            'tools_used': result.get('tools_used', []),
            'data_summary': self._extract_data_summary(result)
        })

        # Keep only last 5 queries
        self.sessions[session_id]['queries'] = self.sessions[session_id]['queries'][-5:]
        self.sessions[session_id]['last_accessed'] = datetime.now()

    def _extract_data_summary(self, result: Dict) -> Dict:
        """
        Extract summary of data for memory (don't store full results)

        Args:
            result: Query result

        Returns:
            Summarized data for memory
        """
        summary = {}

        # Extract patient IDs if available
        raw_data = result.get('raw_data', {})

        if isinstance(raw_data, list):
            # List of patients
            patient_ids = [p.get('patient_id') for p in raw_data if p.get('patient_id')]
            patient_names = [p.get('name') for p in raw_data if p.get('name')]
            summary['patient_ids'] = patient_ids
            summary['patient_names'] = patient_names
            summary['count'] = len(raw_data)

        elif isinstance(raw_data, dict):
            # Single patient or comparison
            if raw_data.get('patient_id'):
                summary['patient_id'] = raw_data['patient_id']
                summary['patient_name'] = raw_data.get('name')

        return summary

    def recall(self, context: Dict, current_query: str) -> Optional[Dict]:
        """
        Recall recent context for follow-up queries

        Args:
            context: Request context
            current_query: Current query string

        Returns:
            Memory context if available, None otherwise
        """
        session_id = self._generate_session_id(context)

        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]

        # Update last accessed
        session['last_accessed'] = datetime.now()

        # Check if current query is a follow-up
        current_lower = current_query.lower()
        follow_up_keywords = ['them', 'those', 'these', 'that patient', 'the ones', 'more about']

        is_follow_up = any(keyword in current_lower for keyword in follow_up_keywords)

        if not is_follow_up:
            return None

        # Get last query that produced patient data
        for past_query in reversed(session['queries']):
            if past_query['data_summary'].get('patient_ids'):
                return {
                    'is_follow_up': True,
                    'previous_query': past_query['query'],
                    'patient_ids': past_query['data_summary'].get('patient_ids', []),
                    'patient_names': past_query['data_summary'].get('patient_names', []),
                    'timestamp': past_query['timestamp']
                }

        return None

    def get_session_history(self, context: Dict) -> List[Dict]:
        """Get recent query history for a session"""
        session_id = self._generate_session_id(context)

        if session_id not in self.sessions:
            return []

        return self.sessions[session_id]['queries']

    def get_stats(self) -> Dict:
        """Get memory store statistics"""
        return {
            'total_sessions': len(self.sessions),
            'max_sessions': self.max_sessions,
            'ttl_hours': self.session_ttl.total_seconds() / 3600,
            'active_sessions': [
                {
                    'session_id': session_id,
                    'query_count': len(data['queries']),
                    'last_accessed': data['last_accessed'].isoformat()
                }
                for session_id, data in self.sessions.items()
            ]
        }


# Global memory instance
session_memory = SessionMemory()
