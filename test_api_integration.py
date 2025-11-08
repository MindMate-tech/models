"""
Integration test for MindMate Cognitive Analysis API
Tests the complete flow from session analysis to dashboard generation
"""
import asyncio
import sys
import os
from uuid import uuid4
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_server import (
    AnalyzeSessionRequest,
    PatientDashboardRequest,
    MRIAnalysisRequest,
    session_analyzer,
    memory_engine,
    brain_mapper
)


async def test_mri_analysis():
    """Test MRI brain region mapping"""
    print("\n" + "="*60)
    print("TEST 1: MRI Brain Region Analysis")
    print("="*60)

    mri_csv = 'data/mri_outputs/report_patient_001.csv'

    if not os.path.exists(mri_csv):
        print("⚠️  MRI file not found, skipping test")
        return

    from tools.brain_region_mapper import analyze_mri_file

    result = analyze_mri_file(mri_csv)

    print("\n📊 Brain Region Scores:")
    for region, score in result['brain_regions'].items():
        print(f"  {region:20s}: {score:.3f}")

    print(f"\n⚠️  Alerts: {len(result['alerts'])}")
    for alert in result['alerts']:
        print(f"  [{alert['severity'].upper()}] {alert['message']}")

    print("\n✅ MRI analysis test passed!\n")


async def test_session_analysis():
    """Test full session cognitive analysis"""
    print("\n" + "="*60)
    print("TEST 2: Session Cognitive Analysis")
    print("="*60)

    # Mock session data
    session_data = {
        'session_id': str(uuid4()),
        'patient_id': str(uuid4()),
        'transcript': """
            AI: Good morning Margaret! How are you today?

            Margaret: Oh hello... I'm okay I think. What month is it?

            AI: It's November 2025. How did you sleep?

            Margaret: November... yes. I had breakfast but I forget what.
            My grandson Lucas came by yesterday. We talked about gardening.
            I used to teach math, you know. I love my roses in the garden.

            AI: That's wonderful! Tell me more about your garden.

            Margaret: Well, the roses bloom in spring. Lucas helps me sometimes.
            We went to Boston once... or was that last year? I can't quite remember.
        """,
        'exercise_type': 'memory_recall',
        'session_date': datetime.utcnow().isoformat()
    }

    patient_profile = {
        'name': 'Margaret',
        'age': 68,
        'diagnosis': 'early-onset dementia',
        'interests': ['gardening', 'family', 'reading'],
        'expected_info': {
            'family_members': ['Lucas'],
            'profession': 'teacher',
            'hometown': 'Boston'
        }
    }

    # Run analysis
    result = await session_analyzer.analyze_session(
        session_data=session_data,
        patient_profile=patient_profile,
        previous_sessions=[]
    )

    print("\n📝 Extracted Memories:")
    for i, memory in enumerate(result['memories'][:3], 1):
        print(f"  {i}. {memory.get('title', 'Untitled')}")
        print(f"     {memory.get('description', '')[:100]}...")

    print(f"\n🧪 Cognitive Test Scores:")
    for test in result['cognitive_test_scores']:
        score_pct = (test['score'] / test['max_score']) * 100
        print(f"  {test['test']:25s}: {score_pct:>5.1f}%")

    print(f"\n📊 Memory Metrics:")
    for metric, score in result['memory_metrics'].items():
        print(f"  {metric:20s}: {score:.3f}")

    print(f"\n🎯 Overall Score: {result['overall_score']:.1%}")

    print(f"\n⚠️  Doctor Alerts: {len(result['doctor_alerts'])}")
    for alert in result['doctor_alerts']:
        print(f"  [{alert['severity'].upper()}] {alert['message']}")

    print(f"\n🏥 Requires Doctor Review: {result['requires_doctor_review']}")

    print("\n✅ Session analysis test passed!\n")

    return result


