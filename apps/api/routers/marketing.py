from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from database import get_db
import models
import json
from datetime import datetime

router = APIRouter(prefix="/marketing", tags=["Marketing & Branding"])

# ============================================================
# TESTIMONIALS
# ============================================================

@router.get("/testimonials")
async def get_testimonials(published_only: bool = False, db: Session = Depends(get_db)):
    """Get all testimonials. Pass published_only=true for public pages."""
    query = db.query(models.Testimonial)
    if published_only:
        query = query.filter(models.Testimonial.is_published == True)
    return query.order_by(models.Testimonial.sort_order, models.Testimonial.created_at.desc()).all()

@router.post("/testimonials")
async def create_testimonial(data: dict, db: Session = Depends(get_db)):
    """Admin: Create a new testimonial"""
    testimonial = models.Testimonial(
        name=data.get("name", ""),
        role=data.get("role", ""),
        content=data.get("content", ""),
        photo_url=data.get("photo_url"),
        rating=data.get("rating", 5),
        is_published=data.get("is_published", True),
        sort_order=data.get("sort_order", 0)
    )
    db.add(testimonial)
    db.commit()
    db.refresh(testimonial)
    return testimonial

@router.put("/testimonials/{id}")
async def update_testimonial(id: int, data: dict, db: Session = Depends(get_db)):
    """Admin: Update a testimonial"""
    testimonial = db.query(models.Testimonial).filter(models.Testimonial.id == id).first()
    if not testimonial:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    
    for key in ["name", "role", "content", "photo_url", "rating", "is_published", "sort_order"]:
        if key in data:
            setattr(testimonial, key, data[key])
    
    db.commit()
    db.refresh(testimonial)
    return testimonial

@router.delete("/testimonials/{id}")
async def delete_testimonial(id: int, db: Session = Depends(get_db)):
    """Admin: Delete a testimonial"""
    testimonial = db.query(models.Testimonial).filter(models.Testimonial.id == id).first()
    if not testimonial:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    db.delete(testimonial)
    db.commit()
    return {"message": "Testimonial deleted"}

# ============================================================
# GALLERY ALBUMS
# ============================================================

@router.get("/gallery/albums")
async def get_albums(category: str = None, published_only: bool = False, db: Session = Depends(get_db)):
    """Get all gallery albums, optionally filtered by category (kegiatan/prestasi)"""
    query = db.query(models.GalleryAlbum)
    if category:
        query = query.filter(models.GalleryAlbum.category == category)
    if published_only:
        query = query.filter(models.GalleryAlbum.is_published == True)
    
    albums = query.order_by(models.GalleryAlbum.sort_order, models.GalleryAlbum.created_at.desc()).all()
    
    result = []
    for album in albums:
        result.append({
            "id": album.id,
            "title": album.title,
            "description": album.description,
            "category": album.category,
            "cover_url": album.cover_url,
            "is_published": album.is_published,
            "sort_order": album.sort_order,
            "created_at": album.created_at,
            "photo_count": len(album.photos) if album.photos else 0
        })
    return result

@router.get("/gallery/albums/{id}")
async def get_album_detail(id: int, db: Session = Depends(get_db)):
    """Get album detail with all photos"""
    album = db.query(models.GalleryAlbum).options(
        joinedload(models.GalleryAlbum.photos)
    ).filter(models.GalleryAlbum.id == id).first()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    photos = sorted(album.photos, key=lambda p: p.sort_order) if album.photos else []
    
    return {
        "id": album.id,
        "title": album.title,
        "description": album.description,
        "category": album.category,
        "cover_url": album.cover_url,
        "is_published": album.is_published,
        "created_at": album.created_at,
        "photos": [{
            "id": p.id,
            "image_url": p.image_url,
            "caption": p.caption,
            "sort_order": p.sort_order
        } for p in photos]
    }

@router.post("/gallery/albums")
async def create_album(data: dict, db: Session = Depends(get_db)):
    """Admin: Create a new gallery album"""
    album = models.GalleryAlbum(
        title=data.get("title", ""),
        description=data.get("description"),
        category=data.get("category", "kegiatan"),
        cover_url=data.get("cover_url"),
        is_published=data.get("is_published", True),
        sort_order=data.get("sort_order", 0)
    )
    db.add(album)
    db.commit()
    db.refresh(album)
    return album

@router.put("/gallery/albums/{id}")
async def update_album(id: int, data: dict, db: Session = Depends(get_db)):
    """Admin: Update a gallery album"""
    album = db.query(models.GalleryAlbum).filter(models.GalleryAlbum.id == id).first()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    for key in ["title", "description", "category", "cover_url", "is_published", "sort_order"]:
        if key in data:
            setattr(album, key, data[key])
    
    db.commit()
    db.refresh(album)
    return album

@router.delete("/gallery/albums/{id}")
async def delete_album(id: int, db: Session = Depends(get_db)):
    """Admin: Delete a gallery album and all its photos"""
    album = db.query(models.GalleryAlbum).filter(models.GalleryAlbum.id == id).first()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    db.delete(album)
    db.commit()
    return {"message": "Album deleted"}

# ============================================================
# GALLERY PHOTOS
# ============================================================

@router.post("/gallery/albums/{album_id}/photos")
async def add_photos(album_id: int, data: dict, db: Session = Depends(get_db)):
    """Admin: Add photos to an album"""
    album = db.query(models.GalleryAlbum).filter(models.GalleryAlbum.id == album_id).first()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    photos_data = data.get("photos", [])
    added = []
    for i, photo in enumerate(photos_data):
        p = models.GalleryPhoto(
            album_id=album_id,
            image_url=photo.get("image_url", ""),
            caption=photo.get("caption"),
            sort_order=photo.get("sort_order", i)
        )
        db.add(p)
        added.append(p)
    
    # Auto-set cover if album has none
    if not album.cover_url and photos_data:
        album.cover_url = photos_data[0].get("image_url", "")
    
    db.commit()
    return {"message": f"{len(added)} photos added"}

@router.delete("/gallery/photos/{photo_id}")
async def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    """Admin: Delete a single photo"""
    photo = db.query(models.GalleryPhoto).filter(models.GalleryPhoto.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    db.delete(photo)
    db.commit()
    return {"message": "Photo deleted"}
