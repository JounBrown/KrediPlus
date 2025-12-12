from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.user import User


class AuthPort(ABC):
    """Puerto para servicios de autenticación"""
    
    @abstractmethod
    async def verify_token(self, token: str) -> Optional[User]:
        """
        Verifica un token JWT y retorna el usuario si es válido
        
        Args:
            token: Token JWT a verificar
            
        Returns:
            User si el token es válido, None si no lo es
        """
        pass
    
    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Obtiene un usuario por su ID
        
        Args:
            user_id: ID del usuario
            
        Returns:
            User si existe, None si no existe
        """
        pass