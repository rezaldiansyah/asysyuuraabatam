import requests
import os
import sys

# Add parent directory to path to import local modules if needed (though we use requests here)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_URL = "http://localhost:8000"
LOGIN_URL = f"{API_URL}/auth/login"
UPLOAD_URL = f"{API_URL}/cms/upload"

def get_token():
    try:
        response = requests.post(LOGIN_URL, data={
            "username": "999999", # Admin NIK
            "password": "password" # Reset password from previous step, or admin123
        })
        
        # Try default password if reset failed or not run
        if response.status_code != 200:
             response = requests.post(LOGIN_URL, data={
                "username": "999999",
                "password": "admin123"
            })
            
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

def test_upload():
    token = get_token()
    if not token:
        return

    # Create dummy image
    dummy_filename = "test_image.txt"
    with open(dummy_filename, "w") as f:
        f.write("This is a dummy image content.")

    try:
        files = {'file': (dummy_filename, open(dummy_filename, 'rb'), 'text/plain')}
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.post(UPLOAD_URL, headers=headers, files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("Upload Successful!")
            print(f"URL: {data['url']}")
            
            # Verify URL accessibility
            # Note: requires server running. Assuming it is or will be.
            # But we can check local file existence too if running locally.
            filename = data['url'].split("/")[-1]
            local_path = os.path.join("uploads", filename)
            # The script is in apps/api/scripts, uploads is in apps/api/uploads
            # relative to script: ../uploads/filename
            relative_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", filename)
            
            if os.path.exists(relative_path):
                print(f"File verified at: {relative_path}")
            else:
                print(f"Warning: File not found at expected local path: {relative_path}")
                
        else:
            print(f"Upload failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        if os.path.exists(dummy_filename):
            os.remove(dummy_filename)

if __name__ == "__main__":
    test_upload()
