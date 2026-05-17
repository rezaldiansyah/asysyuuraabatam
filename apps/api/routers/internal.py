from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from database import get_db
import models
from datetime import datetime
from typing import Optional
from deps import get_current_user

router = APIRouter(prefix="/internal", tags=["Internal Management"])

# ============================================================
# DOCUMENT CENTER (Pusat Unduhan)
# ============================================================

DOCUMENT_CATEGORIES = [
    {"value": "sk_yayasan", "label": "SK Yayasan"},
    {"value": "sop", "label": "SOP"},
    {"value": "kalender_akademik", "label": "Kalender Akademik"},
    {"value": "juknis", "label": "Juknis"},
    {"value": "surat_edaran", "label": "Surat Edaran"},
    {"value": "lainnya", "label": "Lainnya"},
]

@router.get("/documents/categories")
async def get_document_categories():
    """Get available document categories."""
    return DOCUMENT_CATEGORIES

@router.get("/documents")
async def get_documents(
    category: Optional[str] = None,
    visibility: Optional[str] = None,
    search: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all documents (authenticated users only)."""
    query = db.query(models.Document).filter(models.Document.is_active == True)
    
    if category:
        query = query.filter(models.Document.category == category)
    if visibility:
        query = query.filter(models.Document.visibility == visibility)
    if search:
        query = query.filter(models.Document.title.ilike(f"%{search}%"))
    
    docs = query.options(joinedload(models.Document.uploader)).order_by(models.Document.created_at.desc()).all()
    
    result = []
    for doc in docs:
        result.append({
            "id": doc.id,
            "title": doc.title,
            "description": doc.description,
            "category": doc.category,
            "file_url": doc.file_url,
            "file_name": doc.file_name,
            "file_size": doc.file_size,
            "visibility": doc.visibility,
            "uploaded_by": doc.uploaded_by,
            "uploader_name": doc.uploader.full_name if doc.uploader else None,
            "is_active": doc.is_active,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
            "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
        })
    
    return result

@router.post("/documents")
async def create_document(
    data: dict,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new document entry."""
    doc = models.Document(
        title=data.get("title"),
        description=data.get("description"),
        category=data.get("category", "lainnya"),
        file_url=data.get("file_url"),
        file_name=data.get("file_name"),
        file_size=data.get("file_size"),
        visibility=data.get("visibility", "internal"),
        uploaded_by=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {"id": doc.id, "message": "Document created successfully"}

@router.put("/documents/{doc_id}")
async def update_document(
    doc_id: int,
    data: dict,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a document entry."""
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    for field in ["title", "description", "category", "file_url", "file_name", "file_size", "visibility"]:
        if field in data:
            setattr(doc, field, data[field])
    
    doc.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(doc)
    return {"id": doc.id, "message": "Document updated successfully"}

@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft-delete a document."""
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc.is_active = False
    db.commit()
    return {"message": "Document deleted successfully"}
