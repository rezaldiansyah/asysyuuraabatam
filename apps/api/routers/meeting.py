from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, desc
from database import get_db
import models
from datetime import datetime, date
from typing import Optional, List
import json
import io

from deps import get_current_user

router = APIRouter(prefix="/meeting", tags=["Meeting Minutes & Action Items"])

# Role categorization
YAYASAN_LEADERSHIP_ROLES = ["superadmin", "ketua_yayasan", "wakil_ketua_yayasan", "kabid_umum"]
UNIT_LEADERSHIP_ROLES = ["kepala_unit", "wakil_kepala"]

def _is_yayasan_leadership(user: models.User) -> bool:
    role_code = user.role.code if user.role else ""
    return role_code in YAYASAN_LEADERSHIP_ROLES

def _is_unit_leader_of(user: models.User, unit_id: Optional[int]) -> bool:
    if _is_yayasan_leadership(user):
        return True
    role_code = user.role.code if user.role else ""
    if role_code not in UNIT_LEADERSHIP_ROLES:
        return False
    if not unit_id:
        return False
    # Check unit assignments
    if hasattr(user, 'unit_assignments') and user.unit_assignments:
        return any(ua.unit_id == unit_id for ua in user.unit_assignments)
    return False

def _parse_date(val):
    if not val:
        return None
    if isinstance(val, (datetime, date)):
        return val
    try:
        return datetime.fromisoformat(str(val).replace("Z", "+00:00"))
    except Exception:
        try:
            return datetime.strptime(str(val)[:10], "%Y-%m-%d")
        except Exception:
            return None

def _auto_nomor_notulen(db: Session, scope: str, unit_id: Optional[int], meeting_date: datetime) -> str:
    year = meeting_date.year if meeting_date else datetime.utcnow().year
    month = f"{meeting_date.month:02d}" if meeting_date else f"{datetime.utcnow().month:02d}"
    
    code = "YYS"
    if scope == "unit" and unit_id:
        unit = db.query(models.Unit).filter(models.Unit.id == unit_id).first()
        if unit and unit.code:
            code = unit.code.upper()
            
    count = db.query(models.MeetingMinutes).filter(
        models.MeetingMinutes.created_at >= datetime(year, 1, 1),
        models.MeetingMinutes.created_at < datetime(year + 1, 1, 1)
    ).count() + 1
    
    return f"NOT/{code}/{year}/{month}/{count:03d}"

# ============================================================
# MEETING MINUTES ENDPOINTS
# ============================================================

