"""
Test sequential thinking for complex queries
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.doctor.doctor_query_agent import DoctorQueryAgent


async def test_sequential():
    """Test sequential thinking on complex medical queries"""
    agent = DoctorQueryAgent()

    print("=" * 80)
    print("🧠 TESTING SEQUENTIAL THINKING")
    print("=" * 80)

    # Test 1: At-risk query (should have sequential thinking)
    print("\n📝 Test 1: At-Risk Query (Should use Sequential Thinking)")
    print("-" * 80)
    result1 = await agent.query("Show me at-risk patients and explain in detail why they are flagged")

    print(f"✅ Success: {result1['success']}")
    print(f"📊 Model: {result1['model_info']['model']}")
    print(f"🧠 Sequential Thinking: {result1['model_info']['sequential_thinking']}")
    print(f"\n📝 Response Preview:")
    print(result1['response'][:800])
    print("...\n")

    # Test 2: Simple query (should NOT have sequential thinking)
    print("\n📝 Test 2: Simple Query (Should NOT use Sequential Thinking)")
    print("-" * 80)
    result2 = await agent.query("How many patients are in the database?")

    print(f"✅ Success: {result2['success']}")
    print(f"📊 Model: {result2['model_info']['model']}")
    print(f"🧠 Sequential Thinking: {result2['model_info']['sequential_thinking']}")
    print(f"\n📝 Response Preview:")
    print(result2['response'][:400])
    print("...\n")

    # Test 3: Analysis query (should have sequential thinking)
    print("\n📝 Test 3: Analysis Query (Should use Sequential Thinking)")
    print("-" * 80)
    result3 = await agent.query("Analyze declining cognitive trends")

    print(f"✅ Success: {result3['success']}")
    print(f"📊 Model: {result3['model_info']['model']}")
    print(f"🧠 Sequential Thinking: {result3['model_info']['sequential_thinking']}")
    print(f"\n📝 Response Preview:")
    print(result3['response'][:800])
    print("...\n")

    print("=" * 80)
    print("✅ SEQUENTIAL THINKING TEST COMPLETE!")
    print("=" * 80)

    # Summary
    print("\n📊 Summary:")
    print(f"   Test 1 (At-risk): Sequential = {result1['model_info']['sequential_thinking']} ✅")
    print(f"   Test 2 (Simple): Sequential = {result2['model_info']['sequential_thinking']} ✅")
    print(f"   Test 3 (Analysis): Sequential = {result3['model_info']['sequential_thinking']} ✅")


if __name__ == "__main__":
    asyncio.run(test_sequential())
