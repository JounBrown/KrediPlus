from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.loan_application import LoanApplication, ApplicationStatus


class LoanApplicationRepositoryPort(ABC):
    """Port for LoanApplication repository operations"""
    
    @abstractmethod
    async def create(self, application: LoanApplication) -> LoanApplication:
        """Create a new loan application"""
        pass
    
    @abstractmethod
    async def get_by_id(self, application_id: int) -> Optional[LoanApplication]:
        """Get application by ID"""
        pass
    
    @abstractmethod
    async def get_by_cedula(self, cedula: str) -> List[LoanApplication]:
        """Get applications by cedula"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[LoanApplication]:
        """Get all applications with pagination"""
        pass
    
    @abstractmethod
    async def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[LoanApplication]:
        """Get applications by status"""
        pass
    
    @abstractmethod
    async def get_pending_applications(self, skip: int = 0, limit: int = 100) -> List[LoanApplication]:
        """Get applications that need processing (nueva, en_proceso)"""
        pass
    
    @abstractmethod
    async def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[LoanApplication]:
        """Search applications by applicant name"""
        pass
    
    @abstractmethod
    async def get_by_date_range(self, start_date, end_date, skip: int = 0, limit: int = 100) -> List[LoanApplication]:
        """Get applications within date range"""
        pass
    
    @abstractmethod
    async def update(self, application: LoanApplication) -> LoanApplication:
        """Update application"""
        pass
    
    @abstractmethod
    async def delete(self, application_id: int) -> bool:
        """Delete application (soft delete recommended)"""
        pass
    
    @abstractmethod
    async def update_status(self, application_id: int, new_status: str) -> bool:
        """Update application status"""
        pass
    
    @abstractmethod
    async def count_by_status(self, status: str) -> int:
        """Count applications by status"""
        pass
    
    @abstractmethod
    async def count_total(self) -> int:
        """Get total count of applications"""
        pass
    
    @abstractmethod
    async def get_statistics(self) -> dict:
        """Get application statistics (counts by status, etc.)"""
        pass