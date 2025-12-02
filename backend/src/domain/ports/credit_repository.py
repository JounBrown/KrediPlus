from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.credit import Credit, CreditStatus


class CreditRepositoryPort(ABC):
    """Port for Credit repository operations"""
    
    @abstractmethod
    async def create(self, credit: Credit) -> Credit:
        """Create a new credit"""
        pass
    
    @abstractmethod
    async def get_by_id(self, credit_id: int) -> Optional[Credit]:
        """Get credit by ID"""
        pass
    
    @abstractmethod
    async def get_by_client_id(self, client_id: int) -> List[Credit]:
        """Get all credits for a specific client"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Credit]:
        """Get all credits with pagination"""
        pass
    
    @abstractmethod
    async def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Credit]:
        """Get credits by status"""
        pass
    
    @abstractmethod
    async def get_active_credits(self, skip: int = 0, limit: int = 100) -> List[Credit]:
        """Get active credits"""
        pass
    
    @abstractmethod
    async def get_overdue_credits(self, skip: int = 0, limit: int = 100) -> List[Credit]:
        """Get overdue credits"""
        pass
    
    @abstractmethod
    async def get_credits_for_disbursement(self, skip: int = 0, limit: int = 100) -> List[Credit]:
        """Get approved credits ready for disbursement"""
        pass
    
    @abstractmethod
    async def get_by_date_range(self, start_date, end_date, skip: int = 0, limit: int = 100) -> List[Credit]:
        """Get credits within date range"""
        pass
    
    @abstractmethod
    async def update(self, credit: Credit) -> Credit:
        """Update credit"""
        pass
    
    @abstractmethod
    async def delete(self, credit_id: int) -> bool:
        """Delete credit"""
        pass
    
    @abstractmethod
    async def update_status(self, credit_id: int, new_status: str) -> bool:
        """Update credit status"""
        pass
    
    @abstractmethod
    async def count_by_status(self, status: str) -> int:
        """Count credits by status"""
        pass
    
    @abstractmethod
    async def count_total(self) -> int:
        """Get total count of credits"""
        pass
    
    @abstractmethod
    async def get_portfolio_summary(self) -> dict:
        """Get credit portfolio summary (total amounts, counts by status, etc.)"""
        pass
    
    @abstractmethod
    async def calculate_total_disbursed(self) -> float:
        """Calculate total amount disbursed"""
        pass
    
    @abstractmethod
    async def calculate_total_outstanding(self) -> float:
        """Calculate total outstanding amount"""
        pass