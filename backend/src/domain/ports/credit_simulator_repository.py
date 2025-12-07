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
    
    @abstractmethod
    async def get_all(self) -> list[CreditSimulator]:
        """Get all simulator configurations"""
        pass
    
    @abstractmethod
    async def set_active_config(self, config_id: int) -> CreditSimulator:
        """Set a configuration as active (deactivates others)"""
        pass