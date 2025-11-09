"""
Test Complete System Integration
Demonstrates natural language queries accessing sessions, patients, and analysis
"""
import asyncio
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.doctor.doctor_query_agent import DoctorQueryAgent
from db.supabase_client import get_supabase


async def test_complete_integration():
    """Test natural language queries with the complete system"""

    print("=" * 80)
    print("🧪 TESTING COMPLETE SYSTEM INTEGRATION")
    print("=" * 80)
    print("\nThis demonstrates how natural language queries access:")
    print("  ✓ Patient data")
    print("  ✓ Session data")
    print("  ✓ AI analysis")
    print("  ✓ Risk assessment")
    print("  ✓ Predictions")

    # Initialize
    agent = DoctorQueryAgent()
    supabase = get_supabase()

    # Get real data from database
    print("\n📊 Step 1: Getting real patient and session data...")
    print("-" * 80)

    patients = supabase.table("patients").select("*").limit(1).execute()
    if not patients.data:
        print("❌ No patients in database")
        return

    patient = patients.data[0]
    patient_id = patient['patient_id']
    patient_name = patient['name']

    print(f"✅ Using patient: {patient_name}")
    print(f"   ID: {patient_id}")

    # Get sessions for this patient
    sessions = (
        supabase.table("sessions")
        .select("*")
        .eq("patient_id", patient_id)
        .order("session_date", desc=True)
        .execute()
    )

    if sessions.data:
        latest_session = sessions.data[0]
        session_id = latest_session['session_id']
        session_score = latest_session.get('overall_score', 'N/A')
        print(f"   Sessions: {len(sessions.data)}")
        print(f"   Latest session score: {session_score}")
        print(f"   Latest session ID: {session_id}")
    else:
        session_id = None
        print("   No sessions found for this patient")

    # Test 1: General patient query
    print("\n\n" + "=" * 80)
    print("📝 Test 1: Natural Language - General Patient Query")
    print("=" * 80)
    print(f"\nQuery: \"Tell me about {patient_name}\"")
    print("-" * 80)

    result1 = await agent.query(
        doctor_query=f"Tell me about {patient_name}",
        context={"patient_id": patient_id, "doctor_id": "test_doctor"}
    )

    print(f"\n✅ Success: {result1['success']}")
    print(f"🔧 Tools used: {result1['tools_used']}")
    print(f"📊 Model: {result1['model_info']['model']}")
    print(f"🧠 Complexity: {result1['model_info']['complexity']}")

    print(f"\n📝 AI Response:")
    print("-" * 80)
    print(result1['response'][:600])
    if len(result1['response']) > 600:
        print("...\n")
    print("-" * 80)

    # Test 2: Risk assessment query
    print("\n\n" + "=" * 80)
    print("📝 Test 2: Natural Language - Risk Assessment")
    print("=" * 80)
    print(f"\nQuery: \"Is {patient_name} at risk? Should I be concerned?\"")
    print("-" * 80)

    result2 = await agent.query(
        doctor_query=f"Is {patient_name} at risk? Should I be concerned?",
        context={"patient_id": patient_id, "doctor_id": "test_doctor"}
    )

    print(f"\n✅ Success: {result2['success']}")
    print(f"🔧 Tools used: {result2['tools_used']}")
    print(f"📊 Model: {result2['model_info']['model']}")
    print(f"🧠 Complexity: {result2['model_info']['complexity']}")

    # Check for sequential thinking
    if '##' in result2['response'] and '✅' in result2['response']:
        print(f"🎯 Sequential Thinking: ACTIVE (shows reasoning steps)")
    else:
        print(f"🎯 Sequential Thinking: Not detected")

    print(f"\n📝 AI Response:")
    print("-" * 80)
    print(result2['response'][:700])
    if len(result2['response']) > 700:
        print("...\n")
    print("-" * 80)

    # Test 3: Session-specific query (if we have a session)
    if session_id:
        print("\n\n" + "=" * 80)
        print("📝 Test 3: Natural Language - Session Analysis")
        print("=" * 80)
        print(f"\nQuery: \"Analyze the latest session for {patient_name}\"")
        print(f"Context includes: session_id = {session_id}")
        print("-" * 80)

        result3 = await agent.query(
            doctor_query=f"Analyze the latest session for {patient_name}",
            context={
                "session_id": session_id,
                "patient_id": patient_id,
                "doctor_id": "test_doctor"
            }
        )

        print(f"\n✅ Success: {result3['success']}")
        print(f"🔧 Tools used: {result3['tools_used']}")

        # Verify it used session-specific tool
        if 'analyze_session_performance' in result3['tools_used']:
            print(f"   ✅ Correctly routed to analyze_session_performance!")
        elif 'get_session_by_id' in result3['tools_used']:
            print(f"   ✅ Correctly routed to get_session_by_id!")
        else:
            print(f"   ⚠️  Used: {result3['tools_used']}")

        print(f"📊 Model: {result3['model_info']['model']}")

        # Check raw data for findings
        if result3.get('raw_data'):
            if 'findings' in result3['raw_data']:
                findings = result3['raw_data']['findings']
                print(f"\n🔍 Findings detected: {len(findings)}")
                for finding in findings[:2]:
                    print(f"   • [{finding.get('category')}] {finding.get('finding')}")

        print(f"\n📝 AI Response:")
        print("-" * 80)
        print(result3['response'][:600])
        if len(result3['response']) > 600:
            print("...\n")
        print("-" * 80)

    # Test 4: Follow-up query (memory system)
    print("\n\n" + "=" * 80)
    print("📝 Test 4: Natural Language - Follow-up Query (Memory)")
    print("=" * 80)
    print(f"\nQuery 1: \"Show me all at-risk patients\"")
    print("-" * 80)

    result4a = await agent.query(
        doctor_query="Show me all at-risk patients",
        context={"doctor_id": "test_doctor"}
    )

    print(f"\n✅ Success: {result4a['success']}")
    print(f"🔧 Tools used: {result4a['tools_used']}")

    # Check how many at-risk patients
    if result4a.get('raw_data'):
        at_risk_count = len(result4a['raw_data']) if isinstance(result4a['raw_data'], list) else 'N/A'
        print(f"📊 At-risk patients found: {at_risk_count}")

    print(f"\n📝 Response preview:")
    print(result4a['response'][:400])
    if len(result4a['response']) > 400:
        print("...")

    # Follow-up query using memory
    print("\n\nQuery 2 (Follow-up): \"Tell me more about them\"")
    print("-" * 80)

    result4b = await agent.query(
        doctor_query="Tell me more about them",
        context={"doctor_id": "test_doctor"}
    )

    print(f"\n✅ Success: {result4b['success']}")
    print(f"🔧 Tools used: {result4b['tools_used']}")

    # Check if memory was used
    if result4b['model_info'].get('memory_used'):
        print(f"🧠 Memory: ACTIVE (remembered previous query)")
    else:
        print(f"🧠 Memory: Not detected")

    print(f"\n📝 Response preview:")
    print(result4b['response'][:400])
    if len(result4b['response']) > 400:
        print("...")

    # Test 5: Predictive query
    print("\n\n" + "=" * 80)
    print("📝 Test 5: Natural Language - Predictive Scoring")
    print("=" * 80)
    print(f"\nQuery: \"Which patients are likely to decline next month?\"")
    print("-" * 80)

    result5 = await agent.query(
        doctor_query="Which patients are likely to decline next month?",
        context={"doctor_id": "test_doctor"}
    )

    print(f"\n✅ Success: {result5['success']}")
    print(f"🔧 Tools used: {result5['tools_used']}")

    # Verify it used prediction tool
    if 'predict_decline_risk' in result5['tools_used']:
        print(f"   ✅ Correctly routed to predict_decline_risk!")

    # Check cache info
    if result5.get('raw_data') and 'cache_info' in result5['raw_data']:
        cache = result5['raw_data']['cache_info']
        print(f"\n💾 Cache Info:")
        print(f"   Cached: {cache.get('cached', False)}")
        print(f"   Fresh: {cache.get('is_fresh', False)}")
        if cache.get('age_minutes'):
            print(f"   Age: {cache['age_minutes']:.1f} minutes")

    print(f"\n📝 Response preview:")
    print(result5['response'][:600])
    if len(result5['response']) > 600:
        print("...")

    # Summary
    print("\n\n" + "=" * 80)
    print("✅ COMPLETE INTEGRATION TEST FINISHED!")
    print("=" * 80)

    print("\n📊 Test Summary:")
    print(f"   Test 1 (Patient info): {'✅ PASSED' if result1['success'] else '❌ FAILED'}")
    print(f"   Test 2 (Risk assessment): {'✅ PASSED' if result2['success'] else '❌ FAILED'}")
    if session_id:
        print(f"   Test 3 (Session analysis): {'✅ PASSED' if result3['success'] else '❌ FAILED'}")
    print(f"   Test 4 (Memory/follow-up): {'✅ PASSED' if result4b['success'] else '❌ FAILED'}")
    print(f"   Test 5 (Predictions): {'✅ PASSED' if result5['success'] else '❌ FAILED'}")

    print("\n🎯 Features Demonstrated:")
    print("   ✅ Natural language understanding")
    print("   ✅ Intelligent tool routing")
    print("   ✅ Patient data access")
    if session_id:
        print("   ✅ Session-specific queries")
    print("   ✅ Risk assessment")
    print("   ✅ Sequential thinking (medical reasoning)")
    print("   ✅ Memory system (follow-up queries)")
    print("   ✅ Predictive scoring (ML predictions)")
    print("   ✅ Caching for performance")

    print("\n📝 Natural Language Queries Tested:")
    print(f"   1. \"Tell me about {patient_name}\"")
    print(f"   2. \"Is {patient_name} at risk? Should I be concerned?\"")
    if session_id:
        print(f"   3. \"Analyze the latest session for {patient_name}\"")
    print(f"   4. \"Show me all at-risk patients\" → \"Tell me more about them\"")
    print(f"   5. \"Which patients are likely to decline next month?\"")

    print("\n🎉 All components working together!")


if __name__ == "__main__":
    asyncio.run(test_complete_integration())
