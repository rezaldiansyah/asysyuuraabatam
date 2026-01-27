import requests
import json
import sys

API_URL = "http://localhost:8000"
CMS_URL = f"{API_URL}/cms/content"
PUBLIC_URL = f"{API_URL}/public/content"
LOGIN_URL = f"{API_URL}/auth/login"

def get_token():
    try:
        response = requests.post(LOGIN_URL, data={
            "username": "999999",
            "password": "admin123"
        })
        if response.status_code == 200:
            return response.json()["access_token"]
        return None
    except Exception as e:
        print(f"Login Error: {e}")
        return None

def test_json_content():
    token = get_token()
    if not token:
        print("Failed to get token")
        return

    # 1. Update Features for SDIT
    section_key = "sdit_features"
    features_data = [
        {"id": "1", "title": "Tahfidz Intensif", "description": "Program hafalan 2 juz dalam setahun.", "icon": "Sun"},
        {"id": "2", "title": "Kelas Full Day", "description": "Pembelajaran hingga sore hari dengan kegiatan positif.", "icon": "BookOpen"}
    ]
    json_str = json.dumps(features_data)
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "section_key": section_key,
        "content_json": json_str
    }
    
    print(f"Updating {section_key}...")
    res = requests.put(f"{CMS_URL}/{section_key}", json=payload, headers=headers)
    
    if res.status_code == 200:
        print("Update Success!")
    else:
        print(f"Update Failed: {res.status_code} - {res.text}")
        return

    # 2. Verify with Public Get
    print(f"Fetching {section_key}...")
    res = requests.get(f"{PUBLIC_URL}/{section_key}")
    
    if res.status_code == 200:
        data = res.json()
        print("Fetch Success!")
        print(f"Content JSON: {data.get('content_json')}")
        
        # Parse back
        fetched_json = json.loads(data.get('content_json'))
        if len(fetched_json) == 2 and fetched_json[0]['title'] == "Tahfidz Intensif":
            print("VERIFICATION PASSED: Data integrity confirmed.")
        else:
            print("VERIFICATION FAILED: Data mismatch.")
    else:
        print(f"Fetch Failed: {res.status_code}")

if __name__ == "__main__":
    test_json_content()
