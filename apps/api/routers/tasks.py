from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, desc
from datetime import datetime, timezone, timedelta
from typing import Optional, List
import logging

from database import get_db
import models
import schemas
from deps import get_current_user
from email_service import send_task_notification_email, is_email_configured

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["Task Management (Tugas Saya)"])

LEADERSHIP_ROLES = [
    "superadmin", "ketua_yayasan", "wakil_ketua_yayasan", "kabid_umum",
    "kabid_keuangan", "tu_yayasan", "kepala_unit", "wakil_kepala", "tu_unit"
]

def _is_leadership(user: models.User) -> bool:
    role_code = user.role.code if user.role else ""
    return role_code in LEADERSHIP_ROLES

def _format_deadline(dt: Optional[datetime]) -> Optional[str]:
    if not dt:
        return None
    try:
        return dt.strftime("%d %b %Y, %H:%M WIB")
    except Exception:
        return str(dt)


@router.get("/stats/summary")
async def get_task_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get count of tasks grouped by status and stats for dashboard badges."""
    query = db.query(models.Task).filter(models.Task.is_active == True)

    is_leader = _is_leadership(current_user)
    if not is_leader:
        # Non-leadership only sees their relevant tasks
        approver_task_ids = db.query(models.TaskApproverLink.task_id).filter(
            models.TaskApproverLink.user_id == current_user.id
        ).subquery()

        query = query.filter(
            or_(
                models.Task.assignee_id == current_user.id,
                models.Task.creator_id == current_user.id,
                models.Task.id.in_(approver_task_ids)
            )
        )

    all_tasks = query.all()

    now = datetime.utcnow()
    counts = {
        "antrian": 0,
        "prioritas": 0,
        "in_progress": 0,
        "awaiting_approval": 0,
        "need_revision": 0,
        "done": 0,
        "total": len(all_tasks),
        "overdue": 0,
        "my_tasks": 0,
        "awaiting_my_approval": 0
    }

    my_approver_task_ids = set(
        t[0] for t in db.query(models.TaskApproverLink.task_id).filter(
            models.TaskApproverLink.user_id == current_user.id,
            models.TaskApproverLink.status == "pending"
        ).all()
    )

    for t in all_tasks:
        if t.status in counts:
            counts[t.status] += 1
        if t.deadline and t.deadline < now and t.status != "done":
            counts["overdue"] += 1
        if t.assignee_id == current_user.id and t.status != "done":
            counts["my_tasks"] += 1
        if t.id in my_approver_task_ids and t.status == "awaiting_approval":
            counts["awaiting_my_approval"] += 1

    return counts


@router.get("", response_model=List[schemas.TaskRead])
async def get_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    scope: Optional[str] = Query("all", description="all, my_assigned, my_created, my_approval"),
    unit_id: Optional[int] = Query(None, description="Filter by unit"),
    priority_level: Optional[int] = Query(None, description="Filter by priority (1-5)"),
    search: Optional[str] = Query(None, description="Search keyword in title or description"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Retrieve list of tasks with filters and role-based scoping."""
    query = db.query(models.Task).filter(models.Task.is_active == True)

    is_leader = _is_leadership(current_user)

    if scope == "my_assigned":
        query = query.filter(models.Task.assignee_id == current_user.id)
    elif scope == "my_created":
        query = query.filter(models.Task.creator_id == current_user.id)
    elif scope == "my_approval":
        approver_task_ids = db.query(models.TaskApproverLink.task_id).filter(
            models.TaskApproverLink.user_id == current_user.id
        ).subquery()
        query = query.filter(models.Task.id.in_(approver_task_ids))
    else:
        # Default "all" scope
        if not is_leader:
            approver_task_ids = db.query(models.TaskApproverLink.task_id).filter(
                models.TaskApproverLink.user_id == current_user.id
            ).subquery()
            query = query.filter(
                or_(
                    models.Task.assignee_id == current_user.id,
                    models.Task.creator_id == current_user.id,
                    models.Task.id.in_(approver_task_ids)
                )
            )

    if status:
        query = query.filter(models.Task.status == status)

    if unit_id:
        query = query.filter(models.Task.unit_id == unit_id)

    if priority_level:
        query = query.filter(models.Task.priority_level == priority_level)

    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                models.Task.title.ilike(s),
                models.Task.description.ilike(s)
            )
        )

    tasks = query.options(
        joinedload(models.Task.creator).joinedload(models.User.role),
        joinedload(models.Task.assignee).joinedload(models.User.role),
        joinedload(models.Task.approvers).joinedload(models.TaskApproverLink.user),
        joinedload(models.Task.histories).joinedload(models.TaskHistory.changed_by)
    ).order_by(
        models.Task.priority_level.asc(),
        models.Task.deadline.asc().nullslast(),
        models.Task.created_at.desc()
    ).all()

    return tasks


