import os
import sys
import asyncio
from datetime import datetime

# Set path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models
from routers import meeting
from fastapi import HTTPException
import auth

async def run_tests():
    db = SessionLocal()
    print("--- 🧪 Running Sprint 3 Comprehensive Unit & Integration Tests ---")
    
    # 1. Setup test users
    ketua_role = db.query(models.Role).filter(models.Role.code == "ketua_yayasan").first()
    if not ketua_role:
        ketua_role = models.Role(code="ketua_yayasan", name="Ketua Yayasan", scope="yayasan")
        db.add(ketua_role)
        db.commit()
        
    kepala_role = db.query(models.Role).filter(models.Role.code == "kepala_unit").first()
    guru_role = db.query(models.Role).filter(models.Role.code == "guru").first()
    
    # Test Ketua User
    ketua = db.query(models.User).filter(models.User.email == "ketua_test@asysyuura.sch.id").first()
    if not ketua:
        ketua = models.User(
            email="ketua_test@asysyuura.sch.id",
            full_name="Ustadz Ketua Yayasan",
            nik="100001",
            password_hash=auth.get_password_hash("password"),
            role_id=ketua_role.id,
            is_active=True
        )
        db.add(ketua)
        db.commit()
        db.refresh(ketua)

    # Test Kepala Unit User
    kepala = db.query(models.User).filter(models.User.email == "kepala_test@asysyuura.sch.id").first()
    if not kepala:
        kepala = models.User(
            email="kepala_test@asysyuura.sch.id",
            full_name="Ustadz Kepala SDIT",
            nik="200001",
            password_hash=auth.get_password_hash("password"),
            role_id=kepala_role.id,
            is_active=True
        )
        db.add(kepala)
        db.commit()
        db.refresh(kepala)

    # Test Guru / Notulis User
    notulis = db.query(models.User).filter(models.User.email == "notulis_test@asysyuura.sch.id").first()
    if not notulis:
        notulis = models.User(
            email="notulis_test@asysyuura.sch.id",
            full_name="Ustadzah Notulis",
            nik="300001",
            password_hash=auth.get_password_hash("password"),
            role_id=guru_role.id if guru_role else ketua_role.id,
            is_active=True
        )
        db.add(notulis)
        db.commit()
        db.refresh(notulis)

    # 2. Test Create Meeting Minute (Draft)
    payload_minute = {
        "title": "Rapat Koordinasi Anggaran Yayasan 2026",
        "scope": "yayasan_global",
        "meeting_type": "rapat_yayasan",
        "meeting_date": "2026-09-30",
        "start_time": "09:00",
        "end_time": "12:00",
        "location": "Aula Utama Yayasan",
        "agenda": ["Pembahasan RAPBS", "Rencana Renovasi Perpustakaan"],
        "content": "<p>Rapat dibuka oleh Ketua Yayasan. Dilanjutkan pemaparan realisasi anggaran semester sebelumnya.</p>",
        "decisions": ["Pagu anggaran renovasi disetujui sebesar 50 juta rupiah."],
        "attendees": [ketua.id, kepala.id, notulis.id],
        "action_items": [
            {
                "task_description": "Finalisasi draf RAB renovasi perpustakaan",
                "pic_user_id": kepala.id,
                "deadline": "2026-10-05",
                "notes": "Koordinasi dengan bagian sarpras"
            }
        ]
    }
    
    res = await meeting.create_meeting_minute(payload_minute, current_user=notulis, db=db)
    minute_id = res["id"]
    nomor_notulen = res["nomor_notulen"]
    print(f"✅ Created minute #{minute_id}: {nomor_notulen}")

    # 3. Test Submit Minute for Approval
    res = await meeting.submit_meeting_minute(minute_id, current_user=notulis, db=db)
    assert res["status"] == "submitted"
    print("✅ Successfully submitted minute for approval")

    # 4. Test Multi-tier Security: Kepala Unit CANNOT approve Yayasan Global meeting!
    try:
        await meeting.approve_meeting_minute(minute_id, current_user=kepala, db=db)
        assert False, "Should have raised 403 Forbidden!"
    except HTTPException as e:
        assert e.status_code == 403
        print(f"✅ Verified Multi-tier RBAC: Kepala Unit blocked from approving Yayasan Global meeting (403: {e.detail})")

    # 5. Test Rejection flow: Ketua Yayasan requests revision with note
    reject_payload = {"notes": "Mohon cantumkan rincian vendor sarpras yang direkomendasikan."}
    res = await meeting.reject_meeting_minute(minute_id, payload=reject_payload, current_user=ketua, db=db)
    assert res["status"] == "rejected"
    print("✅ Successfully rejected/requested revision with notes")

    # Verify detail shows rejection note
    detail = await meeting.get_meeting_minute_detail(minute_id, current_user=notulis, db=db)
    assert detail["status"] == "rejected"
    assert detail["approval_notes"] == reject_payload["notes"]
    print(f"✅ Verified detail contains approval notes: '{detail['approval_notes']}'")

    # 6. Test Update Minute by Notulis
    update_payload = {
        "title": "Rapat Koordinasi Anggaran Yayasan 2026 (Revisi)",
        "content": "<p>Rapat dibuka oleh Ketua Yayasan. Pagu anggaran disetujui 50 juta dengan rekomendasi 2 vendor lokal.</p>"
    }
    res = await meeting.update_meeting_minute(minute_id, data=update_payload, current_user=notulis, db=db)
    assert res["id"] == minute_id
    print("✅ Successfully updated minute by notulis")

    # 7. Test Re-submit & Authorized Approval by Ketua Yayasan
    await meeting.submit_meeting_minute(minute_id, current_user=notulis, db=db)
    res = await meeting.approve_meeting_minute(minute_id, current_user=ketua, db=db)
    assert res["status"] == "approved"
    print("✅ Successfully approved minute by Ketua Yayasan")

    # 8. Test Action Items Tracking
    action_items = await meeting.list_action_items(current_user=ketua, db=db)
    target_ai = [ai for ai in action_items if ai["meeting_id"] == minute_id][0]
    ai_id = target_ai["id"]
    print(f"✅ Found action item #{ai_id}: '{target_ai['task_description']}'")

    # Update Action Item status to 'done' by PIC
    res = await meeting.update_action_item_status(ai_id, data={"status": "done", "notes": "Selesai ditandatangani"}, current_user=kepala, db=db)
    assert res["status"] == "done"
    print("✅ Action item status updated to 'done' by PIC")

    # 9. Test PDF Export
    pdf_res = await meeting.export_meeting_minute_pdf(minute_id, current_user=ketua, db=db)
    assert pdf_res.media_type == "application/pdf"
    assert pdf_res.body.startswith(b"%PDF-")
    print(f"✅ Official PDF export successful! (Size: {len(pdf_res.body)} bytes)")

    print("\n🎉 ALL SPRINT 3 TESTS PASSED (100%)! 🎉\n")
    db.close()

if __name__ == "__main__":
    asyncio.run(run_tests())
