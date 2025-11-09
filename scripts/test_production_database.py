"""
Simple diagnostic script to check production database contents
"""
import asyncio
import httpx

PROD_API = "https://mindmate-cognitive-api.onrender.com"

async def test_health():
    """Test if API is alive"""
    print("\n1️⃣  Testing API health...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{PROD_API}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")

async def test_at_risk_different_thresholds():
    """Test at-risk endpoint with different thresholds"""
    print("\n2️⃣  Testing at-risk endpoint with different thresholds...")

    thresholds = [0.5, 0.7, 0.9, 0.99]

    async with httpx.AsyncClient(timeout=30.0) as client:
        for threshold in thresholds:
            print(f"\n   Threshold: {threshold}")
            response = await client.get(f"{PROD_API}/doctor/at-risk?threshold={threshold}")
            data = response.json()

            if response.status_code == 200:
                count = len(data.get("patients", []))
                print(f"   ✅ Found {count} at-risk patients")

                if count > 0:
                    print(f"   First patient: {data['patients'][0].get('name', 'Unknown')}")
                    print(f"   Score: {data['patients'][0].get('average_score', 0):.1%}")
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   {data}")

async def test_simple_query():
    """Test simple AI query"""
    print("\n3️⃣  Testing simple AI query...")

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{PROD_API}/doctor/query",
            json={"query": "How many patients are in the database?"}
        )

        print(f"   Status: {response.status_code}")
        data = response.json()

        if data.get("success"):
            print(f"   ✅ AI Response:")
            print(f"   {data.get('response', 'No response')[:500]}")
        else:
            print(f"   ❌ Error: {data.get('error', 'Unknown error')}")

async def main():
    print("="*80)
    print("🔍 PRODUCTION DATABASE DIAGNOSTIC TEST")
    print("="*80)

    try:
        await test_health()
        await test_at_risk_different_thresholds()
        await test_simple_query()

        print("\n" + "="*80)
        print("✅ DIAGNOSTIC COMPLETE")
        print("="*80)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
