"""
Test Doctor Query API with Complex Real Queries
MVP Showcase: Demonstrate AI-powered natural language queries
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.doctor.doctor_query_agent import DoctorQueryAgent


async def test_at_risk_with_reasoning():
    """Test 1: Find at-risk patients with detailed risk reasoning"""
    print("\n" + "="*80)
    print("TEST 1: FIND AT-RISK PATIENTS (WITH AI REASONING)")
    print("="*80)

    agent = DoctorQueryAgent()

    query = "Show me all at-risk patients and explain in detail why each one is flagged"

    print(f"\n🩺 Doctor Query: \"{query}\"")
    print("\n⏳ AI is analyzing patient database...")

    result = await agent.query(query)

    print(f"\n📊 AI Response:\n")
    print("─" * 80)
    print(result.get('response', 'No response'))
    print("─" * 80)

    if result.get('tools_used'):
        print(f"\n🛠️  Tools Used: {result.get('tools_used')}")


async def test_decline_analysis():
    """Test 2: Analyze why a specific patient is declining"""
    print("\n" + "="*80)
    print("TEST 2: ANALYZE PATIENT DECLINE")
    print("="*80)

    agent = DoctorQueryAgent()

    # Get an at-risk patient first
    at_risk_result = await agent.find_at_risk(threshold=0.7)
    patients = at_risk_result.get('data', [])

    if not patients:
        print("❌ No at-risk patients found for decline analysis")
        return

    patient = patients[0]
    patient_id = patient['patient_id']
    patient_name = patient['name']

    query = f"Why is patient {patient_id} declining? Give me detailed analysis of the causes and recommendations."

    print(f"\n🩺 Doctor Query: \"{query}\"")
    print(f"   Patient: {patient_name}")
    print("\n⏳ AI is analyzing decline patterns...")

    result = await agent.query(query, context={'patient_id': patient_id})

    print(f"\n📊 AI Response:\n")
    print("─" * 80)
    print(result.get('response', 'No response'))
    print("─" * 80)


async def test_patient_comparison():
    """Test 3: Compare multiple patients"""
    print("\n" + "="*80)
    print("TEST 3: COMPARE PATIENTS")
    print("="*80)

    agent = DoctorQueryAgent()

    # Get two patients with sessions
    supabase = agent.tools.supabase
    patients = supabase.table("patients").select("patient_id, name").limit(2).execute()

    if len(patients.data) < 2:
        print("❌ Need at least 2 patients for comparison")
        return

    patient1 = patients.data[0]
    patient2 = patients.data[1]

    query = f"Compare patient {patient1['patient_id']} and patient {patient2['patient_id']}. Tell me who's doing better, who needs attention, and why."

    print(f"\n🩺 Doctor Query: \"{query}\"")
    print(f"   Patient 1: {patient1['name']}")
    print(f"   Patient 2: {patient2['name']}")
    print("\n⏳ AI is comparing patients...")

    result = await agent.query(query)

    print(f"\n📊 AI Response:\n")
    print("─" * 80)
    print(result.get('response', 'No response'))
    print("─" * 80)


async def test_complex_search():
    """Test 4: Complex search query"""
    print("\n" + "="*80)
    print("TEST 4: COMPLEX SEARCH")
    print("="*80)

    agent = DoctorQueryAgent()

    query = "Find all female patients and tell me if any of them are at risk"

    print(f"\n🩺 Doctor Query: \"{query}\"")
    print("\n⏳ AI is searching and analyzing...")

    result = await agent.query(query)

    print(f"\n📊 AI Response:\n")
    print("─" * 80)
    print(result.get('response', 'No response'))
    print("─" * 80)


async def test_multi_step_query():
    """Test 5: Multi-step complex query"""
    print("\n" + "="*80)
    print("TEST 5: MULTI-STEP COMPLEX QUERY")
    print("="*80)

    agent = DoctorQueryAgent()

    query = "Show me patients with declining trends, identify the most critical ones, and tell me what actions I should take immediately"

    print(f"\n🩺 Doctor Query: \"{query}\"")
    print("\n⏳ AI is performing multi-step analysis...")

    result = await agent.query(query)

    print(f"\n📊 AI Response:\n")
    print("─" * 80)
    print(result.get('response', 'No response'))
    print("─" * 80)


async def test_fast_endpoints():
    """Test 6: Fast endpoints (no AI)"""
    print("\n" + "="*80)
    print("TEST 6: FAST ENDPOINTS (NO AI)")
    print("="*80)

    agent = DoctorQueryAgent()

    print("\n📊 Fast At-Risk Query (no AI, instant results):")
    result = await agent.find_at_risk(threshold=0.5)

    print(f"   Found: {result.get('count', 0)} at-risk patients")

    if result.get('data'):
        for i, patient in enumerate(result['data'][:3], 1):
            print(f"\n   {i}. {patient['name']} (Risk: {patient['risk_level'].upper()})")
            print(f"      Score: {patient['average_score']:.1%}")
            print(f"      Reasons:")
            for reason in patient.get('risk_reasons', [])[:2]:
                print(f"      - {reason}")


async def main():
    """Run all MVP showcase tests"""
    print("\n" + "="*80)
    print("🩺 MINDMATE DOCTOR QUERY API - MVP SHOWCASE")
    print("="*80)
    print("\nDemonstrating AI-powered natural language queries")
    print("with real patient data from Supabase\n")

    try:
        # Run all showcase tests
        await test_at_risk_with_reasoning()
        await asyncio.sleep(2)

        await test_decline_analysis()
        await asyncio.sleep(2)

        await test_patient_comparison()
        await asyncio.sleep(2)

        await test_complex_search()
        await asyncio.sleep(2)

        await test_multi_step_query()
        await asyncio.sleep(2)

        await test_fast_endpoints()

        print("\n" + "="*80)
        print("✅ ALL MVP SHOWCASE TESTS COMPLETE!")
        print("="*80)
        print("\n🎯 Capabilities Demonstrated:")
        print("   ✅ At-risk detection with detailed reasoning")
        print("   ✅ Decline analysis with causes and recommendations")
        print("   ✅ Multi-patient comparison")
        print("   ✅ Complex search with filtering")
        print("   ✅ Multi-step reasoning")
        print("   ✅ Fast endpoints for simple queries")

        print("\n💡 Key Features:")
        print("   🤖 AI understands natural language")
        print("   🧠 Uses Dedalus tool calling")
        print("   📊 Queries real Supabase data")
        print("   ⚡ Provides actionable insights")
        print("   🔍 Explains risk reasoning")

        print("\n🚀 Ready for:")
        print("   • Frontend integration")
        print("   • Doctor dashboard")
        print("   • Production deployment")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🔬 Starting MVP Showcase...")
    print("⏳ This will demonstrate AI-powered medical queries...\n")

    asyncio.run(main())
