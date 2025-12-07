import math
from typing import Optional
from datetime import datetime
from src.application.dtos.credit_simulator_dtos import (
    SimulateCreditRequest,
    SimulateCreditResponse,
    SimulatorConfigResponse,
    CreateSimulatorConfigRequest,
    UpdateSimulatorConfigRequest
)
from src.domain.ports.credit_simulator_repository import CreditSimulatorRepositoryPort
from src.domain.entities.credit_simulator import CreditSimulator


class CreditSimulatorService:
    """Service for credit simulation operations"""
    
    def __init__(self, simulator_repository: CreditSimulatorRepositoryPort):
        self._simulator_repository = simulator_repository
    
    async def simulate_credit(self, request: SimulateCreditRequest) -> SimulateCreditResponse:
        """
        Simulate a credit with the given parameters
        
        Args:
            request: SimulateCreditRequest with amount and term
            
        Returns:
            SimulateCreditResponse with calculated payment details
        """
        
        # Obtener configuración activa de la base de datos
        config = await self._get_active_config()
        
        # Validar que el monto esté en el rango permitido
        if request.monto < config.monto_minimo or request.monto > config.monto_maximo:
            raise ValueError(f"El monto debe estar entre {config.monto_minimo:,} y {config.monto_maximo:,}")
        
        # Validar que el plazo esté permitido
        if request.plazo_meses not in config.plazos_disponibles:
            raise ValueError(f"Plazo debe ser uno de: {config.plazos_disponibles}")
        
        # Calcular cuota mensual usando la fórmula de anualidad
        cuota_mensual = self._calcular_cuota_mensual(
            request.monto, 
            config.tasa_interes_mensual, 
            request.plazo_meses
        )
        
        # Calcular totales
        total_a_pagar = cuota_mensual * request.plazo_meses
        total_intereses = total_a_pagar - request.monto
        
        return SimulateCreditResponse(
            monto_solicitado=request.monto,
            plazo_meses=request.plazo_meses,
            tasa_interes_mensual=config.tasa_interes_mensual,
            cuota_mensual=cuota_mensual,
            total_a_pagar=total_a_pagar,
            total_intereses=total_intereses
        )
    
    async def get_all_simulator_configs(self) -> list[SimulatorConfigResponse]:
        """
        Get all simulator configurations
        
        Returns:
            List of all simulator configurations (empty list if none exist)
        """
        configs = await self._simulator_repository.get_all()
        
        return [
            SimulatorConfigResponse(
                id=config.id,
                tasa_interes_mensual=config.tasa_interes_mensual,
                monto_minimo=config.monto_minimo,
                monto_maximo=config.monto_maximo,
                plazos_disponibles=config.plazos_disponibles,
                is_active=config.is_active
            )
            for config in configs
        ]
    
    async def update_simulator_config(self, request: CreateSimulatorConfigRequest) -> SimulatorConfigResponse:
        """
        Create new simulator configuration
        
        Args:
            request: CreateSimulatorConfigRequest with new configuration
            
        Returns:
            SimulatorConfigResponse with created configuration
        """
        # Crear nueva configuración
        new_config = CreditSimulator(
            tasa_interes_mensual=request.tasa_interes_mensual,
            monto_minimo=request.monto_minimo,
            monto_maximo=request.monto_maximo,
            plazos_disponibles=request.plazos_disponibles,
            is_active=request.is_active
        )
        
        # Validar configuración
        if not new_config.validate():
            raise ValueError("Configuración inválida")
        
        # Guardar en base de datos
        created_config = await self._simulator_repository.create(new_config)
        
        return SimulatorConfigResponse(
            id=created_config.id,
            tasa_interes_mensual=created_config.tasa_interes_mensual,
            monto_minimo=created_config.monto_minimo,
            monto_maximo=created_config.monto_maximo,
            plazos_disponibles=created_config.plazos_disponibles,
            is_active=created_config.is_active
        )
    
    async def modify_simulator_config(self, config_id: int, request: UpdateSimulatorConfigRequest) -> SimulatorConfigResponse:
        """
        Modify existing simulator configuration (partial updates allowed)
        
        Args:
            config_id: ID of the configuration to modify
            request: UpdateSimulatorConfigRequest with updated configuration (only provided fields will be updated)
            
        Returns:
            SimulatorConfigResponse with updated configuration
        """
        # Obtener configuración existente
        existing_config = await self._simulator_repository.get_by_id(config_id)
        if not existing_config:
            raise ValueError(f"Configuración con ID {config_id} no encontrada")
        
        # Crear configuración actualizada usando valores existentes como base
        # Nota: is_active se mantiene igual, no se puede cambiar via PUT
        updated_config = CreditSimulator(
            id=config_id,
            tasa_interes_mensual=request.tasa_interes_mensual if request.tasa_interes_mensual is not None else existing_config.tasa_interes_mensual,
            monto_minimo=request.monto_minimo if request.monto_minimo is not None else existing_config.monto_minimo,
            monto_maximo=request.monto_maximo if request.monto_maximo is not None else existing_config.monto_maximo,
            plazos_disponibles=request.plazos_disponibles if request.plazos_disponibles is not None else existing_config.plazos_disponibles,
            is_active=existing_config.is_active,  # Siempre mantiene el valor actual
            created_at=existing_config.created_at
        )
        
        # Validar que monto_maximo > monto_minimo
        if updated_config.monto_maximo <= updated_config.monto_minimo:
            raise ValueError("El monto máximo debe ser mayor al monto mínimo")
        
        # Validar configuración
        if not updated_config.validate():
            raise ValueError("Configuración inválida")
        
        # Actualizar en base de datos
        modified_config = await self._simulator_repository.update(updated_config)
        
        return SimulatorConfigResponse(
            id=modified_config.id,
            tasa_interes_mensual=modified_config.tasa_interes_mensual,
            monto_minimo=modified_config.monto_minimo,
            monto_maximo=modified_config.monto_maximo,
            plazos_disponibles=modified_config.plazos_disponibles,
            is_active=modified_config.is_active
        )
    
    def _calcular_cuota_mensual(self, monto: float, tasa_mensual: float, plazo_meses: int) -> float:
        """
        Calculate monthly payment using annuity formula
        
        Formula: Cuota = P × [r × (1 + r)^n] / [(1 + r)^n - 1]
        
        Args:
            monto: Loan principal amount
            tasa_mensual: Monthly interest rate (decimal)
            plazo_meses: Number of monthly payments
            
        Returns:
            Monthly payment amount
        """
        if tasa_mensual == 0:
            return monto / plazo_meses  # No interest case
        
        # Calculate using annuity formula
        factor = (1 + tasa_mensual) ** plazo_meses
        cuota = monto * (tasa_mensual * factor) / (factor - 1)
        
        return round(cuota, 2)
    
    async def _get_active_config(self) -> CreditSimulator:
        """Get the currently active configuration"""
        config = await self._simulator_repository.get_active_config()
        
        if config is None:
            raise ValueError("No existe una configuración activa. Debe activar una configuración primero.")
        
        return config
    
    async def validate_simulation_parameters(self, monto: float, plazo_meses: int) -> dict:
        """
        Validate simulation parameters and return validation result
        
        Args:
            monto: Loan amount to validate
            plazo_meses: Term in months to validate
            
        Returns:
            Dictionary with validation results
        """
        config = await self._get_active_config()
        errors = []
        
        if monto < config.monto_minimo:
            errors.append(f"El monto mínimo es {config.monto_minimo:,}")
        
        if monto > config.monto_maximo:
            errors.append(f"El monto máximo es {config.monto_maximo:,}")
        
        if plazo_meses not in config.plazos_disponibles:
            errors.append(f"Plazos disponibles: {config.plazos_disponibles}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "monto_valido": config.monto_minimo <= monto <= config.monto_maximo,
            "plazo_valido": plazo_meses in config.plazos_disponibles
        }
    
    async def activate_config(self, config_id: int) -> SimulatorConfigResponse:
        """
        Activate a specific simulator configuration
        
        Args:
            config_id: ID of the configuration to activate
            
        Returns:
            SimulatorConfigResponse with activated configuration
        """
        # Verificar que la configuración existe
        config = await self._simulator_repository.get_by_id(config_id)
        if not config:
            raise ValueError(f"Configuración con ID {config_id} no encontrada")
        
        # Activar la configuración (esto desactiva automáticamente las otras)
        activated_config = await self._simulator_repository.set_active_config(config_id)
        
        return SimulatorConfigResponse(
            id=activated_config.id,
            tasa_interes_mensual=activated_config.tasa_interes_mensual,
            monto_minimo=activated_config.monto_minimo,
            monto_maximo=activated_config.monto_maximo,
            plazos_disponibles=activated_config.plazos_disponibles,
            is_active=activated_config.is_active
        )