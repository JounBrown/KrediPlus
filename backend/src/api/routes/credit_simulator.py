from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.services.credit_simulator_service import CreditSimulatorService
from src.application.dtos.credit_simulator_dtos import (
    SimulateCreditRequest,
    SimulateCreditResponse,
    SimulatorConfigResponse,
    CreateSimulatorConfigRequest,
    UpdateSimulatorConfigRequest
)
from src.infrastructure.adapters.database.connection import get_db_session
from src.infrastructure.adapters.database.credit_simulator_repository import SupabaseCreditSimulatorRepository

router = APIRouter(prefix="/simulator", tags=["Credit Simulator"])


def get_simulator_service(db: AsyncSession = Depends(get_db_session)) -> CreditSimulatorService:
    """Dependency to get CreditSimulatorService"""
    repository = SupabaseCreditSimulatorRepository(db)
    return CreditSimulatorService(repository)


@router.post("/config", response_model=SimulatorConfigResponse)
async def create_or_update_config(
    config: CreateSimulatorConfigRequest,
    service: CreditSimulatorService = Depends(get_simulator_service)
):
    """
    Create or update simulator configuration
    
    - **tasa_interes_mensual**: Monthly interest rate (decimal, e.g., 0.013 for 1.3%)
    - **monto_minimo**: Minimum loan amount
    - **monto_maximo**: Maximum loan amount  
    - **plazos_disponibles**: Available terms in months (array)
    
    This endpoint allows administrators to configure the credit simulator parameters.
    """
    try:
        return await service.update_simulator_config(config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating simulator config: {str(e)}")


@router.get("/simulate", response_model=SimulateCreditResponse)
async def simulate_credit_get(
    monto: float = Query(..., gt=0, description="Loan amount"),
    plazo_meses: int = Query(..., gt=0, le=120, description="Term in months"),
    service: CreditSimulatorService = Depends(get_simulator_service)
):
    """
    Simulate a credit using GET parameters (alternative to POST)
    
    - **monto**: Loan amount (100,000 - 100,000,000)
    - **plazo_meses**: Term in months (6, 12, 18, 24, 36, 48, 60, 72)
    """
    try:
        request = SimulateCreditRequest(monto=monto, plazo_meses=plazo_meses)
        return await service.simulate_credit(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error simulating credit: {str(e)}")


@router.get("/config", response_model=list[SimulatorConfigResponse])
async def get_all_simulator_configs(
    service: CreditSimulatorService = Depends(get_simulator_service)
):
    """
    Get all simulator configurations
    
    Returns:
    - List of all configurations (empty list if none exist)
    - Each configuration includes: id, interest rate, amounts, and available terms
    """
    try:
        return await service.get_all_simulator_configs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting simulator configs: {str(e)}")


@router.put("/config/{config_id}", response_model=SimulatorConfigResponse)
async def modify_simulator_config(
    config_id: int,
    config: UpdateSimulatorConfigRequest,
    service: CreditSimulatorService = Depends(get_simulator_service)
):
    """
    Modify existing simulator configuration by ID (partial updates allowed)
    
    - **config_id**: ID of the configuration to modify
    - **tasa_interes_mensual**: Monthly interest rate (decimal, e.g., 0.013 for 1.3%) [optional]
    - **monto_minimo**: Minimum loan amount [optional]
    - **monto_maximo**: Maximum loan amount [optional]
    - **plazos_disponibles**: Available terms in months (array) [optional]
    
    You can update only the fields you want to change. Fields not provided will keep their current values.
    """
    try:
        return await service.modify_simulator_config(config_id, config)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error modifying simulator config: {str(e)}")


@router.post("/config/{config_id}/activate", response_model=SimulatorConfigResponse)
async def activate_simulator_config(
    config_id: int,
    service: CreditSimulatorService = Depends(get_simulator_service)
):
    """
    Activate a specific simulator configuration
    
    - **config_id**: ID of the configuration to activate
    
    This will:
    - Set the specified configuration as active (is_active = true)
    - Automatically deactivate all other configurations (is_active = false)
    - The simulator will use this configuration for all credit simulations
    """
    try:
        return await service.activate_config(config_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error activating simulator config: {str(e)}")


@router.delete("/config/{config_id}")
async def delete_simulator_config(
    config_id: int,
    service: CreditSimulatorService = Depends(get_simulator_service)
):
    """
    Delete a simulator configuration
    
    - **config_id**: ID of the configuration to delete
    
    Restrictions:
    - Cannot delete the currently active configuration
    - Must activate another configuration first if you want to delete the active one
    """
    try:
        return await service.delete_config(config_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting simulator config: {str(e)}")


