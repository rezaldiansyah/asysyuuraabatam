import requests
import json
import sys

API_URL = "http://localhost:8000"
LOGIN_URL = f"{API_URL}/auth/login"
SCHEDULE_URL = f"{API_URL}/academic/schedules"

def get_token():
    try:
        response = requests.post(LOGIN_URL, data={"username": "999999", "password": "password"})
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        print(f"Login failed: {e}")
        sys.exit(1)

def test_schedule_conflict():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Prerequisite: Ensure we have valid IDs. 
    # Fetch academic year, classroom, subject, teacher first to be safe, or use assumed IDs from seed.
    # Assuming IDs 1 exist for all.
    
    # 1. Create Base Schedule
    base_schedule = {
        "academic_year_id": 1,
        "classroom_id": 1,
        "subject_id": 1,
        "teacher_id": 1,
        "day": "SENIN",
        "start_time": "08:00",
        "end_time": "09:00"
    }

    print("1. Creating Base Schedule...")
    res = requests.post(SCHEDULE_URL, json=base_schedule, headers=headers)
    if res.status_code == 200:
        print("   Success: Created Schedule 1")
    else:
        print(f"   Note: Failed or already exists ({res.status_code}). Proceeding...")
        # If it failed because it exists, that's fine for testing conflicts next.
        # But if it failed for other reasons, next tests might be invalid.

    # 2. Test Room Conflict (Same Room, Overlapping Time)
    print("\n2. Testing Room Conflict...")
    conflict_room = base_schedule.copy()
    conflict_room["teacher_id"] = 2 # Different teacher
    conflict_room["subject_id"] = 2
    # Same room (1), Same day, Overlapping time (08:30 - 09:30)
    conflict_room["start_time"] = "08:30"
    conflict_room["end_time"] = "09:30"
    
    res = requests.post(SCHEDULE_URL, json=conflict_room, headers=headers)
    if res.status_code == 400 and "Room Conflict" in res.json()["detail"]:
        print("   PASS: Detected Room Conflict correctly.")
    else:
        print(f"   FAIL: Expected 400 Room Conflict, got {res.status_code} - {res.text}")

    # 3. Test Teacher Conflict (Same Teacher, Different Room)
    print("\n3. Testing Teacher Conflict...")
    conflict_teacher = base_schedule.copy()
    conflict_teacher["classroom_id"] = 2 # Different room
    conflict_teacher["teacher_id"] = 1 # SAME TEACHER
    # Overlapping time (08:30 - 09:30)
    conflict_teacher["start_time"] = "08:30"
    conflict_teacher["end_time"] = "09:30"

    res = requests.post(SCHEDULE_URL, json=conflict_teacher, headers=headers)
    if res.status_code == 400 and "Teacher Conflict" in res.json()["detail"]:
        print("   PASS: Detected Teacher Conflict correctly.")
    else:
        print(f"   FAIL: Expected 400 Teacher Conflict, got {res.status_code} - {res.text}")

if __name__ == "__main__":
    test_schedule_conflict()
