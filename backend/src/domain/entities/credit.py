from datetime import datetime, date
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class CreditStatus(Enum):
    """Credit status enumeration"""
    PENDIENTE = "pendiente"
    APROBADO = "aprobado"
    DESEMBOLSADO = "desembolsado"
    ACTIVO = "activo"
    PAGADO = "pagado"
    VENCIDO = "vencido"
    CANCELADO = "cancelado"


@dataclass
class Credit:
    """Credit aggregate - Represents approved credits"""
    
    id: Optional[int]
    monto_aprobado: float
    plazo_meses: int
    tasa_interes: float
    estado: str = CreditStatus.PENDIENTE.value
    fecha_desembolso: Optional[date] = None
    client_id: int = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def calculate_monthly_payment(self) -> float:
        """Calculate monthly payment amount"""
        if self.tasa_interes <= 0:
            return self.monto_aprobado / self.plazo_meses
        
        monthly_rate = self.tasa_interes / 100
        payment = (self.monto_aprobado * monthly_rate * (1 + monthly_rate) ** self.plazo_meses) / \
                 ((1 + monthly_rate) ** self.plazo_meses - 1)
        return round(payment, 2)
    
    def calculate_total_payment(self) -> float:
        """Calculate total amount to be paid"""
        monthly_payment = self.calculate_monthly_payment()
        return round(monthly_payment * self.plazo_meses, 2)
    
    def calculate_total_interest(self) -> float:
        """Calculate total interest to be paid"""
        return round(self.calculate_total_payment() - self.monto_aprobado, 2)
    
    def approve_credit(self, monto: float, plazo: int, tasa: float) -> bool:
        """Approve credit with specified terms"""
        if self.estado == CreditStatus.PENDIENTE.value and monto > 0 and plazo > 0 and tasa >= 0:
            self.monto_aprobado = monto
            self.plazo_meses = plazo
            self.tasa_interes = tasa
            self.estado = CreditStatus.APROBADO.value
            return True
        return False
    
    def disburse_credit(self, disbursement_date: date = None) -> bool:
        """Disburse the approved credit"""
        if self.estado == CreditStatus.APROBADO.value:
            self.fecha_desembolso = disbursement_date or date.today()
            self.estado = CreditStatus.DESEMBOLSADO.value
            return True
        return False
    
    def activate_credit(self) -> bool:
        """Activate the disbursed credit"""
        if self.estado == CreditStatus.DESEMBOLSADO.value:
            self.estado = CreditStatus.ACTIVO.value
            return True
        return False
    
    def mark_as_paid(self) -> bool:
        """Mark credit as fully paid"""
        if self.estado == CreditStatus.ACTIVO.value:
            self.estado = CreditStatus.PAGADO.value
            return True
        return False
    
    def mark_as_overdue(self) -> bool:
        """Mark credit as overdue"""
        if self.estado == CreditStatus.ACTIVO.value:
            self.estado = CreditStatus.VENCIDO.value
            return True
        return False
    
    def cancel_credit(self) -> bool:
        """Cancel the credit"""
        if self.estado in [CreditStatus.PENDIENTE.value, CreditStatus.APROBADO.value]:
            self.estado = CreditStatus.CANCELADO.value
            return True
        return False
    
    def is_active(self) -> bool:
        """Check if credit is currently active"""
        return self.estado in [CreditStatus.ACTIVO.value, CreditStatus.DESEMBOLSADO.value]
    
    def can_be_disbursed(self) -> bool:
        """Check if credit can be disbursed"""
        return self.estado == CreditStatus.APROBADO.value
    
    def validate(self) -> bool:
        """Validate credit data"""
        return (
            self.monto_aprobado > 0 and
            self.plazo_meses > 0 and
            self.tasa_interes >= 0 and
            self.client_id is not None
        )