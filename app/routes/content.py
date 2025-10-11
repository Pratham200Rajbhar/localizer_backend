"""
Content upload routes
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.file import File as FileModel
from app.schemas.file import FileResponse
from app.utils.file_manager import file_manager
from app.utils.logger import app_logger

router = APIRouter(prefix="/content", tags=["Content"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".doc", ".odt", ".rtf"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@router.post("/upload", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    domain: Optional[str] = Form(None),
    source_language: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a content file for translation
    
    Supported formats: PDF, DOCX, TXT, DOC, ODT, RTF
    Maximum size: 50 MB
    """
    # Validate file extension
    file_ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type not supported. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file to check size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)} MB"
        )
    
    # Reset file pointer
    await file.seek(0)
    
    # Save file to disk
    try:
        saved_file = await file_manager.save_upload(file)
        
        # Create database entry
        db_file = FileModel(
            filename=saved_file["filename"],
            original_filename=file.filename,
            path=saved_file["file_path"],
            file_type=file_ext,
            size=saved_file["size"],
            domain=domain,
            source_language=source_language,
            uploader_id=current_user.id
        )
        
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        app_logger.info(
            f"File uploaded: {file.filename} by user {current_user.username}"
        )
        
        return db_file
    
    except Exception as e:
        app_logger.error(f"File upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error uploading file"
        )


@router.get("/files", response_model=list[FileResponse])
async def list_files(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List uploaded files
    
    Admins see all files, others see only their own
    """
    if current_user.role == "admin":
        files = db.query(FileModel).offset(skip).limit(limit).all()
    else:
        files = db.query(FileModel).filter(
            FileModel.uploader_id == current_user.id
        ).offset(skip).limit(limit).all()
    
    return files


@router.get("/files/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get file details
    """
    file = db.query(FileModel).filter(FileModel.id == file_id).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check permissions
    if current_user.role != "admin" and file.uploader_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return file


@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a file
    """
    file = db.query(FileModel).filter(FileModel.id == file_id).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check permissions
    if current_user.role != "admin" and file.uploader_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Delete from disk
    file_manager.delete_file(file.path)
    
    # Delete from database
    db.delete(file)
    db.commit()
    
    app_logger.info(f"File deleted: {file.filename} by user {current_user.username}")
    
    return None

