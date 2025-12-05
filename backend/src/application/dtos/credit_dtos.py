from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class CreateCreditRequest(BaseModel):
    """DTO for creating a new credit"""
    client_id: int = Field(..., gt=0)
    monto_aprobado: float = Field(..., gt=0)
    plazo_meses: int = Field(..., gt=0, le=120)  # Máximo 10 años
    tasa_interes: float = Field(..., gt=0, le=100)  # Porcentaje
    fecha_desembolso: Optional[date] = None
    
    @validator('monto_aprobado')
    def validate_monto(cls, v):
        if v < 100000:  # Mínimo 100,000
            raise ValueError('El monto mínimo es 100,000')
        if v > 100000000:  # Máximo 100 millones
            raise ValueError('El monto máximo es 100,000,000')
        return v


class UpdateCreditRequest(BaseModel):
    """DTO for updating credit information"""
    monto_aprobado: Optional[float] = Field(None, gt=0)
    plazo_meses: Optional[int] = Field(None, gt=0, le=120)
    tasa_interes: Optional[float] = Field(None, gt=0, le=100)
    estado: Optional[str] = None
    fecha_desembolso: Optional[date] = None
    
    @validator('estado')
    def validate_estado(cls, v):
        if v is not None:
            valid_states = ["pendiente", "aprobado", "desembolsado", "pagado", "vencido", "cancelado"]
            if v not in valid_states:
                raise ValueError(f'Estado debe ser uno de: {valid_states}')
        return v


class CreditResponse(BaseModel):
    """DTO for credit response"""
    id: int
    client_id: int
    monto_aprobado: float
    plazo_meses: int
    tasa_interes: float
    estado: str
    fecha_desembolso: Optional[date]
    created_at: datetime
    
    class Config:
        from_attributes = True


class CreditListResponse(BaseModel):
    """DTO for paginated credit list"""
    credits: list[CreditResponse]
    total: int
    page: int
    page_size: int
    total_pages: int