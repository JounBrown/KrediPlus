from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.admin import Admin


class AuthServicePort(ABC):
    """Port for authentication operations"""
    
    @abstractmethod
    async def authenticate_admin(self, email: str, password: str) -> Optional[Admin]:
        """Authenticate admin with email and password"""
        pass
    
    @abstractmethod
    async def create_access_token(self, admin: Admin) -> str:
        """Create JWT access token for admin"""
        pass
    
    @abstractmethod
    async def verify_token(self, token: str) -> Optional[Admin]:
        """Verify JWT token and return admin if valid"""
        pass
    
    @abstractmethod
    async def revoke_token(self, token: str) -> bool:
        """Revoke/invalidate a token"""
        pass
    
    @abstractmethod
    async def hash_password(self, password: str) -> str:
        """Hash password for storage"""
        pass
    
    @abstractmethod
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        pass