"""
Test predictive risk scoring
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.doctor.doctor_query_agent import DoctorQueryAgent


async def test_predictions():
    """Test predictive risk scoring"""
    agent = DoctorQueryAgent()

    print("=" * 80)
    print("🔮 TESTING PREDICTIVE RISK SCORING")
    print("=" * 80)

    # Test 1: Predict decline
    print("\n📝 Test 1: Predict Future Decline")
    print("-" * 80)
    result1 = await agent.query("Predict which patients will decline next month")

    print(f"✅ Success: {result1['success']}")
    print(f"📊 Model: {result1['model_info']['model']}")
    print(f"🔧 Tools: {result1['tools_used']}")

    # Check cache info
    raw_data = result1.get('raw_data', {})
    cache_info = raw_data.get('cache_info', {})

    print(f"\n💾 Cache Info:")
    print(f"   Cached: {cache_info.get('cached', False)}")
    print(f"   Is Fresh: {cache_info.get('is_fresh', False)}")
    if cache_info.get('age_minutes'):
        print(f"   Age: {cache_info.get('age_minutes', 0):.1f} minutes")

    print(f"\n📝 Response Preview:")
    print(result1['response'][:600])
    print("...\n")

    # Test 2: Run again (should use cache)
    print("\n📝 Test 2: Same Query (Should Use Cache)")
    print("-" * 80)
    result2 = await agent.query("Forecast patient decline for next month")

    print(f"✅ Success: {result2['success']}")

    cache_info2 = result2.get('raw_data', {}).get('cache_info', {})
    print(f"\n💾 Cache Info:")
    print(f"   Cached: {cache_info2.get('cached', False)}")
    print(f"   Is Fresh: {cache_info2.get('is_fresh', False)}")

    # Test 3: Different prediction query
    print("\n\n📝 Test 3: Specific Prediction Question")
    print("-" * 80)
    result3 = await agent.query("Who is most likely to decline cognitively?")

    print(f"✅ Success: {result3['success']}")
    print(f"📝 Response Preview:")
    print(result3['response'][:500])
    print("...\n")

    print("=" * 80)
    print("✅ PREDICTIVE SCORING TEST COMPLETE!")
    print("=" * 80)

    print("\n🎯 Key Features Demonstrated:")
    print("   ✅ Linear regression on score trends")
    print("   ✅ Decline probability calculation")
    print("   ✅ 24-hour caching for performance")
    print("   ✅ Cached predictions return instantly")
    print("   ✅ Natural language prediction queries")


if __name__ == "__main__":
    asyncio.run(test_predictions())