@router.get("/minutes")
async def list_meeting_minutes(
    scope: Optional[str] = None,
    unit_id: Optional[int] = None,
    meeting_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List meeting minutes with filters and multi-level RBAC."""
    query = db.query(models.MeetingMinutes).filter(models.MeetingMinutes.is_active == True)
    
    if scope:
        query = query.filter(models.MeetingMinutes.scope == scope)
    if unit_id:
        query = query.filter(models.MeetingMinutes.unit_id == unit_id)
    if meeting_type:
        query = query.filter(models.MeetingMinutes.meeting_type == meeting_type)
    if status:
        query = query.filter(models.MeetingMinutes.status == status)
    if search:
        query = query.filter(
            or_(
                models.MeetingMinutes.title.ilike(f"%{search}%"),
                models.MeetingMinutes.nomor_notulen.ilike(f"%{search}%"),
                models.MeetingMinutes.location.ilike(f"%{search}%"),
            )
        )
    if start_date:
        s_date = _parse_date(start_date)
        if s_date:
            query = query.filter(models.MeetingMinutes.meeting_date >= s_date)
    if end_date:
        e_date = _parse_date(end_date)
        if e_date:
            query = query.filter(models.MeetingMinutes.meeting_date <= e_date)
            
    # RBAC filtering
    is_yayasan_leader = _is_yayasan_leadership(current_user)
    user_unit_ids = set()
    if hasattr(current_user, 'unit_assignments') and current_user.unit_assignments:
        user_unit_ids = {ua.unit_id for ua in current_user.unit_assignments if ua.unit_id}
        
    all_minutes = query.options(
        joinedload(models.MeetingMinutes.notulis),
        joinedload(models.MeetingMinutes.approver),
        joinedload(models.MeetingMinutes.unit),
        joinedload(models.MeetingMinutes.action_items)
    ).order_by(desc(models.MeetingMinutes.meeting_date), desc(models.MeetingMinutes.created_at)).all()
    
    result = []
    for m in all_minutes:
        # Access control
        if not is_yayasan_leader:
            # If not yayasan leadership:
            # 1. You can always see minutes you created
            if m.notulis_id == current_user.id:
                pass
            # 2. You can see minutes where you are listed in attendees
            elif m.attendees:
                try:
                    att_list = json.loads(m.attendees) if isinstance(m.attendees, str) else m.attendees
                    if current_user.id in att_list:
                        pass
                    elif m.status == "approved" and (m.scope == "yayasan_global" or (m.unit_id and m.unit_id in user_unit_ids)):
                        pass
                    elif m.unit_id and m.unit_id in user_unit_ids and _is_unit_leader_of(current_user, m.unit_id):
                        pass
                    else:
                        continue
                except Exception:
                    continue
            # 3. If published/approved and relevant to user's unit or global
            elif m.status == "approved" and (m.scope == "yayasan_global" or (m.unit_id and m.unit_id in user_unit_ids)):
                pass
            # 4. If unit leader for this unit
            elif m.unit_id and m.unit_id in user_unit_ids and _is_unit_leader_of(current_user, m.unit_id):
                pass
            else:
                continue

        action_items = m.action_items or []
        ai_total = len(action_items)
        ai_done = sum(1 for ai in action_items if ai.status == "done")
        ai_pending = sum(1 for ai in action_items if ai.status in ["pending", "in_progress"])

        result.append({
            "id": m.id,
            "nomor_notulen": m.nomor_notulen,
            "title": m.title,
            "meeting_date": m.meeting_date.isoformat() if m.meeting_date else None,
            "start_time": m.start_time,
            "end_time": m.end_time,
            "location": m.location,
            "scope": m.scope,
            "unit_id": m.unit_id,
            "unit_name": m.unit.name if m.unit else ("Yayasan" if m.scope == "yayasan_global" else "-"),
            "unit_code": m.unit.code if m.unit else ("YYS" if m.scope == "yayasan_global" else "-"),
            "meeting_type": m.meeting_type,
            "status": m.status,
            "notulis_id": m.notulis_id,
            "notulis_name": m.notulis.full_name if m.notulis else "-",
            "approver_id": m.approver_id,
            "approver_name": m.approver.full_name if m.approver else None,
            "approved_at": m.approved_at.isoformat() if m.approved_at else None,
            "action_items_count": {
                "total": ai_total,
                "done": ai_done,
                "pending": ai_pending
            },
            "created_at": m.created_at.isoformat() if m.created_at else None,
        })
        
    return result[offset:offset + limit]


@router.post("/minutes")
async def create_meeting_minute(
    data: dict,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new meeting minute in draft status."""
    title = data.get("title")
    if not title:
        raise HTTPException(status_code=400, detail="Judul rapat wajib diisi")
        
    m_date = _parse_date(data.get("meeting_date")) or datetime.utcnow()
    scope = data.get("scope", "unit")
    unit_id = data.get("unit_id")
    
    # Auto-generate nomor notulen if empty
    nomor = data.get("nomor_notulen") or _auto_nomor_notulen(db, scope, unit_id, m_date)
    
    agenda = data.get("agenda")
    decisions = data.get("decisions")
    attendees = data.get("attendees")
    absent_members = data.get("absent_members")
    attachment_urls = data.get("attachment_urls")
    
    minute = models.MeetingMinutes(
        nomor_notulen=nomor,
        title=title,
        meeting_date=m_date,
        start_time=data.get("start_time"),
        end_time=data.get("end_time"),
        location=data.get("location"),
        scope=scope,
        unit_id=unit_id,
        meeting_type=data.get("meeting_type", "rapat_unit"),
        agenda=json.dumps(agenda) if isinstance(agenda, list) else agenda,
        content=data.get("content", ""),
        decisions=json.dumps(decisions) if isinstance(decisions, list) else decisions,
        attendees=json.dumps(attendees) if isinstance(attendees, list) else attendees,
        absent_members=json.dumps(absent_members) if isinstance(absent_members, list) else absent_members,
        attachment_urls=json.dumps(attachment_urls) if isinstance(attachment_urls, list) else attachment_urls,
        notulis_id=current_user.id,
        status="draft",
        is_active=True,
    )
    db.add(minute)
    db.commit()
    db.refresh(minute)
    
    # Optional action items
    initial_actions = data.get("action_items", [])
    if isinstance(initial_actions, list) and initial_actions:
        for item in initial_actions:
            if item.get("task_description"):
                ai = models.MeetingActionItem(
                    meeting_id=minute.id,
                    task_description=item.get("task_description"),
                    pic_user_id=item.get("pic_user_id"),
                    deadline=_parse_date(item.get("deadline")),
                    status="pending",
                    notes=item.get("notes")
                )
                db.add(ai)
        db.commit()
        db.refresh(minute)
        
    return {"id": minute.id, "nomor_notulen": minute.nomor_notulen, "message": "Notulen berhasil disimpan sebagai draf"}


@router.get("/minutes/{minute_id}")
async def get_meeting_minute_detail(
    minute_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get full meeting minute details with attendees and action items."""
    m = db.query(models.MeetingMinutes).options(
        joinedload(models.MeetingMinutes.notulis),
        joinedload(models.MeetingMinutes.approver),
        joinedload(models.MeetingMinutes.unit),
        joinedload(models.MeetingMinutes.action_items).joinedload(models.MeetingActionItem.pic)
    ).filter(models.MeetingMinutes.id == minute_id, models.MeetingMinutes.is_active == True).first()
    
    if not m:
        raise HTTPException(status_code=404, detail="Notulen rapat tidak ditemukan")
        
    # Parse JSON fields safely
    def _safe_json(val):
        if not val:
            return []
        if isinstance(val, list):
            return val
        try:
            return json.loads(val)
        except Exception:
            return []

    attendee_ids = _safe_json(m.attendees)
    absent_ids = _safe_json(m.absent_members)
    
    attendee_users = []
    if attendee_ids:
        users = db.query(models.User).options(joinedload(models.User.role)).filter(models.User.id.in_(attendee_ids)).all()
        attendee_users = [{
            "id": u.id,
            "full_name": u.full_name,
            "nik": u.nik,
            "role_name": u.role.name if u.role else "-"
        } for u in users]
        
    absent_users = []
    if absent_ids:
        users = db.query(models.User).options(joinedload(models.User.role)).filter(models.User.id.in_(absent_ids)).all()
        absent_users = [{
            "id": u.id,
            "full_name": u.full_name,
            "nik": u.nik,
            "role_name": u.role.name if u.role else "-"
        } for u in users]
        
    action_items = []
    for ai in m.action_items:
        action_items.append({
            "id": ai.id,
            "task_description": ai.task_description,
            "pic_user_id": ai.pic_user_id,
            "pic_name": ai.pic.full_name if ai.pic else "-",
            "deadline": ai.deadline.isoformat() if ai.deadline else None,
            "status": ai.status,
            "completion_date": ai.completion_date.isoformat() if ai.completion_date else None,
            "notes": ai.notes,
        })
        
    # Check if current user is allowed to approve
    can_approve = False
    if m.status == "submitted":
        if m.scope == "yayasan_global":
            can_approve = _is_yayasan_leadership(current_user)
        else:
            can_approve = _is_unit_leader_of(current_user, m.unit_id) or _is_yayasan_leadership(current_user)

    return {
        "id": m.id,
        "nomor_notulen": m.nomor_notulen,
        "title": m.title,
        "meeting_date": m.meeting_date.isoformat() if m.meeting_date else None,
        "start_time": m.start_time,
        "end_time": m.end_time,
        "location": m.location,
        "scope": m.scope,
        "unit_id": m.unit_id,
        "unit_name": m.unit.name if m.unit else ("Yayasan" if m.scope == "yayasan_global" else "-"),
        "unit_code": m.unit.code if m.unit else ("YYS" if m.scope == "yayasan_global" else "-"),
        "meeting_type": m.meeting_type,
        "agenda": _safe_json(m.agenda),
        "content": m.content or "",
        "decisions": _safe_json(m.decisions),
        "attendees": attendee_users,
        "attendee_ids": attendee_ids,
        "absent_members": absent_users,
        "absent_member_ids": absent_ids,
        "attachment_urls": _safe_json(m.attachment_urls),
        "notulis_id": m.notulis_id,
        "notulis_name": m.notulis.full_name if m.notulis else "-",
        "status": m.status,
        "approver_id": m.approver_id,
        "approver_name": m.approver.full_name if m.approver else None,
        "approved_at": m.approved_at.isoformat() if m.approved_at else None,
        "approval_notes": m.approval_notes,
        "can_approve": can_approve,
        "action_items": action_items,
        "created_at": m.created_at.isoformat() if m.created_at else None,
        "updated_at": m.updated_at.isoformat() if m.updated_at else None,
    }


@router.put("/minutes/{minute_id}")
async def update_meeting_minute(
    minute_id: int,
    data: dict,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update meeting minute (only when draft or rejected)."""
    m = db.query(models.MeetingMinutes).filter(models.MeetingMinutes.id == minute_id, models.MeetingMinutes.is_active == True).first()
    if not m:
        raise HTTPException(status_code=404, detail="Notulen tidak ditemukan")
        
    if m.status not in ["draft", "rejected"]:
        raise HTTPException(status_code=400, detail="Notulen yang sudah diajukan atau disahkan tidak dapat diedit langsung.")
        
    # Check permission
    is_owner = (m.notulis_id == current_user.id)
    is_admin = _is_yayasan_leadership(current_user)
    if not (is_owner or is_admin):
        raise HTTPException(status_code=403, detail="Hanya notulis atau pimpinan yang dapat mengedit draf notulen.")
        
    for field in ["title", "nomor_notulen", "start_time", "end_time", "location", "scope", "unit_id", "meeting_type", "content"]:
        if field in data:
            setattr(m, field, data[field])
            
    if "meeting_date" in data:
        m.meeting_date = _parse_date(data["meeting_date"]) or m.meeting_date
        
    for json_field in ["agenda", "decisions", "attendees", "absent_members", "attachment_urls"]:
        if json_field in data:
            val = data[json_field]
            setattr(m, json_field, json.dumps(val) if isinstance(val, list) else val)
            
    # Sync Action Items
    if "action_items" in data and isinstance(data["action_items"], list):
        # Keep track of existing
        existing_items = {ai.id: ai for ai in m.action_items}
        sent_ids = set()
        
        for item in data["action_items"]:
            ai_id = item.get("id")
            if ai_id and ai_id in existing_items:
                # Update existing
                ai = existing_items[ai_id]
                ai.task_description = item.get("task_description", ai.task_description)
                ai.pic_user_id = item.get("pic_user_id", ai.pic_user_id)
                ai.deadline = _parse_date(item.get("deadline")) or ai.deadline
                ai.status = item.get("status", ai.status)
                ai.notes = item.get("notes", ai.notes)
                sent_ids.add(ai_id)
            else:
                # Add new
                if item.get("task_description"):
                    new_ai = models.MeetingActionItem(
                        meeting_id=m.id,
                        task_description=item.get("task_description"),
                        pic_user_id=item.get("pic_user_id"),
                        deadline=_parse_date(item.get("deadline")),
                        status=item.get("status", "pending"),
                        notes=item.get("notes")
                    )
                    db.add(new_ai)
                    
        # Remove items that were deleted in the UI
        for ai_id, ai in existing_items.items():
            if ai_id not in sent_ids:
                db.delete(ai)
                
    m.updated_at = datetime.utcnow()
    db.commit()
    return {"id": m.id, "message": "Notulen berhasil diperbarui"}


@router.post("/minutes/{minute_id}/submit")
async def submit_meeting_minute(
    minute_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit meeting minute for approval."""
    m = db.query(models.MeetingMinutes).filter(models.MeetingMinutes.id == minute_id, models.MeetingMinutes.is_active == True).first()
    if not m:
        raise HTTPException(status_code=404, detail="Notulen tidak ditemukan")
        
    if m.status not in ["draft", "rejected"]:
        raise HTTPException(status_code=400, detail="Hanya draf notulen atau yang perlu revisi yang dapat diajukan.")
        
    m.status = "submitted"
    m.updated_at = datetime.utcnow()
    db.commit()
    return {"id": m.id, "status": m.status, "message": "Notulen berhasil diajukan untuk disahkan oleh pimpinan"}


@router.post("/minutes/{minute_id}/approve")
async def approve_meeting_minute(
    minute_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve meeting minute:
    - If scope == 'yayasan_global': Only Ketua / Wakil Ketua Yayasan / Superadmin.
    - If scope == 'unit': Kepala Unit / Wakil Kepala Unit (or Yayasan leadership).
    """
    m = db.query(models.MeetingMinutes).filter(models.MeetingMinutes.id == minute_id, models.MeetingMinutes.is_active == True).first()
    if not m:
        raise HTTPException(status_code=404, detail="Notulen tidak ditemukan")
        
    if m.status != "submitted":
        raise HTTPException(status_code=400, detail="Hanya notulen berstatus 'Menunggu Persetujuan' yang dapat disahkan.")
        
    # Check Authority
    if m.scope == "yayasan_global":
        if not _is_yayasan_leadership(current_user):
            raise HTTPException(
                status_code=403, 
                detail="Notulen tingkat Yayasan / Seluruh Unit hanya dapat disahkan oleh Ketua atau Wakil Ketua Yayasan."
            )
    else:
        if not (_is_unit_leader_of(current_user, m.unit_id) or _is_yayasan_leadership(current_user)):
            raise HTTPException(
                status_code=403, 
                detail="Notulen unit hanya dapat disahkan oleh Kepala Unit atau Pimpinan Yayasan."
            )
            
    m.status = "approved"
    m.approver_id = current_user.id
    m.approved_at = datetime.utcnow()
    m.approval_notes = None
    m.updated_at = datetime.utcnow()
    db.commit()
    return {"id": m.id, "status": m.status, "approver_name": current_user.full_name, "message": "Notulen rapat resmi disahkan dan diterbitkan."}


@router.post("/minutes/{minute_id}/reject")
async def reject_meeting_minute(
    minute_id: int,
    payload: dict,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Return meeting minute to notulis with revision notes."""
    m = db.query(models.MeetingMinutes).filter(models.MeetingMinutes.id == minute_id, models.MeetingMinutes.is_active == True).first()
    if not m:
        raise HTTPException(status_code=404, detail="Notulen tidak ditemukan")
        
    if m.status != "submitted":
        raise HTTPException(status_code=400, detail="Hanya notulen berstatus 'Menunggu Persetujuan' yang dapat dikembalikan.")
        
    # Check Authority
    if m.scope == "yayasan_global":
        if not _is_yayasan_leadership(current_user):
            raise HTTPException(
                status_code=403, 
                detail="Notulen tingkat Yayasan hanya dapat ditinjau oleh Ketua atau Wakil Ketua Yayasan."
            )
    else:
        if not (_is_unit_leader_of(current_user, m.unit_id) or _is_yayasan_leadership(current_user)):
            raise HTTPException(
                status_code=403, 
                detail="Notulen unit hanya dapat ditinjau oleh Kepala Unit atau Pimpinan Yayasan."
            )
            
    notes = payload.get("notes", "").strip()
    if not notes:
        raise HTTPException(status_code=400, detail="Catatan perbaikan / revisi wajib diisi.")
        
    m.status = "rejected"
    m.approver_id = current_user.id
    m.approval_notes = notes
    m.updated_at = datetime.utcnow()
    db.commit()
    return {"id": m.id, "status": m.status, "message": "Notulen dikembalikan ke notulis untuk revisi."}


@router.delete("/minutes/{minute_id}")
async def delete_meeting_minute(
    minute_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete a meeting minute."""
    m = db.query(models.MeetingMinutes).filter(models.MeetingMinutes.id == minute_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Notulen tidak ditemukan")
        
    is_owner = (m.notulis_id == current_user.id and m.status in ["draft", "rejected"])
    is_admin = _is_yayasan_leadership(current_user)
    if not (is_owner or is_admin):
        raise HTTPException(status_code=403, detail="Tidak memiliki hak untuk menghapus notulen ini.")
        
    m.is_active = False
    m.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Notulen berhasil dihapus"}


# ============================================================
# ACTION ITEMS ENDPOINTS
# ============================================================

@router.get("/action-items")
async def list_action_items(
    pic_user_id: Optional[int] = None,
    status: Optional[str] = None,
    meeting_id: Optional[int] = None,
    overdue: bool = False,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all action items with filtering."""
    query = db.query(models.MeetingActionItem).join(models.MeetingMinutes).filter(
        models.MeetingMinutes.is_active == True
    )
    
    if pic_user_id:
        query = query.filter(models.MeetingActionItem.pic_user_id == pic_user_id)
    if status:
        query = query.filter(models.MeetingActionItem.status == status)
    if meeting_id:
        query = query.filter(models.MeetingActionItem.meeting_id == meeting_id)
    if overdue:
        query = query.filter(
            models.MeetingActionItem.status != "done",
            models.MeetingActionItem.deadline < datetime.utcnow()
        )
        
    items = query.options(
        joinedload(models.MeetingActionItem.pic),
        joinedload(models.MeetingActionItem.meeting)
    ).order_by(models.MeetingActionItem.deadline.asc()).all()
    
    return [
        {
            "id": ai.id,
            "meeting_id": ai.meeting_id,
            "meeting_title": ai.meeting.title if ai.meeting else "-",
            "nomor_notulen": ai.meeting.nomor_notulen if ai.meeting else "-",
            "task_description": ai.task_description,
            "pic_user_id": ai.pic_user_id,
            "pic_name": ai.pic.full_name if ai.pic else "-",
            "deadline": ai.deadline.isoformat() if ai.deadline else None,
            "status": ai.status,
            "is_overdue": bool(ai.deadline and ai.deadline < datetime.utcnow() and ai.status != "done"),
            "completion_date": ai.completion_date.isoformat() if ai.completion_date else None,
            "notes": ai.notes,
        }
        for ai in items
    ]


@router.get("/action-items/my")
async def list_my_action_items(
    status: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List action items assigned to currently authenticated user."""
    return await list_action_items(pic_user_id=current_user.id, status=status, current_user=current_user, db=db)


@router.put("/action-items/{item_id}")
async def update_action_item_status(
    item_id: int,
    data: dict,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update progress/status of an action item."""
    ai = db.query(models.MeetingActionItem).filter(models.MeetingActionItem.id == item_id).first()
    if not ai:
        raise HTTPException(status_code=404, detail="Action item tidak ditemukan")
        
    # User can update if they are PIC, notulis of the meeting, or leadership
    is_pic = (ai.pic_user_id == current_user.id)
    is_notulis = (ai.meeting and ai.meeting.notulis_id == current_user.id)
    is_leader = _is_yayasan_leadership(current_user)
    
    if not (is_pic or is_notulis or is_leader):
        raise HTTPException(status_code=403, detail="Hanya PIC atau pimpinan yang dapat memperbarui tugas ini.")
        
    new_status = data.get("status")
    if new_status and new_status in ["pending", "in_progress", "done"]:
        ai.status = new_status
        if new_status == "done" and not ai.completion_date:
            ai.completion_date = datetime.utcnow()
        elif new_status != "done":
            ai.completion_date = None
            
    if "notes" in data:
        ai.notes = data["notes"]
        
    ai.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ai)
    return {"id": ai.id, "status": ai.status, "message": "Status tugas berhasil diperbarui"}


# ============================================================
# PDF EXPORT (ReportLab)
# ============================================================

@router.get("/minutes/{minute_id}/export-pdf")
async def export_meeting_minute_pdf(
    minute_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate official PDF document for meeting minutes."""
    m = db.query(models.MeetingMinutes).options(
        joinedload(models.MeetingMinutes.notulis),
        joinedload(models.MeetingMinutes.approver),
        joinedload(models.MeetingMinutes.unit),
        joinedload(models.MeetingMinutes.action_items).joinedload(models.MeetingActionItem.pic)
    ).filter(models.MeetingMinutes.id == minute_id, models.MeetingMinutes.is_active == True).first()
    
    if not m:
        raise HTTPException(status_code=404, detail="Notulen tidak ditemukan")
        
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    header_style = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        alignment=1, # Center
        textColor=colors.HexColor('#0F172A')
    )
    sub_header_style = ParagraphStyle(
        'HeaderSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        alignment=1, # Center
        textColor=colors.HexColor('#475569')
    )
    doc_title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        alignment=1,
        textColor=colors.HexColor('#059669')
    )
    section_h2 = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#1E293B')
    )
    body_style = ParagraphStyle(
        'BodyTxt',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )
    meta_key = ParagraphStyle(
        'MetaKey',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#475569')
    )
    meta_val = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#1E293B')
    )

    elements = []
    
    # 1. Header / Kop Surat
    instansi = "YAYASAN ASY-SYUURAA BATAM"
    sub_instansi = "SEKOLAH ISLAM TERPADU ASY-SYUURAA"
    if m.scope == "unit" and m.unit:
        sub_instansi = f"UNIT {m.unit.name.upper()}"
        
    elements.append(Paragraph(instansi, header_style))
    elements.append(Paragraph(sub_instansi, header_style))
    elements.append(Paragraph("Komplek Asy-Syuuraa, Batam, Kepulauan Riau — https://asy-syuuraabatam.or.id", sub_header_style))
    elements.append(Spacer(1, 6))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#059669'), spaceAfter=12))
    
    # 2. Judul Dokumen & Nomor Notulen
    elements.append(Paragraph("RISALAH & NOTULEN RAPAT RESMI", doc_title_style))
    elements.append(Paragraph(f"Nomor: {m.nomor_notulen or '-'}", sub_header_style))
    elements.append(Spacer(1, 10))
    
    # 3. Identitas Pertemuan (Table)
    m_date_str = m.meeting_date.strftime("%d %B %Y") if m.meeting_date else "-"
    time_str = f"{m.start_time or '-'} s.d {m.end_time or '-'}"
    unit_str = m.unit.name if m.unit else ("Seluruh Unit / Yayasan" if m.scope == "yayasan_global" else "-")
    
    meta_data = [
        [Paragraph("Topik / Judul", meta_key), Paragraph(f": {m.title}", meta_val),
         Paragraph("Hari / Tanggal", meta_key), Paragraph(f": {m_date_str}", meta_val)],
        [Paragraph("Jenis Rapat", meta_key), Paragraph(f": {m.meeting_type.replace('_', ' ').title()}", meta_val),
         Paragraph("Waktu Pelaksanaan", meta_key), Paragraph(f": {time_str}", meta_val)],
        [Paragraph("Cakupan / Unit", meta_key), Paragraph(f": {unit_str}", meta_val),
         Paragraph("Tempat Pertemuan", meta_key), Paragraph(f": {m.location or '-'}", meta_val)],
    ]
    meta_table = Table(meta_data, colWidths=[80, 180, 85, 170])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 12))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=10))

    # Helper for JSON list
    def _parse_list(val):
        if not val:
            return []
        if isinstance(val, list):
            return val
        try:
            return json.loads(val)
        except Exception:
            return []

    # 4. Agenda Rapat
    agenda_list = _parse_list(m.agenda)
    if agenda_list:
        elements.append(Paragraph("I. AGENDA PEMBAHASAN", section_h2))
        elements.append(Spacer(1, 4))
        for idx, ag in enumerate(agenda_list, 1):
            elements.append(Paragraph(f"{idx}. {ag}", body_style))
        elements.append(Spacer(1, 10))

    # 5. Isi Notulensi / Pembahasan
    elements.append(Paragraph("II. JALANNYA RAPAT / PEMBAHASAN", section_h2))
    elements.append(Spacer(1, 4))
    import re
    clean_content = re.sub('<[^<]+?>', '', m.content or "Tidak ada catatan pembahasan.")
    elements.append(Paragraph(clean_content.replace('\n', '<br/>'), body_style))
    elements.append(Spacer(1, 10))

    # 6. Keputusan / Kesimpulan Rapat
    decisions_list = _parse_list(m.decisions)
    if decisions_list:
        elements.append(Paragraph("III. KEPUTUSAN & KESIMPULAN", section_h2))
        elements.append(Spacer(1, 4))
        for idx, dec in enumerate(decisions_list, 1):
            elements.append(Paragraph(f"{idx}. {dec}", body_style))
        elements.append(Spacer(1, 10))

    # 7. Action Items / Tindak Lanjut
    if m.action_items:
        elements.append(Paragraph("IV. TINDAK LANJUT / ACTION ITEMS", section_h2))
        elements.append(Spacer(1, 4))
        ai_table_data = [[
            Paragraph("No", meta_key),
            Paragraph("Uraian Tugas", meta_key),
            Paragraph("Penanggung Jawab (PIC)", meta_key),
            Paragraph("Batas Waktu", meta_key),
            Paragraph("Status", meta_key)
        ]]
        for idx, ai in enumerate(m.action_items, 1):
            d_line = ai.deadline.strftime("%d/%m/%Y") if ai.deadline else "-"
            st_map = {"pending": "Menunggu", "in_progress": "Berjalan", "done": "Selesai"}
            ai_table_data.append([
                Paragraph(str(idx), body_style),
                Paragraph(ai.task_description, body_style),
                Paragraph(ai.pic.full_name if ai.pic else "-", body_style),
                Paragraph(d_line, body_style),
                Paragraph(st_map.get(ai.status, ai.status), body_style)
            ])
        ai_table = Table(ai_table_data, colWidths=[25, 210, 130, 75, 75])
        ai_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(ai_table)
        elements.append(Spacer(1, 15))

    # 8. Tanda Tangan & Pengesahan Digital
    elements.append(Spacer(1, 10))
    appr_title = "Ketua Yayasan" if m.scope == "yayasan_global" else "Kepala Unit"
    appr_name = m.approver.full_name if m.approver else "............................"
    appr_date = m.approved_at.strftime("%d %B %Y") if m.approved_at else ""
    notulis_name = m.notulis.full_name if m.notulis else "-"
    
    sig_data = [
        [Paragraph("Disahkan oleh,", body_style), Paragraph("Batam, " + (m.meeting_date.strftime("%d %B %Y") if m.meeting_date else "-"), body_style)],
        [Paragraph(f"<b>{appr_title}</b>", body_style), Paragraph("<b>Notulis Rapat,</b>", body_style)],
        [Spacer(1, 35), Spacer(1, 35)],
        [Paragraph(f"<b><u>{appr_name}</u></b>", body_style), Paragraph(f"<b><u>{notulis_name}</u></b>", body_style)],
        [Paragraph(f"<font color='#059669'>Tervalidasi Sistem {appr_date}</font>" if m.approved_at else "", sub_header_style),
         Paragraph(f"NIK: {m.notulis.nik or '-'}" if m.notulis else "", body_style)]
    ]
    sig_table = Table(sig_data, colWidths=[250, 265])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ]))
    elements.append(sig_table)
    
    doc.build(elements)
    buffer.seek(0)
    
    filename = f"Notulen_{m.nomor_notulen.replace('/', '_') if m.nomor_notulen else m.id}.pdf"
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'}
    )
