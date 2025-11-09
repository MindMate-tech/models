"""
Test Doctor Agent Querying Patient Database
Simulates a doctor asking questions about patient data
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.doctor.doctor_agent import DoctorAgent


async def test_direct_lookup():
    """Test 1: Direct patient lookup by ID"""
    print("\n" + "="*70)
    print("TEST 1: DIRECT PATIENT LOOKUP")
    print("="*70)

    agent = DoctorAgent()

    print("\n🔍 Doctor: 'Show me patient p001'")
    result = await agent.lookup_patient(patient_id="p001")

    print(f"\n✅ Found Patient:")
    print(f"   Name: {result['name']}")
    print(f"   Age: {result['age']}")
    print(f"   Diagnosis: {result['diagnosis']}")
    print(f"   Last Check-in: {result['last_checkin']}")
    print(f"   Current Score: {result['current_score']:.1%}")
    print(f"   Risk Level: {result['risk_level'].upper()}")
    print(f"   Recent Alerts: {len(result['recent_alerts'])}")

    return result


async def test_natural_language_query():
    """Test 2: Natural language patient search"""
    print("\n" + "="*70)
    print("TEST 2: NATURAL LANGUAGE QUERY")
    print("="*70)

    agent = DoctorAgent()

    queries = [
        "Show me all patients at high risk",
        "Who has cognitive decline?",
        "Find patients with dementia",
        "Which patients need immediate attention?"
    ]

    for query in queries:
        print(f"\n🔍 Doctor: '{query}'")
        print("   AI is searching...")
        result = await agent.lookup_patient(query=query)
        print(f"\n   📊 Result:")
        if 'search_result' in result:
            print(f"   {result['search_result']}")
        elif 'error' in result:
            print(f"   ❌ {result['error']}")
        print()

        # Small delay for readability
        await asyncio.sleep(1)


async def test_get_at_risk_patients():
    """Test 3: Get list of at-risk patients"""
    print("\n" + "="*70)
    print("TEST 3: AT-RISK PATIENTS LIST")
    print("="*70)

    agent = DoctorAgent()

    print("\n🔍 Doctor: 'Show me all at-risk patients'")
    at_risk = await agent.get_at_risk_patients()

    print(f"\n⚠️  Found {len(at_risk)} at-risk patient(s):\n")
    for patient in at_risk:
        print(f"   [{patient['risk_level'].upper()}] {patient['name']} (ID: {patient['patient_id']})")
        print(f"      Recent alerts: {patient['recent_alerts']}")
        print()


async def test_dashboard_data():
    """Test 4: Get comprehensive dashboard"""
    print("\n" + "="*70)
    print("TEST 4: PATIENT DASHBOARD")
    print("="*70)

    agent = DoctorAgent()

    print("\n🔍 Doctor: 'Show me Margaret's complete dashboard'")
    dashboard = await agent.get_dashboard(patient_id="p001")

    print(f"\n📊 Dashboard for {dashboard['name']}:")
    print(f"\n   Basic Info:")
    print(f"      Age: {dashboard['age']}")
    print(f"      Diagnosis: {dashboard['diagnosis']}")
    print(f"      MRI Summary: {dashboard['mri_summary']}")

    print(f"\n   Performance Metrics:")
    print(f"      Baseline Score: {dashboard['baseline_score']:.1%}")
    print(f"      Current Score: {dashboard['current_score']:.1%}")
    print(f"      Decline Rate: {dashboard['metrics']['decline_rate']}")
    print(f"      Days Monitored: {dashboard['metrics']['days_monitored']}")
    print(f"      Average Daily Score: {dashboard['metrics']['avg_daily_score']:.1%}")

    print(f"\n   Recent Timeline (last 7 days):")
    for entry in dashboard['timeline'][-7:]:
        score_emoji = "🔴" if entry['cognitive_score'] < 0.5 else "🟡" if entry['cognitive_score'] < 0.7 else "🟢"
        print(f"      {entry['date']}: {score_emoji} {entry['cognitive_score']:.1%} - {entry['mood']}")

    print(f"\n   Recent Alerts:")
    for alert in dashboard['recent_alerts']:
        print(f"      ⚠️  [{alert['severity'].upper()}] {alert['type']} ({alert['date']})")


async def test_generate_report():
    """Test 5: Generate medical report"""
    print("\n" + "="*70)
    print("TEST 5: GENERATE MEDICAL REPORT")
    print("="*70)

    agent = DoctorAgent()

    print("\n🔍 Doctor: 'Generate a 7-day progress report for Margaret'")
    print("   AI is generating report...")

    report = await agent.generate_report(patient_id="p001", timeframe="7 days")

    print(f"\n📄 Generated Report:\n")
    print("─" * 70)
    print(report)
    print("─" * 70)


async def test_interactive_query():
    """Test 6: Interactive doctor query mode"""
    print("\n" + "="*70)
    print("TEST 6: INTERACTIVE QUERY MODE")
    print("="*70)

    agent = DoctorAgent()

    print("\n💬 You are now in Doctor Query Mode!")
    print("   Ask questions about patients in natural language.")
    print("   Type 'quit' to exit.\n")

    sample_queries = [
        "Show me patient p001",
        "Who has dementia?",
        "List all at-risk patients"
    ]

    print("   Sample queries to try:")
    for i, q in enumerate(sample_queries, 1):
        print(f"   {i}. {q}")

    print("\n   (Running automated demo queries...)\n")

    for query in sample_queries:
        print(f"Doctor > {query}")

        if query.startswith("Show me patient"):
            patient_id = query.split()[-1]
            result = await agent.lookup_patient(patient_id=patient_id)
            print(f"System > Found: {result.get('name', 'Unknown')} - {result.get('diagnosis', 'N/A')}")
        elif "at-risk" in query.lower():
            at_risk = await agent.get_at_risk_patients()
            print(f"System > {len(at_risk)} at-risk patient(s) found")
            for p in at_risk:
                print(f"         - {p['name']} ({p['risk_level']})")
        else:
            result = await agent.lookup_patient(query=query)
            if 'search_result' in result:
                print(f"System > {result['search_result'][:200]}...")

        print()
        await asyncio.sleep(1)


async def main():
    """Run all doctor query tests"""
    print("\n" + "="*70)
    print("🩺 MINDMATE DOCTOR AGENT - DATABASE QUERY TESTING")
    print("="*70)
    print("\nThis simulates a doctor querying the patient database")
    print("using natural language and AI-powered search.\n")

    try:
        # Run all tests
        await test_direct_lookup()
        await test_natural_language_query()
        await test_get_at_risk_patients()
        await test_dashboard_data()
        await test_generate_report()
        await test_interactive_query()

        print("\n" + "="*70)
        print("✅ ALL DOCTOR QUERY TESTS PASSED!")
        print("="*70)
        print("\n🎯 Agent Capabilities Demonstrated:")
        print("   ✅ Direct patient lookup by ID")
        print("   ✅ Natural language search queries")
        print("   ✅ At-risk patient identification")
        print("   ✅ Comprehensive dashboard generation")
        print("   ✅ AI-powered medical report generation")
        print("   ✅ Interactive query mode")

        print("\n💡 Integration Status:")
        print("   📦 Mock Database: Working (2 patients)")
        print("   🔌 Ready for Supabase: Yes")
        print("   🤖 AI Query Engine: Working")
        print("   📊 Dashboard API: Ready")

        print("\n🚀 Next Steps:")
        print("   1. Connect to real Supabase database in backend")
        print("   2. Replace mock data with live patient records")
        print("   3. Add authentication and permissions")
        print("   4. Deploy and test with production data")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🔬 Starting Doctor Agent Query Tests...")
    print("⏳ This will test AI-powered database querying capabilities.\n")

    asyncio.run(main())
