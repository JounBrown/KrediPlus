from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Union

from src.infrastructure.inbound.api.middleware.auth_middleware import get_current_user
from src.application.services.client_document_service import ClientDocumentService
from src.application.dtos.client_document_dtos import ClientDocumentResponse
from src.infrastructure.outbound.database.connection import get_db_session
from src.infrastructure.outbound.database.client_document_repository import SupabaseClientDocumentRepository
from src.infrastructure.outbound.supabase_storage_service import SupabaseStorageService

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
    dependencies=[Depends(get_current_user)]
)


def get_document_service(db: AsyncSession = Depends(get_db_session)) -> ClientDocumentService:
    """Dependency to get ClientDocumentService"""
    repository = SupabaseClientDocumentRepository(db)
    storage_service = SupabaseStorageService()
    return ClientDocumentService(repository, storage_service)


def parse_optional_int(value: str) -> Optional[int]:
    """Parse string to int, return None if empty or invalid"""
    if not value or value.strip() == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload"),
    document_type: str = Form(..., description="Type of document (CEDULA_FRENTE, CEDULA_REVERSO, etc.)"),
    client_id: int = Form(..., description="Client ID"),
    credit_id: str = Form("", description="Credit ID (optional, can be empty string)"),
    service: ClientDocumentService = Depends(get_document_service)
):
    """
    Upload a document file to Supabase Storage and save record to database
    """
    try:
        # Validate file size (optional - add if needed)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        if file.size and file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail="File size exceeds maximum limit of 10MB"
            )
        
        # Validate file type (optional - add if needed)
        ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx'}
        if file.filename:
            file_ext = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
            if file_ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
                )
        
        # Parse credit_id (handle empty string)
        parsed_credit_id = parse_optional_int(credit_id)
        
        # Upload document
        result = await service.upload_document(
            file=file,
            document_type=document_type,
            client_id=client_id,
            credit_id=parsed_credit_id
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/client/{client_id}", response_model=List[ClientDocumentResponse])
async def get_client_documents(
    client_id: int,
    service: ClientDocumentService = Depends(get_document_service)
):
    """
    Get all documents for a specific client
    
    - **client_id:** ID of the client to get documents for
    """
    try:
        return await service.get_client_documents(client_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting client documents: {str(e)}")


@router.get("/credit/{credit_id}", response_model=List[ClientDocumentResponse])
async def get_credit_documents(
    credit_id: int,
    service: ClientDocumentService = Depends(get_document_service)
):
    """
    Get all documents for a specific credit
    
    - **credit_id:** ID of the credit to get documents for
    """
    try:
        return await service.get_credit_documents(credit_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting credit documents: {str(e)}")


@router.get("/{document_id}/download")
async def get_document_download_url(
    document_id: int,
    expires_in: int = 3600,
    service: ClientDocumentService = Depends(get_document_service)
):
    """
    Get a signed URL for downloading a document
    
    - **document_id:** ID of the document to download
    - **expires_in:** URL expiration time in seconds (default: 1 hour)
    """
    try:
        signed_url = await service.get_document_download_url(document_id, expires_in)
        return {"download_url": signed_url}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))