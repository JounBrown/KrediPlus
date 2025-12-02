from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.admin import Admin


class AdminRepositoryPort(ABC):
    """Port for Admin repository operations"""
    
    @abstractmethod
    async def create(self, admin: Admin) -> Admin:
        """Create a new admin"""
        pass
    
    @abstractmethod
    async def get_by_id(self, admin_id: int) -> Optional[Admin]:
        """Get admin by ID"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Admin]:
        """Get admin by email"""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Admin]:
        """Get all admins"""
        pass
    
    @abstractmethod
    async def update(self, admin: Admin) -> Admin:
        """Update admin"""
        pass
    
    @abstractmethod
    async def delete(self, admin_id: int) -> bool:
        """Delete admin"""
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Check if admin exists by email"""
        pass