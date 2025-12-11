import jwt
import httpx
from typing import Optional
from datetime import datetime
from src.domain.ports.auth_port import AuthPort
from src.domain.entities.user import User
from src.config import SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_JWT_SECRET


class SupabaseAuthAdapter(AuthPort):
    """Adaptador para autenticación con Supabase"""
    
    def __init__(self):
        self.supabase_url = SUPABASE_URL
        self.service_key = SUPABASE_SERVICE_KEY
        self.jwt_secret = SUPABASE_JWT_SECRET
        
    async def _get_jwt_secret(self) -> str:
        """Obtiene el JWT secret de Supabase para verificar tokens"""
        if self.jwt_secret:
            return self.jwt_secret

        # Como fallback, intentar usar el service key. Idealmente debe
        # configurarse SUPABASE_JWT_SECRET explícitamente en el entorno.
        if not self.service_key:
            raise RuntimeError("Supabase JWT secret not configured")

        self.jwt_secret = self.service_key
        return self.jwt_secret
    
    async def verify_token(self, token: str) -> Optional[User]:
        """
        Verifica un token JWT de Supabase y extrae la información del usuario
        """
        try:
            # Obtener el secret para verificar el token
            secret = await self._get_jwt_secret()
            
            # Decodificar el token JWT
            payload = jwt.decode(
                token, 
                secret, 
                algorithms=["HS256"],
                audience="authenticated"  # Supabase usa "authenticated" como audience
            )
            
            # Extraer información del usuario del payload
            user_id = payload.get("sub")
            email = payload.get("email")
            role = payload.get("role")
            
            if not user_id or not email:
                return None
                
            # Crear entidad User
            user = User(
                id=user_id,
                email=email,
                role=role,
                created_at=datetime.fromtimestamp(payload.get("iat", 0)) if payload.get("iat") else None
            )
            
            return user
            
        except jwt.ExpiredSignatureError:
            # Token expirado
            return None
        except jwt.InvalidTokenError:
            # Token inválido
            return None
        except Exception:
            # Cualquier otro error
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Obtiene información adicional del usuario desde Supabase
        """
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.service_key}",
                    "apikey": self.service_key,
                    "Content-Type": "application/json"
                }
                
                # Consultar la tabla auth.users (requiere service key)
                response = await client.get(
                    f"{self.supabase_url}/auth/v1/admin/users/{user_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    
                    return User(
                        id=user_data["id"],
                        email=user_data["email"],
                        role=user_data.get("user_metadata", {}).get("role"),
                        created_at=datetime.fromisoformat(user_data["created_at"].replace("Z", "+00:00")) if user_data.get("created_at") else None,
                        last_sign_in_at=datetime.fromisoformat(user_data["last_sign_in_at"].replace("Z", "+00:00")) if user_data.get("last_sign_in_at") else None
                    )
                
                return None
                
        except Exception:
            return None