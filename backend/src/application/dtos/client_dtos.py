from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class CreateClientRequest(BaseModel):
    """DTO for creating a new client"""
    nombre_completo: str = Field(..., min_length=1, max_length=255)
    cedula: str = Field(..., min_length=8, max_length=20)
    email: str = Field(..., min_length=5, max_length=255)
    telefono: str = Field(..., min_length=7, max_length=20)
    
    @validator('telefono')
    def validate_telefono(cls, v):
        import re
        # Remove spaces and special characters
        phone_clean = re.sub(r'[\s\-\(\)]', '', v)
        
        # Colombian mobile patterns
        patterns = [
            r'^\+57[3][0-9]{9}$',  # +573001234567
            r'^57[3][0-9]{9}$',    # 573001234567
            r'^[3][0-9]{9}$'       # 3001234567
        ]
        
        if not any(re.match(pattern, phone_clean) for pattern in patterns):
            raise ValueError('Teléfono debe ser un número colombiano válido (ej: 3001234567)')
        return v
    fecha_nacimiento: date
    direccion: str = Field(..., min_length=5, max_length=500)
    info_adicional: Optional[Dict[str, Any]] = None
    
    @validator('cedula')
    def validate_cedula(cls, v):
        cedula_digits = ''.join(filter(str.isdigit, v))
        if not (7 <= len(cedula_digits) <= 10):
            raise ValueError(f'Cédula debe tener entre 7 y 10 dígitos (actual: {len(cedula_digits)} dígitos)')
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
        if age < 22:
            raise ValueError(f'El cliente debe tener al menos 22 años (edad actual: {age} años)')
        return v


class UpdateClientRequest(BaseModel):
    """DTO for updating client information"""
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
    limit: int = Field(20, ge=1, le=10000)  # Límite mucho más alto