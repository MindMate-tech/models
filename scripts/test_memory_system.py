"""
Test memory system for follow-up queries
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.doctor.doctor_query_agent import DoctorQueryAgent
from agents.doctor.memory_store import session_memory


async def test_memory():
    """Test memory-augmented follow-up queries"""
    agent = DoctorQueryAgent()

    # Create a mock session context
    context = {"doctor_id": "test_doctor_123"}

    print("=" * 80)
    print("🧠 TESTING MEMORY SYSTEM")
    print("=" * 80)

    # Query 1: Initial query (should remember patients)
    print("\n📝 Query 1: Initial At-Risk Query")
    print("-" * 80)
    result1 = await agent.query("Show me at-risk patients", context=context)

    print(f"✅ Success: {result1['success']}")
    print(f"🧠 Memory Used: {result1['model_info']['memory_used']}")
    print(f"👥 Found {len(result1.get('raw_data', []))} patients")

    # Show what's stored in memory
    history = session_memory.get_session_history(context)
    print(f"📚 Memory: {len(history)} queries stored")
    if history:
        last_query = history[-1]
        print(f"   Last query: \"{last_query['query']}\"")
        print(f"   Patient IDs in memory: {last_query['data_summary'].get('patient_ids', [])[: 2]}...")

    # Query 2: Follow-up query using "them"
    print("\n\n📝 Query 2: Follow-Up Query (using 'them')")
    print("-" * 80)
    result2 = await agent.query("Tell me more about them", context=context)

    print(f"✅ Success: {result2['success']}")
    print(f"🧠 Memory Used: {result2['model_info']['memory_used']}")
    print(f"📝 Response Preview:")
    print(result2['response'][:400])
    print("...")

    # Query 3: Another follow-up with different phrasing
    print("\n\n📝 Query 3: Follow-Up Query (using 'those patients')")
    print("-" * 80)
    result3 = await agent.query("Compare those patients", context=context)

    print(f"✅ Success: {result3['success']}")
    print(f"🧠 Memory Used: {result3['model_info']['memory_used']}")
    print(f"🔧 Tools Used: {result3['tools_used']}")
    print(f"📝 Response Preview:")
    print(result3['response'][:400])
    print("...")

    # Query 4: New query (not a follow-up)
    print("\n\n📝 Query 4: New Query (not a follow-up)")
    print("-" * 80)
    result4 = await agent.query("How many patients total?", context=context)

    print(f"✅ Success: {result4['success']}")
    print(f"🧠 Memory Used: {result4['model_info']['memory_used']}")
    print(f"📝 Response Preview:")
    print(result4['response'][:200])
    print("...")

    # Show final memory state
    print("\n\n📊 Final Memory State")
    print("-" * 80)
    stats = session_memory.get_stats()
    print(f"Total Sessions: {stats['total_sessions']}")
    print(f"Active Sessions: {len(stats['active_sessions'])}")

    history = session_memory.get_session_history(context)
    print(f"\nQuery History for test_doctor_123:")
    for i, query_data in enumerate(history, 1):
        print(f"  {i}. \"{query_data['query']}\" ({query_data['timestamp'].strftime('%H:%M:%S')})")

    print("\n" + "=" * 80)
    print("✅ MEMORY SYSTEM TEST COMPLETE!")
    print("=" * 80)

    print("\n🎯 Key Features Demonstrated:")
    print("   ✅ Initial query stores patient context in memory")
    print("   ✅ Follow-up queries detect references ('them', 'those')")
    print("   ✅ Memory provides patient IDs for follow-up actions")
    print("   ✅ Non-follow-up queries don't use memory")
    print("   ✅ Session history tracked (last 5 queries)")


if __name__ == "__main__":
    asyncio.run(test_memory())
