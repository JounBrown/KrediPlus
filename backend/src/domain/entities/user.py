from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class User:
    """Entidad de usuario del dominio"""
    id: str
    email: str
    role: Optional[str] = None
    created_at: Optional[datetime] = None
    last_sign_in_at: Optional[datetime] = None
    
    def is_admin(self) -> bool:
        """Verifica si el usuario tiene rol de administrador"""
        return self.role == "admin"
    
    def is_active(self) -> bool:
        """Verifica si el usuario está activo"""
        return self.id is not None and self.email is not None