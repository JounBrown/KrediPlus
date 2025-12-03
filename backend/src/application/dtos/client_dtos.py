from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class CreateClientRequest(BaseModel):
    """DTO for creating a new client"""
    nombre_completo: str = Field(..., min_length=1, max_length=255)
    cedula: str = Field(..., min_length=8, max_length=20)
    email: str = Field(..., min_length=5, max_length=255)
    telefono: str = Field(..., min_length=7, max_length=20)
    fecha_nacimiento: date
    direccion: str = Field(..., min_length=5, max_length=500)
    info_adicional: Optional[Dict[str, Any]] = None
    
    @validator('cedula')
    def validate_cedula(cls, v):
        cedula_digits = ''.join(filter(str.isdigit, v))
        if not (8 <= len(cedula_digits) <= 11):
            raise ValueError('Cédula debe tener entre 8 y 11 dígitos')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Email inválido')
        return v
    
    @validator('fecha_nacimiento')
    def validate_age(cls, v):
        today = date.today()
        age = today.year - v.year
        if today.month < v.month or (today.month == v.month and today.day < v.day):
            age -= 1
        if age < 18:
            raise ValueError('El cliente debe ser mayor de edad (18 años)')
        return v


class UpdateClientRequest(BaseModel):
    """DTO for updating client information"""
    client_id: int = Field(..., gt=0)
    nombre_completo: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, min_length=5, max_length=255)
    telefono: Optional[str] = Field(None, min_length=7, max_length=20)
    direccion: Optional[str] = Field(None, min_length=5, max_length=500)
    info_adicional: Optional[Dict[str, Any]] = None
    
    @validator('email')
    def validate_email(cls, v):
        if v is not None:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v):
                raise ValueError('Email inválido')
        return v


class ClientResponse(BaseModel):
    """DTO for client response"""
    id: int
    nombre_completo: str
    cedula: str
    email: str
    telefono: str
    fecha_nacimiento: date
    direccion: str
    info_adicional: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ClientListResponse(BaseModel):
    """DTO for paginated client list"""
    clients: List[ClientResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SearchClientsRequest(BaseModel):
    """DTO for searching clients"""
    search_term: Optional[str] = None  # Busca en nombre o cédula
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)