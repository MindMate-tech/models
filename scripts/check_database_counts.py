"""
Direct database query to count patients and sessions
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.supabase_client import get_supabase

def main():
    print("\n" + "="*80)
    print("🔍 DIRECT DATABASE COUNT CHECK")
    print("="*80)

    try:
        supabase = get_supabase()

        # Count patients
        print("\n1️⃣  Counting patients...")
        patients_result = supabase.table("patients").select("*", count="exact").execute()
        patient_count = len(patients_result.data)
        print(f"   ✅ Total patients: {patient_count}")

        if patient_count > 0:
            print(f"\n   Sample patients (first patient's columns):")
            print(f"   Columns: {list(patients_result.data[0].keys())}")
            print(f"\n   First 5 patients:")
            for i, p in enumerate(patients_result.data[:5], 1):
                print(f"   {i}. {p}")

        # Count sessions
        print("\n2️⃣  Counting sessions...")
        sessions_result = supabase.table("sessions").select("*", count="exact").execute()
        session_count = len(sessions_result.data)
        print(f"   ✅ Total sessions: {session_count}")

        if session_count > 0:
            print(f"\n   Sample sessions (first session's columns):")
            print(f"   Columns: {list(sessions_result.data[0].keys())}")
            print(f"\n   First 5 sessions:")
            for i, s in enumerate(sessions_result.data[:5], 1):
                print(f"   {i}. {s}")

        # Calculate at-risk manually
        print("\n3️⃣  Manual at-risk calculation...")

        if patient_count > 0 and session_count > 0:
            # Get all patients with their sessions
            patients_with_sessions = supabase.table("patients").select("*, sessions(*)").execute()

            at_risk_count = 0
            all_patients_count = 0
            for patient in patients_with_sessions.data:
                sessions = patient.get('sessions', [])
                if sessions:
                    all_patients_count += 1
                    # overall_score is out of 100, so divide by 100 to get percentage
                    avg_score = sum(s.get('overall_score', 0) for s in sessions) / len(sessions) / 100
                    if avg_score < 0.5:
                        at_risk_count += 1
                        print(f"   ⚠️  {patient.get('name', 'Unknown')}: avg score {avg_score:.1%} from {len(sessions)} sessions")
                    else:
                        print(f"   ✅ {patient.get('name', 'Unknown')}: avg score {avg_score:.1%} from {len(sessions)} sessions")

            print(f"\n   Total patients with sessions: {all_patients_count}")
            print(f"   Total at-risk patients (avg < 50%): {at_risk_count}")

        print("\n" + "="*80)
        print("✅ DATABASE CHECK COMPLETE")
        print("="*80)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
