from datetime import datetime, date
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class Client:
    """Client aggregate - Represents customers"""
    
    id: Optional[int]
    nombre_completo: str
    cedula: str
    email: str
    telefono: str
    fecha_nacimiento: date
    direccion: str
    info_adicional: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.info_adicional is None:
            self.info_adicional = {}
    
    def validate_cedula(self) -> bool:
        """Validate cedula format (basic validation)"""
        # Remove any non-digit characters
        cedula_digits = ''.join(filter(str.isdigit, self.cedula))
        # Basic validation: should have 8-11 digits
        return 8 <= len(cedula_digits) <= 11
    
    def is_valid_email(self) -> bool:
        """Validate email format"""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, self.email) is not None
    
    def is_adult(self) -> bool:
        """Check if client is 18 years or older"""
        today = date.today()
        age = today.year - self.fecha_nacimiento.year
        if today.month < self.fecha_nacimiento.month or \
           (today.month == self.fecha_nacimiento.month and today.day < self.fecha_nacimiento.day):
            age -= 1
        return age >= 18
    
    def update_contact_info(self, email: str, telefono: str) -> None:
        """Update client contact information"""
        if email and self._is_valid_email_format(email):
            self.email = email
        if telefono:
            self.telefono = telefono
    
    def _is_valid_email_format(self, email: str) -> bool:
        """Helper method for email validation"""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    def validate(self) -> bool:
        """Validate all client data"""
        return (
            self.nombre_completo and len(self.nombre_completo.strip()) > 0 and
            self.validate_cedula() and
            self.is_valid_email() and
            self.telefono and len(self.telefono.strip()) > 0 and
            self.direccion and len(self.direccion.strip()) > 0 and
            self.is_adult()
        )