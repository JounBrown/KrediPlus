from datetime import datetime, date
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class ApplicationStatus(Enum):
    """Application status enumeration"""
    NUEVA = "nueva"
    EN_PROCESO = "en_proceso"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"
    CANCELADA = "cancelada"


@dataclass
class LoanApplication:
    """LoanApplication aggregate - Represents credit applications"""
    
    id: Optional[int]
    name: str
    cedula: str
    convenio: Optional[str]
    telefono: str
    fecha_nacimiento: date
    monto_solicitado: float
    plazo: int
    estado: str = ApplicationStatus.NUEVA.value
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def validate_cedula(self) -> bool:
        """Validate cedula format"""
        cedula_digits = ''.join(filter(str.isdigit, self.cedula))
        return 8 <= len(cedula_digits) <= 11
    
    def is_adult(self) -> bool:
        """Check if applicant is 18 years or older"""
        today = date.today()
        age = today.year - self.fecha_nacimiento.year
        if today.month < self.fecha_nacimiento.month or \
           (today.month == self.fecha_nacimiento.month and today.day < self.fecha_nacimiento.day):
            age -= 1
        return age >= 18
    
    def validate_amount(self, min_amount: float = 100000, max_amount: float = 50000000) -> bool:
        """Validate requested amount is within limits"""
        return min_amount <= self.monto_solicitado <= max_amount
    
    def validate_term(self, available_terms: list[int] = None) -> bool:
        """Validate loan term"""
        if available_terms is None:
            available_terms = [6, 12, 18, 24, 36, 48, 60]
        return self.plazo in available_terms
    
    def calculate_monthly_payment(self, tasa_interes_mensual: float) -> float:
        """Calculate estimated monthly payment"""
        if tasa_interes_mensual <= 0:
            return self.monto_solicitado / self.plazo
        
        # Formula for loan payment calculation
        monthly_rate = tasa_interes_mensual / 100
        payment = (self.monto_solicitado * monthly_rate * (1 + monthly_rate) ** self.plazo) / \
                 ((1 + monthly_rate) ** self.plazo - 1)
        return round(payment, 2)
    
    def update_status(self, new_status: str) -> bool:
        """Update application status"""
        valid_statuses = [status.value for status in ApplicationStatus]
        if new_status in valid_statuses:
            self.estado = new_status
            return True
        return False
    
    def can_be_approved(self) -> bool:
        """Check if application can be approved"""
        return (
            self.estado == ApplicationStatus.NUEVA.value or 
            self.estado == ApplicationStatus.EN_PROCESO.value
        )
    
    def approve(self) -> bool:
        """Approve the application"""
        if self.can_be_approved():
            self.estado = ApplicationStatus.APROBADA.value
            return True
        return False
    
    def reject(self) -> bool:
        """Reject the application"""
        if self.can_be_approved():
            self.estado = ApplicationStatus.RECHAZADA.value
            return True
        return False
    
    def validate_application_data(self) -> bool:
        """Validate all application data"""
        return (
            self.name and len(self.name.strip()) > 0 and
            self.validate_cedula() and
            self.telefono and len(self.telefono.strip()) > 0 and
            self.is_adult() and
            self.validate_amount() and
            self.validate_term() and
            self.monto_solicitado > 0 and
            self.plazo > 0
        )