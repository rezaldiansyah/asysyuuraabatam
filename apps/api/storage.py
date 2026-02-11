"""
Cloudflare R2 Storage Service
S3-compatible object storage with image compression.
"""
import io
import os
import uuid
import boto3
from PIL import Image
from botocore.config import Config


# Image compression settings
MAX_IMAGE_WIDTH = 1920
WEBP_QUALITY = 80
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff'}


def get_r2_client():
    """Create boto3 S3 client configured for Cloudflare R2."""
    account_id = os.getenv("R2_ACCOUNT_ID")
    access_key = os.getenv("R2_ACCESS_KEY_ID")
    secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
    
    if not all([account_id, access_key, secret_key]):
        raise ValueError("R2 credentials not configured. Set R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY")
    
    return boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )


def compress_image(file_bytes: bytes, original_extension: str) -> tuple[bytes, str]:
    """
    Compress image and convert to WebP format.
    Returns (compressed_bytes, new_extension).
    
    - Resizes to max 1920px width (maintains aspect ratio)
    - Converts to WebP format (typically 50-70% smaller)
    - Quality: 80 (good balance of quality vs size)
    """
    img = Image.open(io.BytesIO(file_bytes))
    
    # Handle animated GIFs — skip compression, keep original
    if original_extension.lower() == '.gif' and getattr(img, 'is_animated', False):
        return file_bytes, '.gif'
    
    # Convert RGBA to RGB for WebP compatibility (if needed for palette images)
    if img.mode in ('RGBA', 'LA'):
        # Keep RGBA for WebP (it supports transparency)
        pass
    elif img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGB')
    
    # Resize if wider than MAX_IMAGE_WIDTH
    if img.width > MAX_IMAGE_WIDTH:
        ratio = MAX_IMAGE_WIDTH / img.width
        new_height = int(img.height * ratio)
        img = img.resize((MAX_IMAGE_WIDTH, new_height), Image.LANCZOS)
    
    # Save as WebP
    output = io.BytesIO()
    img.save(output, format='WEBP', quality=WEBP_QUALITY, method=4)
    output.seek(0)
    
    return output.read(), '.webp'


def get_content_type(extension: str) -> str:
    """Get MIME type from file extension."""
    content_types = {
        '.webp': 'image/webp',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }
    return content_types.get(extension.lower(), 'application/octet-stream')


def upload_to_r2(
    file_bytes: bytes,
    original_filename: str,
    folder: str = "uploads"
) -> str:
    """
    Upload file to Cloudflare R2.
    Images are compressed before upload.
    Returns the public URL of the uploaded file.
    """
    client = get_r2_client()
    bucket = os.getenv("R2_BUCKET_NAME", "asy-syuuraa-assets")
    public_url = os.getenv("R2_PUBLIC_URL", "").rstrip("/")
    
    if not public_url:
        raise ValueError("R2_PUBLIC_URL not configured")
    
    # Get file extension
    _, extension = os.path.splitext(original_filename)
    extension = extension.lower()
    
    # Compress if image
    if extension in IMAGE_EXTENSIONS:
        file_bytes, extension = compress_image(file_bytes, extension)
    
    # Generate unique filename
    unique_name = f"{uuid.uuid4()}{extension}"
    object_key = f"{folder}/{unique_name}"
    
    # Upload to R2
    content_type = get_content_type(extension)
    client.put_object(
        Bucket=bucket,
        Key=object_key,
        Body=file_bytes,
        ContentType=content_type,
    )
    
    return f"{public_url}/{object_key}"


def is_r2_configured() -> bool:
    """Check if R2 credentials are set."""
    return all([
        os.getenv("R2_ACCOUNT_ID"),
        os.getenv("R2_ACCESS_KEY_ID"),
        os.getenv("R2_SECRET_ACCESS_KEY"),
        os.getenv("R2_PUBLIC_URL"),
    ])
