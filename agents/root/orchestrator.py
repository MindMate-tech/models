"""Root orchestrator - routes requests to specialized agents"""
import asyncio
from typing import Dict, Any
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class RootOrchestrator:
    """Main orchestrator that delegates to specialized agents"""
    
    def __init__(self):
        # Lazy import to avoid circular dependencies
        self._doctor_agent = None
        self._patient_agent = None
    
    @property
    def doctor_agent(self):
        if self._doctor_agent is None:
            from agents.doctor.doctor_agent import DoctorAgent
            self._doctor_agent = DoctorAgent()
        return self._doctor_agent
    
    @property
    def patient_agent(self):
        if self._patient_agent is None:
            from agents.patient.patient_agent import PatientAgent
            self._patient_agent = PatientAgent()
        return self._patient_agent
    
    async def route_request(self, request_type: str, **kwargs) -> Dict:
        """
        Route request to appropriate agent
        
        Request types:
        - patient_checkin: Daily patient check-in
        - doctor_lookup: Find patient by ID
        - doctor_dashboard: Get patient dashboard
        - analyze_speech: Analyze speech patterns
        - generate_report: Generate medical report
        """
        
        print(f"🔀 Routing: {request_type}")
        
        if request_type == "patient_checkin":
            return await self.patient_agent.daily_checkin(**kwargs)
        
        elif request_type == "doctor_lookup":
            return await self.doctor_agent.lookup_patient(**kwargs)
        
        elif request_type == "doctor_dashboard":
            return await self.doctor_agent.get_dashboard(**kwargs)
        
        elif request_type == "analyze_speech":
            return await self.patient_agent.analyze_speech(**kwargs)
        
        elif request_type == "generate_report":
            return await self.doctor_agent.generate_report(**kwargs)
        
        else:
            return {
                "error": f"Unknown request type: {request_type}",
                "available_types": [
                    "patient_checkin",
                    "doctor_lookup", 
                    "doctor_dashboard",
                    "analyze_speech",
                    "generate_report"
                ]
            }
    
    async def batch_process(self, requests: list) -> list:
        """Process multiple requests in parallel"""
        tasks = [
            self.route_request(req['type'], **req.get('params', {}))
            for req in requests
        ]
        return await asyncio.gather(*tasks)
