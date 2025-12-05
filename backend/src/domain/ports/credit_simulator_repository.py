from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.credit_simulator import CreditSimulator


class CreditSimulatorRepositoryPort(ABC):
    """Port for CreditSimulator repository operations"""
    
    @abstractmethod
    async def create(self, simulator: CreditSimulator) -> CreditSimulator:
        """Create a new simulator configuration"""
        pass
    
    @abstractmethod
    async def get_active_config(self) -> Optional[CreditSimulator]:
        """Get the currently active simulator configuration"""
        pass
    
    @abstractmethod
    async def update(self, simulator: CreditSimulator) -> CreditSimulator:
        """Update simulator configuration"""
        pass
    
    @abstractmethod
    async def get_by_id(self, config_id: int) -> Optional[CreditSimulator]:
        """Get simulator configuration by ID"""
        pass