@router.post("", response_model=schemas.TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: schemas.TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new task with initial history and optional approver links & email."""
    new_task = models.Task(
        title=payload.title.strip(),
        description=payload.description.strip() if payload.description else None,
        status="antrian",
        priority_level=payload.priority_level if payload.priority_level in [1, 2, 3, 4, 5] else 5,
        creator_id=current_user.id,
        assignee_id=payload.assignee_id,
        unit_id=payload.unit_id,
        deadline=payload.deadline,
        meeting_minute_id=payload.meeting_minute_id,
        meeting_action_item_id=payload.meeting_action_item_id,
        is_active=True
    )
    db.add(new_task)
    db.flush()

    # Add initial history
    history = models.TaskHistory(
        task_id=new_task.id,
        from_status=None,
        to_status="antrian",
        comment="Tugas berhasil dibuat",
        changed_by_id=current_user.id
    )
    db.add(history)

    # Add approvers if provided
    if payload.approver_ids:
        unique_approver_ids = list(dict.fromkeys(payload.approver_ids))
        for uid in unique_approver_ids:
            if uid != current_user.id:  # or allow self if leadership
                link = models.TaskApproverLink(
                    task_id=new_task.id,
                    user_id=uid,
                    status="pending"
                )
                db.add(link)

    db.commit()
    db.refresh(new_task)

    # Send email notification if assignee is assigned
    if new_task.assignee_id and new_task.assignee:
        assignee_user = new_task.assignee
        if assignee_user.email and is_email_configured():
            background_tasks.add_task(
                send_task_notification_email,
                to_email=assignee_user.email,
                to_name=assignee_user.full_name or assignee_user.nik or "Rekan",
                task_title=new_task.title,
                action_type="assignment",
                task_id=new_task.id,
                actor_name=current_user.full_name or current_user.nik or "Pimpinan",
                deadline_str=_format_deadline(new_task.deadline),
                priority_level=new_task.priority_level,
                note=new_task.description
            )

    return new_task


@router.get("/{task_id}", response_model=schemas.TaskRead)
async def get_task_detail(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get single task detail."""
    task = db.query(models.Task).options(
        joinedload(models.Task.creator).joinedload(models.User.role),
        joinedload(models.Task.assignee).joinedload(models.User.role),
        joinedload(models.Task.approvers).joinedload(models.TaskApproverLink.user),
        joinedload(models.Task.histories).joinedload(models.TaskHistory.changed_by)
    ).filter(
        models.Task.id == task_id,
        models.Task.is_active == True
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan")

    return task


@router.patch("/{task_id}", response_model=schemas.TaskRead)
async def update_task(
    task_id: int,
    payload: schemas.TaskUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update task status, priority, assignee, or deadline, and record history."""
    task = db.query(models.Task).options(
        joinedload(models.Task.creator),
        joinedload(models.Task.assignee),
        joinedload(models.Task.approvers).joinedload(models.TaskApproverLink.user)
    ).filter(
        models.Task.id == task_id,
        models.Task.is_active == True
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan")

    is_leader = _is_leadership(current_user)
    is_owner = task.creator_id == current_user.id
    is_assignee = task.assignee_id == current_user.id

    if not (is_leader or is_owner or is_assignee):
        raise HTTPException(status_code=403, detail="Anda tidak memiliki izin mengubah tugas ini")

    old_status = task.status
    old_assignee_id = task.assignee_id

    # Handle text/metadata updates
    if payload.title is not None:
        task.title = payload.title.strip()
    if payload.description is not None:
        task.description = payload.description.strip()
    if payload.priority_level is not None and payload.priority_level in [1, 2, 3, 4, 5]:
        task.priority_level = payload.priority_level
    if payload.unit_id is not None:
        task.unit_id = payload.unit_id
    if payload.deadline is not None:
        task.deadline = payload.deadline

    # Handle Assignee changes
    new_assignee_assigned = False
    if payload.assignee_id is not None and payload.assignee_id != old_assignee_id:
        task.assignee_id = payload.assignee_id
        new_assignee_assigned = True
        # Record assignee change in history
        new_user = db.query(models.User).filter(models.User.id == payload.assignee_id).first()
        assignee_name = new_user.full_name if new_user else "Pengguna lain"
        h = models.TaskHistory(
            task_id=task.id,
            from_status=task.status,
            to_status=task.status,
            comment=f"Penanggung jawab diubah menjadi: {assignee_name}",
            changed_by_id=current_user.id
        )
        db.add(h)

    # Handle Status change
    status_changed = False
    if payload.status is not None and payload.status != old_status:
        valid_statuses = ["antrian", "prioritas", "in_progress", "awaiting_approval", "need_revision", "done"]
        if payload.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Status tidak valid: {payload.status}")

        task.status = payload.status
        status_changed = True

        status_labels = {
            "antrian": "Antrian Tugas",
            "prioritas": "Prioritas Tugas",
            "in_progress": "Sedang Dikerjakan",
            "awaiting_approval": "Menunggu Approval",
            "need_revision": "Butuh Revisi",
            "done": "Selesai"
        }

        comment_msg = payload.comment or f"Status dipindahkan ke '{status_labels.get(payload.status, payload.status)}'"
        h = models.TaskHistory(
            task_id=task.id,
            from_status=old_status,
            to_status=payload.status,
            comment=comment_msg,
            changed_by_id=current_user.id
        )
        db.add(h)

    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)

    # Notifications via BackgroundTasks
    actor_name = current_user.full_name or current_user.nik or "Pimpinan"

    # 1. New assignee notification
    if new_assignee_assigned and task.assignee and task.assignee.email and is_email_configured():
        background_tasks.add_task(
            send_task_notification_email,
            to_email=task.assignee.email,
            to_name=task.assignee.full_name or "Rekan",
            task_title=task.title,
            action_type="assignment",
            task_id=task.id,
            actor_name=actor_name,
            deadline_str=_format_deadline(task.deadline),
            priority_level=task.priority_level,
            note=task.description
        )

    # 2. Status change notifications
    if status_changed and is_email_configured():
        # Awaiting approval -> notify all approvers
        if task.status == "awaiting_approval":
            for link in task.approvers:
                if link.user and link.user.email:
                    background_tasks.add_task(
                        send_task_notification_email,
                        to_email=link.user.email,
                        to_name=link.user.full_name or "Pimpinan",
                        task_title=task.title,
                        action_type="approval_request",
                        task_id=task.id,
                        actor_name=actor_name,
                        deadline_str=_format_deadline(task.deadline),
                        priority_level=task.priority_level,
                        note=payload.comment
                    )
        # Need revision -> notify assignee
        elif task.status == "need_revision" and task.assignee and task.assignee.email:
            background_tasks.add_task(
                send_task_notification_email,
                to_email=task.assignee.email,
                to_name=task.assignee.full_name or "Rekan",
                task_title=task.title,
                action_type="revision_request",
                task_id=task.id,
                actor_name=actor_name,
                deadline_str=_format_deadline(task.deadline),
                priority_level=task.priority_level,
                note=payload.comment
            )
        # Done -> notify creator and assignee
        elif task.status == "done":
            recipients = []
            if task.creator and task.creator.email:
                recipients.append(task.creator)
            if task.assignee and task.assignee.email and task.assignee.id != task.creator_id:
                recipients.append(task.assignee)
            for rec in recipients:
                background_tasks.add_task(
                    send_task_notification_email,
                    to_email=rec.email,
                    to_name=rec.full_name or "Rekan",
                    task_title=task.title,
                    action_type="done",
                    task_id=task.id,
                    actor_name=actor_name,
                    deadline_str=_format_deadline(task.deadline),
                    priority_level=task.priority_level,
                    note=payload.comment
                )

    return task


@router.post("/{task_id}/approve", response_model=schemas.TaskRead)
async def approve_or_reject_task(
    task_id: int,
    payload: schemas.TaskApproveRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Approve or request revision for a task in 'awaiting_approval'."""
    task = db.query(models.Task).options(
        joinedload(models.Task.creator),
        joinedload(models.Task.assignee),
        joinedload(models.Task.approvers).joinedload(models.TaskApproverLink.user)
    ).filter(
        models.Task.id == task_id,
        models.Task.is_active == True
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan")

    is_leader = _is_leadership(current_user)
    my_link = None
    for link in task.approvers:
        if link.user_id == current_user.id:
            my_link = link
            break

    if not my_link and not is_leader:
        raise HTTPException(status_code=403, detail="Anda bukan approver untuk tugas ini")

    actor_name = current_user.full_name or current_user.nik or "Approver"

    if payload.approved:
        # Mark my link as approved
        if my_link:
            my_link.status = "approved"
            my_link.note = payload.note
            my_link.approved_at = datetime.utcnow()
        else:
            # Leadership acting as ad-hoc approver
            link = models.TaskApproverLink(
                task_id=task.id,
                user_id=current_user.id,
                status="approved",
                note=payload.note,
                approved_at=datetime.utcnow()
            )
            db.add(link)

        # Check if ALL approver links are approved
        all_approved = True
        for link in task.approvers:
            if link.user_id != current_user.id and link.status != "approved":
                all_approved = False
                break

        if all_approved or is_leader:
            task.status = "done"
            status_note = f"Disetujui penuh oleh {actor_name}. Tugas Selesai."
        else:
            status_note = f"Disetujui oleh {actor_name}. Menunggu approver lainnya."

        h = models.TaskHistory(
            task_id=task.id,
            from_status="awaiting_approval",
            to_status=task.status,
            comment=payload.note or status_note,
            changed_by_id=current_user.id
        )
        db.add(h)

        db.commit()
        db.refresh(task)

        # If fully done, notify creator and assignee
        if task.status == "done" and is_email_configured():
            recipients = []
            if task.creator and task.creator.email:
                recipients.append(task.creator)
            if task.assignee and task.assignee.email and task.assignee.id != task.creator_id:
                recipients.append(task.assignee)
            for rec in recipients:
                background_tasks.add_task(
                    send_task_notification_email,
                    to_email=rec.email,
                    to_name=rec.full_name or "Rekan",
                    task_title=task.title,
                    action_type="done",
                    task_id=task.id,
                    actor_name=actor_name,
                    deadline_str=_format_deadline(task.deadline),
                    priority_level=task.priority_level,
                    note=payload.note
                )
    else:
        # Revision requested
        if my_link:
            my_link.status = "revision_requested"
            my_link.note = payload.note
            my_link.approved_at = None

        task.status = "need_revision"
        h = models.TaskHistory(
            task_id=task.id,
            from_status="awaiting_approval",
            to_status="need_revision",
            comment=f"Permintaan revisi oleh {actor_name}: {payload.note or 'Harap periksa kembali'}",
            changed_by_id=current_user.id
        )
        db.add(h)

        db.commit()
        db.refresh(task)

        if task.assignee and task.assignee.email and is_email_configured():
            background_tasks.add_task(
                send_task_notification_email,
                to_email=task.assignee.email,
                to_name=task.assignee.full_name or "Rekan",
                task_title=task.title,
                action_type="revision_request",
                task_id=task.id,
                actor_name=actor_name,
                deadline_str=_format_deadline(task.deadline),
                priority_level=task.priority_level,
                note=payload.note
            )

    return task


@router.post("/{task_id}/approvers")
async def set_task_approvers(
    task_id: int,
    user_ids: List[int],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Set or update approvers list for a task."""
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.is_active == True
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan")

    if not (_is_leadership(current_user) or task.creator_id == current_user.id):
        raise HTTPException(status_code=403, detail="Tidak memiliki izin mengatur approver")

    # Clear old links
    db.query(models.TaskApproverLink).filter(models.TaskApproverLink.task_id == task.id).delete()

    unique_ids = list(dict.fromkeys(user_ids))
    for uid in unique_ids:
        link = models.TaskApproverLink(
            task_id=task.id,
            user_id=uid,
            status="pending"
        )
        db.add(link)

    db.commit()
    return {"message": "Daftar approver berhasil diperbarui", "count": len(unique_ids)}


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Soft delete task (is_active = False). Only creator or leadership allowed."""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan")

    if not (_is_leadership(current_user) or task.creator_id == current_user.id):
        raise HTTPException(status_code=403, detail="Hanya pembuat tugas atau pimpinan yang dapat menghapus tugas")

    task.is_active = False
    task.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Tugas berhasil dihapus"}
