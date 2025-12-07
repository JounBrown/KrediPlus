from datetime import datetime, date
from typing import Optional
from dataclasses import dataclass


@dataclass
class LoanApplication:
    """LoanApplication aggregate - Represents credit applications"""
    
    id: Optional[int]
    name: str
    cedula: str
    convenio: Optional[str]
    telefono: str
    fecha_nacimiento: date
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
    

    
    def validate_application_data(self) -> bool:
        """Validate all application data"""
        return (
            self.name and len(self.name.strip()) > 0 and
            self.validate_cedula() and
            self.telefono and len(self.telefono.strip()) > 0 and
            self.is_adult()
        )