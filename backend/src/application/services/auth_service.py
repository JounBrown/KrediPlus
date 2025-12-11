from typing import Optional
from src.domain.ports.auth_port import AuthPort
from src.domain.entities.user import User


class AuthService:
    """Servicio de aplicación para autenticación"""
    
    def __init__(self, auth_port: AuthPort):
        self.auth_port = auth_port
    
    async def authenticate_user(self, token: str) -> Optional[User]:
        """
        Autentica un usuario usando su token JWT
        
        Args:
            token: Token JWT del frontend
            
        Returns:
            User si la autenticación es exitosa, None si falla
        """
        if not token:
            return None
            
        # Remover "Bearer " si está presente
        if token.startswith("Bearer "):
            token = token[7:]
            
        return await self.auth_port.verify_token(token)
    
    async def get_user_details(self, user_id: str) -> Optional[User]:
        """
        Obtiene detalles completos de un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            User con detalles completos si existe
        """
        return await self.auth_port.get_user_by_id(user_id)
    
    async def authorize_admin(self, token: str) -> bool:
        """
        Verifica si el usuario tiene permisos de administrador
        
        Args:
            token: Token JWT del usuario
            
        Returns:
            True si es admin, False si no
        """
        user = await self.authenticate_user(token)
        return user is not None and user.is_admin()