from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from enum import Enum


class EstadoCreditoDto(str, Enum):
    """Credit status enumeration for DTOs"""
    EN_ESTUDIO = "EN_ESTUDIO"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"
    DESEMBOLSADO = "DESEMBOLSADO"
    AL_DIA = "AL_DIA"
    EN_MORA = "EN_MORA"
    PAGADO = "PAGADO"


class CreateCreditForClientRequest(BaseModel):
    """DTO for creating a credit for a specific client (without client_id in body)"""
    monto_aprobado: Decimal = Field(..., gt=0)
    plazo_meses: int = Field(..., gt=0, le=120)  # Máximo 10 años
    tasa_interes: Decimal = Field(..., gt=0, le=100)  # Porcentaje
    fecha_desembolso: Optional[date] = None
    
    @validator('monto_aprobado')
    def validate_monto(cls, v):
        if v < Decimal('100000'):  # Mínimo 100,000
            raise ValueError('El monto mínimo es 100,000')
        if v > Decimal('100000000'):  # Máximo 100 millones
            raise ValueError('El monto máximo es 100,000,000')
        return v


class CreateCreditRequest(BaseModel):
    """DTO for creating a new credit"""
    client_id: int = Field(..., gt=0)
    monto_aprobado: Decimal = Field(..., gt=0)
    plazo_meses: int = Field(..., gt=0, le=120)  # Máximo 10 años
    tasa_interes: Decimal = Field(..., gt=0, le=100)  # Porcentaje
    fecha_desembolso: Optional[date] = None
    
    @validator('monto_aprobado')
    def validate_monto(cls, v):
        if v < Decimal('100000'):  # Mínimo 100,000
            raise ValueError('El monto mínimo es 100,000')
        if v > Decimal('100000000'):  # Máximo 100 millones
            raise ValueError('El monto máximo es 100,000,000')
        return v


class UpdateCreditRequest(BaseModel):
    """DTO for updating credit information"""
    monto_aprobado: Optional[Decimal] = Field(None, gt=0)
    plazo_meses: Optional[int] = Field(None, gt=0, le=120)
    tasa_interes: Optional[Decimal] = Field(None, gt=0, le=100)
    estado: Optional[EstadoCreditoDto] = None
    fecha_desembolso: Optional[date] = None


class CreditResponse(BaseModel):
    """DTO for credit response"""
    id: int
    client_id: int
    monto_aprobado: Decimal
    plazo_meses: int
    tasa_interes: Decimal
    estado: EstadoCreditoDto
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