"""
Test MRI Upload Service
Tests the external MRI processing service at http://52.15.158.102:8001
"""
import requests
import time
import os


MRI_SERVICE_URL = "http://3.143.242.154"
TEST_MRI_FILE = "path/to/venv/lib/python3.12/site-packages/nibabel/tests/data/anatomical.nii"


def test_mri_upload():
    """Test MRI file upload and processing"""

    print("=" * 80)
    print("🧠 TESTING MRI UPLOAD SERVICE")
    print("=" * 80)

    # Check if test file exists
    print(f"\n📂 Step 1: Checking test MRI file...")
    print("-" * 80)

    if not os.path.exists(TEST_MRI_FILE):
        print(f"❌ Test file not found: {TEST_MRI_FILE}")
        return

    file_size = os.path.getsize(TEST_MRI_FILE)
    print(f"✅ Test file found: {TEST_MRI_FILE}")
    print(f"   Size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")

    # Test 1: Check if service is accessible
    print(f"\n\n{'=' * 80}")
    print("📝 Test 1: Check Service Availability")
    print("=" * 80)

    try:
        print(f"\n🔄 Connecting to {MRI_SERVICE_URL}...")
        response = requests.get(MRI_SERVICE_URL, timeout=10)
        print(f"✅ Service is accessible!")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   Response: {data}")
            except:
                print(f"   Response: {response.text[:200]}")
    except requests.exceptions.Timeout:
        print(f"⏱️  Connection timeout (10s)")
        print("   Service might be slow or unavailable")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection failed: {e}")
        print("   Service might be down or unreachable")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    # Test 2: Upload MRI file
    print(f"\n\n{'=' * 80}")
    print("📝 Test 2: Upload MRI File")
    print("=" * 80)

    try:
        print(f"\n🔄 Uploading MRI file...")
        print(f"   File: {os.path.basename(TEST_MRI_FILE)}")
        print(f"   Age: 50")
        print(f"   Sex: Male")

        with open(TEST_MRI_FILE, 'rb') as f:
            files = {'file': (os.path.basename(TEST_MRI_FILE), f, 'application/octet-stream')}
            data = {'age': '50', 'sex': 'Male'}

            upload_response = requests.post(
                f"{MRI_SERVICE_URL}/upload",
                files=files,
                data=data,
                timeout=60
            )

        print(f"\n📊 Upload Status: {upload_response.status_code}")

        if upload_response.status_code == 200:
            result = upload_response.json()
            print(f"✅ Upload successful!")

            if 'job_id' in result:
                job_id = result['job_id']
                print(f"   Job ID: {job_id}")

                # Test 3: Poll for results
                print(f"\n\n{'=' * 80}")
                print("📝 Test 3: Poll for Processing Results")
                print("=" * 80)

                max_attempts = 30  # 30 seconds
                attempt = 0

                while attempt < max_attempts:
                    attempt += 1
                    print(f"\n🔄 Polling attempt {attempt}/{max_attempts}...")

                    status_response = requests.get(
                        f"{MRI_SERVICE_URL}/status/{job_id}",
                        timeout=10
                    )

                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"   Status: {status_data.get('status', 'unknown')}")

                        if status_data.get('status') == 'completed':
                            print(f"\n✅ Processing complete!")
                            print(f"\n📊 Results:")
                            print("-" * 80)

                            # Print results
                            if 'result' in status_data:
                                result_data = status_data['result']
                                print(f"Result data: {result_data}")

                                # Pretty print brain regions if available
                                if isinstance(result_data, dict):
                                    for key, value in result_data.items():
                                        print(f"   {key}: {value}")
                            else:
                                print(status_data)
                            print("-" * 80)
                            break

                        elif status_data.get('status') == 'failed':
                            print(f"❌ Processing failed!")
                            print(f"   Error: {status_data.get('error', 'Unknown error')}")
                            break

                        elif status_data.get('status') == 'processing':
                            print(f"   ⏳ Still processing...")
                            time.sleep(1)

                        else:
                            print(f"   Status: {status_data}")
                            time.sleep(1)
                    else:
                        print(f"   ❌ Status check failed: {status_response.status_code}")
                        break

                if attempt >= max_attempts:
                    print(f"\n⏱️  Timeout: Processing took longer than {max_attempts} seconds")

            else:
                print(f"   Response: {result}")
        else:
            print(f"❌ Upload failed: {upload_response.status_code}")
            print(f"   Response: {upload_response.text[:500]}")

    except requests.exceptions.Timeout:
        print(f"\n⏱️  Upload timeout (60s)")
        print("   File might be too large or service is slow")
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ Connection failed during upload: {e}")
    except Exception as e:
        print(f"\n❌ Upload error: {e}")
        import traceback
        traceback.print_exc()

    # Summary
    print(f"\n\n{'=' * 80}")
    print("✅ MRI UPLOAD TEST COMPLETE!")
    print("=" * 80)

    print("\n📊 Service Information:")
    print(f"   URL: {MRI_SERVICE_URL}")
    print(f"   Upload endpoint: POST /upload")
    print(f"   Status endpoint: GET /status/{{job_id}}")

    print("\n📝 Expected Flow:")
    print("   1. Upload MRI file with age and sex")
    print("   2. Receive job_id")
    print("   3. Poll /status/{job_id} until completed")
    print("   4. Get brain analysis results")


if __name__ == "__main__":
    test_mri_upload()
