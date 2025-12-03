from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from src.domain.entities.loan_application import ApplicationStatus


class CreateLoanApplicationRequest(BaseModel):
    """DTO for creating a new loan application"""
    name: str = Field(..., min_length=1, max_length=255)
    cedula: str = Field(..., min_length=8, max_length=20)
    convenio: Optional[str] = Field(None, max_length=100)
    telefono: str = Field(..., min_length=7, max_length=20)
    fecha_nacimiento: date
    monto_solicitado: float = Field(..., gt=0, le=100000000)
    plazo: int = Field(..., gt=0, le=120)
    
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
    
    @validator('monto_solicitado')
    def validate_amount(cls, v):
        if v < 100000:  # Minimum 100,000
            raise ValueError('El monto mínimo es $100,000')
        if v > 50000000:  # Maximum 50,000,000
            raise ValueError('El monto máximo es $50,000,000')
        return v
    
    @validator('plazo')
    def validate_term(cls, v):
        valid_terms = [6, 12, 18, 24, 36, 48, 60, 72]
        if v not in valid_terms:
            raise ValueError(f'Plazo debe ser uno de: {valid_terms} meses')
        return v


class UpdateLoanApplicationStatusRequest(BaseModel):
    """DTO for updating loan application status"""
    application_id: int = Field(..., gt=0)
    new_status: str = Field(...)
    notes: Optional[str] = Field(None, max_length=1000)
    
    @validator('new_status')
    def validate_status(cls, v):
        valid_statuses = [status.value for status in ApplicationStatus]
        if v not in valid_statuses:
            raise ValueError(f'Estado debe ser uno de: {valid_statuses}')
        return v


class LoanApplicationResponse(BaseModel):
    """DTO for loan application response"""
    id: int
    name: str
    cedula: str
    convenio: Optional[str]
    telefono: str
    fecha_nacimiento: date
    monto_solicitado: float
    plazo: int
    estado: str
    created_at: datetime
    estimated_monthly_payment: Optional[float] = None
    
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
    nueva: int
    en_proceso: int
    aprobada: int
    rechazada: int
    cancelada: int
    total_amount_requested: float
    average_amount: float
    average_term: float


class ListClientLoanApplicationsRequest(BaseModel):
    """DTO for listing client loan applications"""
    cedula: str = Field(..., min_length=8, max_length=20)
    status_filter: Optional[str] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)
    
    @validator('status_filter')
    def validate_status_filter(cls, v):
        if v is not None:
            valid_statuses = [status.value for status in ApplicationStatus]
            if v not in valid_statuses:
                raise ValueError(f'Estado debe ser uno de: {valid_statuses}')
        return v