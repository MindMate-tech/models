"""Demo script"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.mindmate_agent import MindMateAgent
from tools.mri_analysis import MRIAnalyzer

async def main():
    patient_profile = {
        'patient_id': 'p001',
        'name': 'Margaret',
        'age': 68,
        'diagnosis': 'early-onset dementia',
        'interests': ['gardening', 'family', 'reading'],
        'expected_info': {
            'family_members': ['Mary', 'John', 'Lucas'],
            'profession': 'teacher',
            'hometown': 'Boston'
        }
    }
    
    # Check for MRI data
    mri_csv = 'data/mri_outputs/report_patient_001.csv'
    if os.path.exists(mri_csv):
        print("📊 Loading MRI data...")
        analyzer = MRIAnalyzer()
        metrics = analyzer.parse_csv(mri_csv)
        summary = analyzer.clinical_summary(metrics)
        patient_profile['baseline_mri'] = {'metrics': metrics, 'clinical_summary': summary}
        print(f"✅ MRI: {summary}\n")
    else:
        print("ℹ️  No MRI data found (will process after Docker completes)\n")
    
    transcript = """
    AI: Good morning Margaret! How are you today?
    
    Margaret: Oh hello... I'm okay I think. What month is it?
    
    AI: It's November 2025. How did you sleep?
    
    Margaret: November... yes. I had breakfast but I forget what. 
    My grandson came by... or was that yesterday? What's his name again? 
    Lucas? I'm not sure.
    
    AI: That's okay. Tell me about your day.
    
    Margaret: Well I used to teach. Math I think. And I love my garden, 
    my roses... I forget what I was saying.
    """
    
    agent = MindMateAgent()
    result = await agent.daily_checkin('p001', transcript, patient_profile)
    
    print("\n" + "="*60)
    print("📊 RESULTS")
    print("="*60)
    print(f"Overall: {result['assessment']['overall_score']:.1%}")
    print(f"Temporal: {result['assessment']['temporal_orientation']:.1%}")
    print(f"Recall: {result['assessment']['personal_recall']:.1%}")
    print(f"Vocabulary: {result['assessment']['speech_analysis']['vocabulary_richness']:.1%}")
    
    print("\n⚠️  ALERTS:")
    for alert in result['risk_alerts']:
        print(f"  [{alert['severity'].upper()}] {alert['message']}")
    
    print(f"\n💬 AI: {result['conversation_response']}\n")

if __name__ == "__main__":
    asyncio.run(main())
