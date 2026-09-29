import os
import sys
import asyncio
from datetime import datetime

# Set path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models
from routers import internal

async def run_tests():
    db = SessionLocal()
    print("--- 🧪 Running Duplicate Detection & Resolution Automated Tests ---")
    
    mock_user = db.query(models.User).filter(models.User.is_active == True).first()
    assert mock_user is not None, "Need at least 1 user in DB"

    # Clean up test documents
    db.query(models.DocumentDuplicateResolution).delete()
    db.query(models.Document).filter(models.Document.title.like("TEST_DUP_%")).delete()
    db.commit()

    # 1. Create two very similar documents
    doc1 = models.Document(
        title="TEST_DUP_SOP Penerimaan Tamu Sekolah Asy Syuuraa",
        document_number="99/SK/Y-AS/IX/2026",
        category="sop",
        file_url="https://example.com/sop1.pdf",
        file_name="sop_tamu_2026.pdf",
        uploaded_by=mock_user.id,
        is_active=True
    )
    doc2 = models.Document(
        title="TEST_DUP_SOP Penerimaan Tamu Sekolah di Lingkungan Asy Syuuraa",
        document_number="99/SK/Y-AS/IX/2026", # Same number!
        category="sop",
        file_url="https://example.com/sop2.pdf",
        file_name="sop_tamu_2026.pdf",
        uploaded_by=mock_user.id,
        is_active=True
    )
    db.add_all([doc1, doc2])
    db.commit()
    db.refresh(doc1)
    db.refresh(doc2)
    print(f"✅ Created 2 test documents: #{doc1.id} & #{doc2.id}")

    # 2. Test get_duplicate_candidates
    candidates_res = await internal.get_duplicate_candidates(current_user=mock_user, db=db)
    print(f"✅ Found {candidates_res['count']} duplicate pairs")
    assert candidates_res["count"] >= 1, "Should find at least 1 duplicate candidate"

    found_pair = next((p for p in candidates_res["pairs"] if p["doc_a_id"] in (doc1.id, doc2.id) and p["doc_b_id"] in (doc1.id, doc2.id)), None)
    assert found_pair is not None, "Test pair should be identified as duplicate"
    assert found_pair["score"] >= 80, f"Expected score >= 80, got {found_pair['score']}"
    print(f"✅ Detected pair score: {found_pair['score']}%, reason: '{found_pair['reason']}'")

    # 3. Test real-time check: check_single_duplicate
    check_res = await internal.check_single_duplicate(
        title="TEST_DUP_SOP Penerimaan Tamu",
        document_number="99/SK/Y-AS/IX/2026",
        category="sop",
        exclude_id=None,
        current_user=mock_user,
        db=db
    )
    assert check_res["has_match"] is True
    print(f"✅ Real-time check passed: matched doc '{check_res['match']['title']}' with score {check_res['match']['score']}%")

    # 4. Test Resolve: mark_distinct
    res_distinct = await internal.resolve_duplicate_pair(
        data={
            "doc_a_id": doc1.id,
            "doc_b_id": doc2.id,
            "action": "mark_distinct"
        },
        current_user=mock_user,
        db=db
    )
    print(f"✅ Resolved as 'mark_distinct': {res_distinct['message']}")

    # Verify candidate is now ignored in duplicates list
    res_after = await internal.get_duplicate_candidates(current_user=mock_user, db=db)
    pairs_after = res_after["pairs"]
    assert not any(p["doc_a_id"] in (doc1.id, doc2.id) and p["doc_b_id"] in (doc1.id, doc2.id) for p in pairs_after), "Pair should be omitted after distinct resolution"
    print("✅ Verified: Resolved pair no longer appears in duplicate candidates list")

    # 5. Test Resolve: merge_as_revision
    doc3 = models.Document(
        title="TEST_DUP_SK Beban Mengajar 2026",
        document_number="55/SK/2026",
        category="sk_yayasan",
        file_url="https://example.com/sk1.pdf",
        file_name="sk1.pdf",
        uploaded_by=mock_user.id,
        is_active=True
    )
    doc4 = models.Document(
        title="TEST_DUP_SK Beban Mengajar Guru 2026",
        document_number="55/SK/2026",
        category="sk_yayasan",
        file_url="https://example.com/sk2.pdf",
        file_name="sk2.pdf",
        uploaded_by=mock_user.id,
        is_active=True
    )
    db.add_all([doc3, doc4])
    db.commit()
    db.refresh(doc3)
    db.refresh(doc4)

    merge_res = await internal.resolve_duplicate_pair(
        data={
            "doc_a_id": doc3.id,
            "doc_b_id": doc4.id,
            "action": "merge_as_revision",
            "parent_doc_id": doc3.id,
            "child_doc_id": doc4.id
        },
        current_user=mock_user,
        db=db
    )
    db.refresh(doc4)
    assert doc4.replaces_id == doc3.id, "Child doc should now link to parent doc"
    print("✅ Verified: merge_as_revision successfully set replaces_id relationship")

    # Clean up test records
    db.query(models.DocumentDuplicateResolution).delete()
    db.query(models.Document).filter(models.Document.title.like("TEST_DUP_%")).delete()
    db.commit()
    db.close()

    print("\n🎉 ALL DUPLICATE DETECTION & RESOLUTION TESTS PASSED (100%)! 🎉\n")

if __name__ == "__main__":
    asyncio.run(run_tests())
