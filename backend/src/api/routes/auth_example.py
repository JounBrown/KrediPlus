from fastapi import APIRouter, Depends
from typing import Optional
from src.infrastructure.inbound.api.middleware.auth_middleware import (
    get_current_user, 
    get_current_user_optional, 
    require_admin
)
from src.domain.entities.user import User

router = APIRouter(tags=["auth"])


@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Endpoint protegido que requiere autenticación
    """
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }


@router.get("/public-data")
async def get_public_data(current_user: Optional[User] = Depends(get_current_user_optional)):
    """
    Endpoint público que puede mostrar datos diferentes si el usuario está autenticado
    """
    if current_user:
        return {
            "message": f"Hola {current_user.email}, aquí tienes datos personalizados",
            "authenticated": True
        }
    else:
        return {
            "message": "Datos públicos para usuarios no autenticados",
            "authenticated": False
        }


@router.get("/admin-only")
async def admin_endpoint(admin_user: User = Depends(require_admin)):
    """
    Endpoint que solo pueden acceder los administradores
    """
    return {
        "message": "Datos sensibles solo para administradores",
        "admin_user": admin_user.email
    }