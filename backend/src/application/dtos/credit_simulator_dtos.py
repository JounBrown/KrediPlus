from pydantic import BaseModel, Field, validator
from typing import List


class SimulateCreditRequest(BaseModel):
    """DTO for credit simulation request"""
    monto: float = Field(..., gt=0, description="Loan amount")
    plazo_meses: int = Field(..., gt=0, le=120, description="Term in months")
    
    @validator('monto')
    def validate_monto(cls, v):
        if v < 100000:  # Mínimo 100,000
            raise ValueError('El monto mínimo es 100,000')
        if v > 100000000:  # Máximo 100 millones
            raise ValueError('El monto máximo es 100,000,000')
        return v
    
    @validator('plazo_meses')
    def validate_plazo(cls, v):
        valid_terms = [6, 12, 18, 24, 36, 48, 60, 72]
        if v not in valid_terms:
            raise ValueError(f'Plazo debe ser uno de: {valid_terms}')
        return v


class SimulateCreditResponse(BaseModel):
    """DTO for credit simulation response"""
    monto_solicitado: float
    plazo_meses: int
    tasa_interes_mensual: float
    cuota_mensual: float
    total_a_pagar: float
    total_intereses: float
    
    class Config:
        from_attributes = True


class CreateSimulatorConfigRequest(BaseModel):
    """DTO for creating/updating simulator configuration"""
    tasa_interes_mensual: float = Field(..., gt=0, le=0.2, description="Monthly interest rate (0.001 - 0.2)")
    monto_minimo: float = Field(..., gt=0, description="Minimum loan amount")
    monto_maximo: float = Field(..., gt=0, description="Maximum loan amount")
    plazos_disponibles: List[int] = Field(..., description="Available terms in months")
    is_active: bool = Field(False, description="Whether this configuration should be active")
    
    @validator('tasa_interes_mensual')
    def validate_tasa(cls, v):
        if v <= 0 or v > 0.2:  # Máximo 20% mensual
            raise ValueError('Tasa debe estar entre 0.1% y 20% mensual')
        return v
    
    @validator('monto_maximo')
    def validate_montos(cls, v, values):
        if 'monto_minimo' in values and v <= values['monto_minimo']:
            raise ValueError('Monto máximo debe ser mayor al monto mínimo')
        return v
    
    @validator('plazos_disponibles')
    def validate_plazos(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Debe especificar al menos un plazo')
        if any(plazo <= 0 or plazo > 120 for plazo in v):
            raise ValueError('Plazos deben estar entre 1 y 120 meses')
        return sorted(list(set(v)))  # Remove duplicates and sort


class UpdateSimulatorConfigRequest(BaseModel):
    """DTO for updating simulator configuration (partial updates allowed)"""
    tasa_interes_mensual: float = Field(None, gt=0, le=0.2, description="Monthly interest rate (0.001 - 0.2)")
    monto_minimo: float = Field(None, gt=0, description="Minimum loan amount")
    monto_maximo: float = Field(None, gt=0, description="Maximum loan amount")
    plazos_disponibles: List[int] = Field(None, description="Available terms in months")
    # is_active removed - use POST /config/{id}/activate to change active status
    
    @validator('tasa_interes_mensual')
    def validate_tasa(cls, v):
        if v is not None and (v <= 0 or v > 0.2):  # Máximo 20% mensual
            raise ValueError('Tasa debe estar entre 0.1% y 20% mensual')
        return v
    
    @validator('plazos_disponibles')
    def validate_plazos(cls, v):
        if v is not None:
            if len(v) == 0:
                raise ValueError('Debe especificar al menos un plazo')
            if any(plazo <= 0 or plazo > 120 for plazo in v):
                raise ValueError('Plazos deben estar entre 1 y 120 meses')
            return sorted(list(set(v)))  # Remove duplicates and sort
        return v


class SimulatorConfigResponse(BaseModel):
    """DTO for simulator configuration response"""
    id: int
    tasa_interes_mensual: float
    monto_minimo: float
    monto_maximo: float
    plazos_disponibles: List[int]
    is_active: bool
    
    class Config:
        from_attributes = True