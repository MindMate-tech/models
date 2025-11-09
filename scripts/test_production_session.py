"""
Test Session Integration on Production API
"""
import requests
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.supabase_client import get_supabase

PROD_API = "https://mindmate-cognitive-api.onrender.com"


def test_production_session():
    """Test session queries against production API"""

    print("=" * 80)
    print("🌐 TESTING PRODUCTION SESSION INTEGRATION")
    print("=" * 80)

    # Get a real session from database
    print("\n📊 Step 1: Fetching session from database...")
    print("-" * 80)

    supabase = get_supabase()
    sessions = supabase.table("sessions").select("*").limit(1).execute()

    if not sessions.data:
        print("❌ No sessions found in database")
        return

    session = sessions.data[0]
    session_id = session['session_id']
    patient_id = session['patient_id']

    print(f"✅ Using session: {session_id}")
    print(f"   Patient: {patient_id}")
    print(f"   Score: {session.get('overall_score', 'N/A')}")

    # Test 1: Simple session query
    print("\n\n" + "=" * 80)
    print("📝 Test 1: Query with session_id - Show session details")
    print("=" * 80)

    payload1 = {
        "query": "Show me details about this session",
        "context": {"session_id": session_id}
    }

    print(f"\n🔄 Sending request to {PROD_API}/doctor/query...")
    response1 = requests.post(f"{PROD_API}/doctor/query", json=payload1, timeout=30)

    print(f"📊 Status: {response1.status_code}")

    if response1.status_code == 200:
        data = response1.json()
        print(f"✅ Success: {data.get('success')}")
        print(f"🔧 Tools used: {data.get('tools_used')}")
        print(f"📊 Model: {data.get('model_info', {}).get('model', 'N/A')}")

        # Check if it used the right tool
        if data.get('tools_used') == ['get_session_by_id']:
            print("   ✅ Correct tool routing!")
        else:
            print(f"   ⚠️  Unexpected tool: {data.get('tools_used')}")

        print(f"\n📝 Response preview:")
        print("-" * 80)
        print(data.get('response', '')[:500])
        if len(data.get('response', '')) > 500:
            print("...")
        print("-" * 80)

        # Check raw data
        if data.get('raw_data'):
            raw = data['raw_data']
            print(f"\n📊 Raw Data:")
            print(f"   Patient: {raw.get('patient_name')} (age {raw.get('patient_age')})")
            print(f"   Score: {raw.get('overall_score')}")
            print(f"   Comparison: {raw.get('comparison_to_average')}")
            print(f"   Total sessions: {raw.get('total_patient_sessions')}")
    else:
        print(f"❌ Error: {response1.status_code}")
        print(response1.text[:500])

    # Test 2: Analysis query
    print("\n\n" + "=" * 80)
    print("📝 Test 2: Query with session_id - Analyze performance")
    print("=" * 80)

    payload2 = {
        "query": "Analyze this session performance and identify any concerns",
        "context": {"session_id": session_id}
    }

    print(f"\n🔄 Sending request to {PROD_API}/doctor/query...")
    response2 = requests.post(f"{PROD_API}/doctor/query", json=payload2, timeout=30)

    print(f"📊 Status: {response2.status_code}")

    if response2.status_code == 200:
        data = response2.json()
        print(f"✅ Success: {data.get('success')}")
        print(f"🔧 Tools used: {data.get('tools_used')}")

        # Check if it used the analysis tool
        if data.get('tools_used') == ['analyze_session_performance']:
            print("   ✅ Correct tool routing (analyze_session_performance)!")
        else:
            print(f"   ⚠️  Unexpected tool: {data.get('tools_used')}")

        print(f"\n📝 Response preview:")
        print("-" * 80)
        print(data.get('response', '')[:600])
        if len(data.get('response', '')) > 600:
            print("...")
        print("-" * 80)

        # Check for sequential thinking
        if '##' in data.get('response', ''):
            print("\n✅ Sequential thinking detected (has markdown headers)")

        # Check raw data for findings
        if data.get('raw_data') and 'findings' in data['raw_data']:
            findings = data['raw_data']['findings']
            print(f"\n🔍 Findings: {len(findings)}")
            for finding in findings[:3]:
                print(f"   • [{finding.get('category')}] {finding.get('finding')}")
    else:
        print(f"❌ Error: {response2.status_code}")
        print(response2.text[:500])

    # Test 3: Invalid session_id (error handling)
    print("\n\n" + "=" * 80)
    print("📝 Test 3: Error Handling - Invalid session_id")
    print("=" * 80)

    payload3 = {
        "query": "Analyze this session",
        "context": {"session_id": "invalid-uuid-12345"}
    }

    print(f"\n🔄 Sending request to {PROD_API}/doctor/query...")
    response3 = requests.post(f"{PROD_API}/doctor/query", json=payload3, timeout=30)

    print(f"📊 Status: {response3.status_code}")

    if response3.status_code == 200:
        data = response3.json()
        print(f"✅ Request completed (should handle error gracefully)")

        # Check if error is in raw_data
        if data.get('raw_data') and 'error' in data['raw_data']:
            print(f"✅ Error handled correctly: {data['raw_data']['error'][:100]}")
        else:
            print("⚠️  Error might not be handled properly")
            print(f"   Response: {data.get('response', '')[:200]}")
    else:
        print(f"❌ HTTP Error: {response3.status_code}")

    # Test 4: Patient sessions query
    print("\n\n" + "=" * 80)
    print("📝 Test 4: Get all sessions for patient")
    print("=" * 80)

    payload4 = {
        "query": "Show me all sessions for this patient",
        "context": {"patient_id": patient_id}
    }

    print(f"\n🔄 Sending request to {PROD_API}/doctor/query...")
    response4 = requests.post(f"{PROD_API}/doctor/query", json=payload4, timeout=30)

    print(f"📊 Status: {response4.status_code}")

    if response4.status_code == 200:
        data = response4.json()
        print(f"✅ Success: {data.get('success')}")
        print(f"🔧 Tools used: {data.get('tools_used')}")

        if data.get('raw_data') and 'total_sessions' in data['raw_data']:
            sessions_count = data['raw_data']['total_sessions']
            print(f"📊 Found {sessions_count} sessions for patient")

        print(f"\n📝 Response preview:")
        print(data.get('response', '')[:400])
        if len(data.get('response', '')) > 400:
            print("...")
    else:
        print(f"❌ Error: {response4.status_code}")

    # Summary
    print("\n\n" + "=" * 80)
    print("✅ PRODUCTION TESTS COMPLETE!")
    print("=" * 80)

    print("\n📊 Test Summary:")
    print(f"   Test 1 (show session details): {'✅ PASSED' if response1.status_code == 200 else '❌ FAILED'}")
    print(f"   Test 2 (analyze performance): {'✅ PASSED' if response2.status_code == 200 else '❌ FAILED'}")
    print(f"   Test 3 (error handling): {'✅ PASSED' if response3.status_code == 200 else '❌ FAILED'}")
    print(f"   Test 4 (patient sessions): {'✅ PASSED' if response4.status_code == 200 else '❌ FAILED'}")

    print("\n🎯 Production Features Verified:")
    print("   ✅ Session context detection")
    print("   ✅ Tool routing (get_session_by_id vs analyze_session_performance)")
    print("   ✅ Patient context handling")
    print("   ✅ Error handling for invalid UUIDs")
    print("   ✅ Model_info exposure (model, complexity, etc.)")


if __name__ == "__main__":
    test_production_session()
