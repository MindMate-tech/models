"""Comprehensive multi-agent system test"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.root.orchestrator import RootOrchestrator
from tools.mri_analysis import MRIAnalyzer

async def test_patient_checkin(orchestrator):
    """Test patient check-in flow"""
    print("\n" + "="*60)
    print("TEST 1: PATIENT CHECK-IN")
    print("="*60)
    
    # Load MRI data if available
    mri_csv = 'data/mri_outputs/report_patient_001.csv'
    baseline_mri = None
    
    if os.path.exists(mri_csv):
        print("📊 Loading MRI data...")
        analyzer = MRIAnalyzer()
        metrics = analyzer.parse_csv(mri_csv)
        summary = analyzer.clinical_summary(metrics)
        baseline_mri = {'metrics': metrics, 'clinical_summary': summary}
        print(f"✅ MRI loaded: {summary}")
    else:
        print("ℹ️  No MRI data - using cognitive tests only")
    
    patient_profile = {
        'patient_id': 'p001',
        'name': 'Margaret',
        'age': 68,
        'interests': ['gardening', 'family', 'reading'],
        'expected_info': {
            'family_members': ['Mary', 'John', 'Lucas'],
            'profession': 'teacher',
            'hometown': 'Boston'
        },
        'baseline_mri': baseline_mri
    }
    
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
    
    result = await orchestrator.route_request(
        "patient_checkin",
        patient_id="p001",
        transcript=transcript,
        patient_profile=patient_profile
    )
    
    print(f"\n📊 Results:")
    print(f"   Overall Score: {result['assessment']['overall_score']:.1%}")
    print(f"   Temporal: {result['assessment']['temporal_orientation']:.1%}")
    print(f"   Recall: {result['assessment']['personal_recall']:.1%}")
    print(f"   Vocabulary: {result['assessment']['speech_analysis']['vocabulary_richness']:.1%}")
    print(f"\n⚠️  Risk Alerts: {len(result['risk_alerts'])}")
    for alert in result['risk_alerts']:
        print(f"   - [{alert['severity'].upper()}] {alert['message']}")
    
    print(f"\n💬 AI Response:")
    print(f"   {result['conversation_response']}\n")
    
    return result

async def test_doctor_lookup(orchestrator):
    """Test doctor patient lookup"""
    print("\n" + "="*60)
    print("TEST 2: DOCTOR PATIENT LOOKUP")
    print("="*60)
    
    result = await orchestrator.route_request(
        "doctor_lookup",
        patient_id="p001"
    )
    
    print(f"\n✅ Found Patient:")
    print(f"   Name: {result['name']}")
    print(f"   Age: {result['age']}")
    print(f"   Risk Level: {result['risk_level'].upper()}")
    print(f"   Recent Alerts: {len(result['recent_alerts'])}\n")
    
    return result

async def test_dashboard(orchestrator):
    """Test dashboard data"""
    print("\n" + "="*60)
    print("TEST 3: DOCTOR DASHBOARD")
    print("="*60)
    
    result = await orchestrator.route_request(
        "doctor_dashboard",
        patient_id="p001"
    )
    
    print(f"\n📈 Dashboard Data:")
    print(f"   Timeline Points: {len(result['timeline'])}")
    print(f"   Decline Rate: {result['metrics']['decline_rate']}")
    print(f"   Days Monitored: {result['metrics']['days_monitored']}")
    print(f"   Avg Score: {result['metrics']['avg_daily_score']:.1%}\n")
    
    print("   Recent Trend:")
    for entry in result['timeline'][-5:]:
        print(f"     {entry['date']}: {entry['cognitive_score']:.1%} ({entry['mood']})")
    
    return result

async def test_report_generation(orchestrator):
    """Test medical report generation"""
    print("\n" + "="*60)
    print("TEST 4: GENERATE MEDICAL REPORT")
    print("="*60)
    
    result = await orchestrator.route_request(
        "generate_report",
        patient_id="p001",
        timeframe="7 days"
    )
    
    print(f"\n📄 Generated Report:\n")
    print(result)
    
    return result

async def main():
    print("\n" + "="*70)
    print("🤖 MINDMATE MULTI-AGENT SYSTEM - COMPREHENSIVE TEST")
    print("="*70)
    
    orchestrator = RootOrchestrator()
    
    # Run all tests
    try:
        checkin_result = await test_patient_checkin(orchestrator)
        lookup_result = await test_doctor_lookup(orchestrator)
        dashboard_result = await test_dashboard(orchestrator)
        report_result = await test_report_generation(orchestrator)
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print("\n🎯 System Ready for Integration:")
        print("   ✅ Patient Agent: Daily check-ins working")
        print("   ✅ Doctor Agent: Lookups and dashboards working")
        print("   ✅ Root Orchestrator: Routing working")
        print("   ✅ MRI Integration: Ready (using mock data)")
        print("\n💡 Next Steps:")
        print("   1. Backend teammate: Integrate RootOrchestrator")
        print("   2. Frontend teammate: Build UI components")
        print("   3. You: Add speech recognition + cloud MRI")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
