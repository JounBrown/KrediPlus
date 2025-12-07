from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class CreateLoanApplicationRequest(BaseModel):
    """DTO for creating a new loan application"""
    name: str = Field(..., min_length=1, max_length=255)
    cedula: str = Field(..., min_length=8, max_length=20)
    convenio: Optional[str] = Field(None, max_length=100)
    telefono: str = Field(..., min_length=7, max_length=20)
    fecha_nacimiento: date
    
    @validator('cedula')
    def validate_cedula(cls, v):
        # Remove any non-digit characters and validate length
        cedula_digits = ''.join(filter(str.isdigit, v))
        if not (8 <= len(cedula_digits) <= 11):
            raise ValueError('Cédula debe tener entre 8 y 11 dígitos')
        return v
    
    @validator('fecha_nacimiento')
    def validate_age(cls, v):
        today = date.today()
        age = today.year - v.year
        if today.month < v.month or (today.month == v.month and today.day < v.day):
            age -= 1
        if age < 18:
            raise ValueError('El solicitante debe ser mayor de edad (18 años)')
        return v


class UpdateLoanApplicationRequest(BaseModel):
    """DTO for updating loan application"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    convenio: Optional[str] = Field(None, max_length=100)
    telefono: Optional[str] = Field(None, min_length=7, max_length=20)
    fecha_nacimiento: Optional[date] = None
    
    @validator('fecha_nacimiento')
    def validate_age(cls, v):
        if v is not None:
            today = date.today()
            age = today.year - v.year
            if today.month < v.month or (today.month == v.month and today.day < v.day):
                age -= 1
            if age < 18:
                raise ValueError('El solicitante debe ser mayor de edad (18 años)')
        return v


class LoanApplicationResponse(BaseModel):
    """DTO for loan application response"""
    id: int
    name: str
    cedula: str
    convenio: Optional[str]
    telefono: str
    fecha_nacimiento: date
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoanApplicationListResponse(BaseModel):
    """DTO for paginated loan application list"""
    applications: List[LoanApplicationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class LoanApplicationStatsResponse(BaseModel):
    """DTO for loan application statistics"""
    total_applications: int
    applications_by_convenio: dict
    applications_by_month: dict


class ListClientLoanApplicationsRequest(BaseModel):
    """DTO for listing client loan applications"""
    cedula: str = Field(..., min_length=8, max_length=20)
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)