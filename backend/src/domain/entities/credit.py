from datetime import datetime, date
from typing import Optional
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal


class CreditStatus(Enum):
    """Credit status enumeration"""
    EN_ESTUDIO = "EN_ESTUDIO"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"
    DESEMBOLSADO = "DESEMBOLSADO"
    AL_DIA = "AL_DIA"
    EN_MORA = "EN_MORA"
    PAGADO = "PAGADO"


@dataclass
class Credit:
    """Credit aggregate - Represents approved credits"""
    
    id: Optional[int]
    monto_aprobado: Decimal
    plazo_meses: int
    tasa_interes: Decimal
    estado: str = CreditStatus.EN_ESTUDIO.value
    fecha_desembolso: Optional[date] = None
    client_id: int = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def calculate_monthly_payment(self) -> Decimal:
        """Calculate monthly payment amount"""
        if self.tasa_interes <= 0:
            return self.monto_aprobado / self.plazo_meses
        
        monthly_rate = self.tasa_interes / Decimal('100')
        payment = (self.monto_aprobado * monthly_rate * (1 + monthly_rate) ** self.plazo_meses) / \
                 ((1 + monthly_rate) ** self.plazo_meses - 1)
        return payment.quantize(Decimal('0.01'))
    
    def calculate_total_payment(self) -> Decimal:
        """Calculate total amount to be paid"""
        monthly_payment = self.calculate_monthly_payment()
        return (monthly_payment * self.plazo_meses).quantize(Decimal('0.01'))
    
    def calculate_total_interest(self) -> Decimal:
        """Calculate total interest to be paid"""
        return (self.calculate_total_payment() - self.monto_aprobado).quantize(Decimal('0.01'))
    
    def approve_credit(self, monto: Decimal, plazo: int, tasa: Decimal) -> bool:
        """Approve credit with specified terms"""
        if self.estado == CreditStatus.EN_ESTUDIO.value and monto > 0 and plazo > 0 and tasa >= 0:
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
    
    def mark_as_current(self) -> bool:
        """Mark credit as current (al día)"""
        if self.estado == CreditStatus.DESEMBOLSADO.value:
            self.estado = CreditStatus.AL_DIA.value
            return True
        return False
    
    def mark_as_paid(self) -> bool:
        """Mark credit as fully paid"""
        if self.estado in [CreditStatus.AL_DIA.value, CreditStatus.EN_MORA.value]:
            self.estado = CreditStatus.PAGADO.value
            return True
        return False
    
    def mark_as_overdue(self) -> bool:
        """Mark credit as overdue (en mora)"""
        if self.estado == CreditStatus.AL_DIA.value:
            self.estado = CreditStatus.EN_MORA.value
            return True
        return False
    
    def reject_credit(self) -> bool:
        """Reject the credit"""
        if self.estado == CreditStatus.EN_ESTUDIO.value:
            self.estado = CreditStatus.RECHAZADO.value
            return True
        return False
    
    def is_active(self) -> bool:
        """Check if credit is currently active"""
        return self.estado in [CreditStatus.AL_DIA.value, CreditStatus.EN_MORA.value, CreditStatus.DESEMBOLSADO.value]
    
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