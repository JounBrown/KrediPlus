from datetime import datetime, date
from typing import Optional, Dict, Any
from dataclasses import dataclass
import re


@dataclass
class Client:
    """Client aggregate - Represents customers with validation methods"""
    
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
    
    # 1. Validación de formato de email
    def validate_email(self) -> bool:
        """Validate that email has correct format"""
        if not self.email or not self.email.strip():
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, self.email.strip()) is not None
    
    # 2. Validación de número de teléfono colombiano
    def validate_phone(self) -> bool:
        """Validate Colombian phone number format"""
        if not self.telefono or not self.telefono.strip():
            return False
        
        # Remove spaces and special characters
        phone_clean = re.sub(r'[\s\-\(\)]', '', self.telefono)
        
        # Colombian mobile patterns:
        # +573001234567, 573001234567, 3001234567
        patterns = [
            r'^\+57[3][0-9]{9}$',  # +573001234567
            r'^57[3][0-9]{9}$',    # 573001234567
            r'^[3][0-9]{9}$'       # 3001234567
        ]
        
        return any(re.match(pattern, phone_clean) for pattern in patterns)
    
    # 3. Validación de documento de identidad
    def validate_document(self) -> bool:
        """Validate Colombian ID document (cedula) format"""
        if not self.cedula or not self.cedula.strip():
            return False
        
        # Remove any non-digit characters
        cedula_digits = ''.join(filter(str.isdigit, self.cedula))
        
        # Colombian cedula: 7 to 10 digits
        return 7 <= len(cedula_digits) <= 10 and cedula_digits.isdigit()
    
    # 4. Validación de edad (mínimo 22 años)
    def validate_age(self) -> bool:
        """Validate that client age is at least 22 years"""
        if not self.fecha_nacimiento:
            return False
        
        today = date.today()
        age = today.year - self.fecha_nacimiento.year
        
        # Adjust age if birthday hasn't occurred this year
        if today.month < self.fecha_nacimiento.month or \
           (today.month == self.fecha_nacimiento.month and today.day < self.fecha_nacimiento.day):
            age -= 1
        
        return age >= 22
    
    def get_age(self) -> int:
        """Calculate and return current age"""
        today = date.today()
        age = today.year - self.fecha_nacimiento.year
        
        if today.month < self.fecha_nacimiento.month or \
           (today.month == self.fecha_nacimiento.month and today.day < self.fecha_nacimiento.day):
            age -= 1
        
        return age
    
    # 5. Validación de completitud de datos
    def is_complete(self) -> bool:
        """Validate that all required fields are complete"""
        required_fields = [
            self.nombre_completo,
            self.cedula,
            self.email,
            self.telefono,
            self.direccion
        ]
        
        return all(field and field.strip() for field in required_fields) and \
               self.fecha_nacimiento is not None
    
    def update_contact_info(self, email: Optional[str] = None, telefono: Optional[str] = None) -> bool:
        """
        Update client contact information with validation
        
        Args:
            email: New email address (optional)
            telefono: New phone number (optional)
            
        Returns:
            bool: True if update was successful, False if validation failed
        """
        updated = False
        
        if email is not None:
            # Create temporary client to validate email
            temp_client = Client(
                id=self.id,
                nombre_completo=self.nombre_completo,
                cedula=self.cedula,
                email=email,
                telefono=self.telefono,
                fecha_nacimiento=self.fecha_nacimiento,
                direccion=self.direccion
            )
            
            if temp_client.validate_email():
                self.email = email
                updated = True
        
        if telefono is not None:
            # Create temporary client to validate phone
            temp_client = Client(
                id=self.id,
                nombre_completo=self.nombre_completo,
                cedula=self.cedula,
                email=self.email,
                telefono=telefono,
                fecha_nacimiento=self.fecha_nacimiento,
                direccion=self.direccion
            )
            
            if temp_client.validate_phone():
                self.telefono = telefono
                updated = True
        
        return updated
    
    def validate(self) -> bool:
        """
        Validate all client data using all validation methods
        
        Returns:
            bool: True if all validations pass, False otherwise
        """
        return (
            self.is_complete() and
            self.validate_email() and
            self.validate_phone() and
            self.validate_document() and
            self.validate_age()
        )
    
    def get_validation_errors(self) -> list[str]:
        """
        Get list of validation errors for debugging
        
        Returns:
            list[str]: List of validation error messages
        """
        errors = []
        
        if not self.is_complete():
            errors.append("Faltan campos obligatorios")
        
        if not self.validate_email():
            errors.append("Formato de email inválido")
        
        if not self.validate_phone():
            errors.append("Formato de teléfono inválido (debe ser número colombiano)")
        
        if not self.validate_document():
            errors.append("Formato de cédula inválido (7-10 dígitos)")
        
        if not self.validate_age():
            errors.append(f"Edad inválida: {self.get_age()} años (debe ser mayor de 22 años)")
        
        return errors