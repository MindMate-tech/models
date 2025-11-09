"""
Test intelligent model routing
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.doctor.doctor_query_agent import DoctorQueryAgent


async def test_routing():
    """Test model routing with different query complexities"""
    agent = DoctorQueryAgent()

    test_queries = [
        # Simple queries (should use Haiku)
        ("How many patients are in the database?", "simple", "Haiku"),
        ("Find all female patients", "simple", "Haiku"),
        ("List all patients", "simple", "Haiku"),

        # Complex queries (should use Sonnet)
        ("Show me at-risk patients and explain why", "complex", "Sonnet"),
        ("Analyze declining patients", "complex", "Sonnet"),
        ("Compare patient performance trends", "complex", "Sonnet"),
        ("What actions should I take for high-risk patients?", "complex", "Sonnet"),
    ]

    print("=" * 80)
    print("🧪 TESTING INTELLIGENT MODEL ROUTING")
    print("=" * 80)

    for query, expected_complexity, expected_model in test_queries:
        print(f"\n📝 Query: \"{query}\"")

        # Analyze complexity
        complexity_info = agent._analyze_query_complexity(query)

        print(f"   Complexity: {complexity_info['complexity']} (expected: {expected_complexity})")
        print(f"   Model: {complexity_info['model']}")
        print(f"   Reasoning: {complexity_info['reasoning']}")

        # Verify expectations
        if complexity_info['complexity'] == expected_complexity:
            print(f"   ✅ Correct complexity detected!")
        else:
            print(f"   ❌ Expected {expected_complexity}, got {complexity_info['complexity']}")

        if expected_model.lower() in complexity_info['model'].lower():
            print(f"   ✅ Correct model selected!")
        else:
            print(f"   ❌ Expected {expected_model}, got {complexity_info['model']}")

    print("\n" + "=" * 80)
    print("🎯 LIVE QUERY TEST (Simple)")
    print("=" * 80)

    # Test with a real simple query
    simple_result = await agent.query("How many patients are in the database?")
    print(f"\n✅ Success: {simple_result['success']}")
    print(f"📊 Model Used: {simple_result.get('model_info', {}).get('model', 'N/A')}")
    print(f"⚡ Complexity: {simple_result.get('model_info', {}).get('complexity', 'N/A')}")
    print(f"📝 Response: {simple_result['response'][:200]}...")

    print("\n" + "=" * 80)
    print("🎯 LIVE QUERY TEST (Complex)")
    print("=" * 80)

    # Test with a real complex query
    complex_result = await agent.query("Show me at-risk patients with detailed reasoning")
    print(f"\n✅ Success: {complex_result['success']}")
    print(f"📊 Model Used: {complex_result.get('model_info', {}).get('model', 'N/A')}")
    print(f"⚡ Complexity: {complex_result.get('model_info', {}).get('complexity', 'N/A')}")
    print(f"📝 Response: {complex_result['response'][:200]}...")

    print("\n" + "=" * 80)
    print("✅ MODEL ROUTING TEST COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_routing())
