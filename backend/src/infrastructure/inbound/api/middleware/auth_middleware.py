from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from src.application.services.auth_service import AuthService
from src.infrastructure.outbound.supabase_auth_adapter import SupabaseAuthAdapter
from src.domain.entities.user import User

# Configuración del esquema de seguridad
security = HTTPBearer()

# Instancia global del servicio de auth (se puede mejorar con DI)
_auth_service = AuthService(SupabaseAuthAdapter())


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependency para obtener el usuario actual autenticado
    
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    user = await _auth_service.authenticate_user(credentials.credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Dependency para obtener el usuario actual (opcional)
    
    Returns:
        User si está autenticado, None si no hay token o es inválido
    """
    if not credentials:
        return None
        
    return await _auth_service.authenticate_user(credentials.credentials)


async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency que requiere permisos de administrador
    
    Raises:
        HTTPException: Si el usuario no es administrador
    """
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    
    return current_user