async def test_dashboard_generation():
    """Test patient dashboard data generation"""
    print("\n" + "="*60)
    print("TEST 3: Patient Dashboard Generation")
    print("="*60)

    # Mock historical sessions
    mock_sessions = []
    for i in range(7):
        mock_sessions.append({
            'session_id': str(uuid4()),
            'patient_id': 'test-patient-001',
            'session_date': f'2025-11-{8-i:02d}T10:00:00',
            'exercise_type': 'memory_recall',
            'overall_score': 0.7 - (i * 0.05),  # Declining trend
            'ai_extracted_data': {
                'overall_score': 0.7 - (i * 0.05),
                'memory_metrics': {
                    'shortTermRecall': 0.7 - (i * 0.04),
                    'longTermRecall': 0.65 - (i * 0.05),
                    'semanticMemory': 0.75,
                    'episodicMemory': 0.6 - (i * 0.06),
                    'workingMemory': 0.7
                },
                'notable_events': [] if i > 3 else ['Memory difficulty detected']
            }
        })

    # Generate dashboard
    request = PatientDashboardRequest(
        patient_id=uuid4(),
        patient_name="Margaret Smith",
        sessions=mock_sessions,
        mri_csv_path='data/mri_outputs/report_patient_001.csv',
        days_back=30
    )

    # Simulate dashboard generation logic
    from services.patient_cache import get_cache
    cache = get_cache()

    # Build dashboard data
    brain_regions = {'hippocampus': 0.75, 'prefrontalCortex': 0.80, 'temporalLobe': 0.72,
                    'parietalLobe': 0.78, 'amygdala': 0.74, 'cerebellum': 0.82}

    if os.path.exists('data/mri_outputs/report_patient_001.csv'):
        from tools.brain_region_mapper import analyze_mri_file
        mri_analysis = analyze_mri_file('data/mri_outputs/report_patient_001.csv')
        brain_regions = mri_analysis['brain_regions']

    memory_metrics = memory_engine.generate_time_series(
        sessions=mock_sessions,
        days_back=30
    )

    recent_sessions = []
    for session in mock_sessions[:5]:
        recent_sessions.append({
            'date': session['session_date'],
            'score': session['overall_score'],
            'exerciseType': session['exercise_type'],
            'notableEvents': session['ai_extracted_data']['notable_events']
        })

    overall_score = sum(s['score'] for s in recent_sessions) / len(recent_sessions)
    memory_retention = memory_engine.calculate_memory_retention_rate(
        sessions=mock_sessions,
        days_back=7
    )

    print("\n🧠 Brain Regions:")
    for region, score in brain_regions.items():
        bar = "█" * int(score * 20)
        print(f"  {region:20s}: {bar} {score:.3f}")

    print(f"\n📈 Memory Metrics Time Series:")
    for metric, data_points in memory_metrics.items():
        print(f"  {metric:20s}: {len(data_points)} data points")

    print(f"\n📋 Recent Sessions: {len(recent_sessions)}")
    for session in recent_sessions[:3]:
        print(f"  {session['date'][:10]}: {session['score']:.1%}")

    print(f"\n🎯 Overall Cognitive Score: {overall_score:.1%}")
    print(f"💾 Memory Retention Rate: {memory_retention:.1%}")

    print("\n✅ Dashboard generation test passed!\n")


async def test_complete_flow():
    """Test the complete integration flow"""
    print("\n" + "="*70)
    print(" "*15 + "MINDMATE API INTEGRATION TEST")
    print("="*70)

    try:
        # Test 1: MRI Analysis
        await test_mri_analysis()

        # Test 2: Session Analysis
        analysis_result = await test_session_analysis()

        # Test 3: Dashboard Generation
        await test_dashboard_generation()

        print("\n" + "="*70)
        print(" "*20 + "ALL TESTS PASSED! ✅")
        print("="*70)

        print("\n📝 Next Steps:")
        print("  1. Start the API server: python api_server.py")
        print("  2. Test with curl or Postman:")
        print("     curl http://localhost:8000/health")
        print("  3. Deploy to Render:")
        print("     - Push code to GitHub")
        print("     - Connect to Render")
        print("     - Set environment variables (DEDALUS_API_KEY, ANTHROPIC_API_KEY)")
        print("  4. Update your main backend to call this API")
        print("\n")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_complete_flow())
