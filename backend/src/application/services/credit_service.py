from typing import List, Optional
from datetime import datetime
from src.domain.entities.credit import Credit, CreditStatus
from src.domain.ports.credit_repository import CreditRepositoryPort
from src.application.dtos.credit_dtos import (
    CreateCreditRequest,
    UpdateCreditRequest,
    CreditResponse
)


class CreditService:
    """Service for credit operations"""
    
    def __init__(self, credit_repository: CreditRepositoryPort):
        self._credit_repository = credit_repository
    
    async def create_credit(self, request: CreateCreditRequest) -> CreditResponse:
        """Create a new credit"""
        
        # Create domain entity
        credit = Credit(
            id=None,
            client_id=request.client_id,
            monto_aprobado=request.monto_aprobado,
            plazo_meses=request.plazo_meses,
            tasa_interes=request.tasa_interes,
            estado=CreditStatus.EN_ESTUDIO.value,  # Default status
            fecha_desembolso=request.fecha_desembolso,
            created_at=datetime.now()
        )
        
        # Save to repository
        try:
            created_credit = await self._credit_repository.create(credit)
            
            return CreditResponse(
                id=created_credit.id,
                client_id=created_credit.client_id,
                monto_aprobado=created_credit.monto_aprobado,
                plazo_meses=created_credit.plazo_meses,
                tasa_interes=created_credit.tasa_interes,
                estado=created_credit.estado,
                fecha_desembolso=created_credit.fecha_desembolso,
                created_at=created_credit.created_at
            )
            
        except Exception as e:
            raise Exception(f"Error al crear el crédito: {str(e)}")
    
    async def get_credit_by_id(self, credit_id: int) -> Optional[CreditResponse]:
        """Get credit by ID"""
        credit = await self._credit_repository.get_by_id(credit_id)
        if not credit:
            return None
        
        return CreditResponse(
            id=credit.id,
            client_id=credit.client_id,
            monto_aprobado=credit.monto_aprobado,
            plazo_meses=credit.plazo_meses,
            tasa_interes=credit.tasa_interes,
            estado=credit.estado,
            fecha_desembolso=credit.fecha_desembolso,
            created_at=credit.created_at
        )
    
    async def update_credit(self, credit_id: int, request: UpdateCreditRequest) -> CreditResponse:
        """Update credit information"""
        
        # Get existing credit
        credit = await self._credit_repository.get_by_id(credit_id)
        if not credit:
            raise ValueError(f"Crédito con ID {credit_id} no encontrado")
        
        # Update fields if provided
        if request.monto_aprobado is not None:
            credit.monto_aprobado = request.monto_aprobado
        if request.plazo_meses is not None:
            credit.plazo_meses = request.plazo_meses
        if request.tasa_interes is not None:
            credit.tasa_interes = request.tasa_interes
        if request.estado is not None:
            credit.estado = request.estado.value if hasattr(request.estado, 'value') else request.estado
        if request.fecha_desembolso is not None:
            credit.fecha_desembolso = request.fecha_desembolso
        
        try:
            updated_credit = await self._credit_repository.update(credit)
            
            return CreditResponse(
                id=updated_credit.id,
                client_id=updated_credit.client_id,
                monto_aprobado=updated_credit.monto_aprobado,
                plazo_meses=updated_credit.plazo_meses,
                tasa_interes=updated_credit.tasa_interes,
                estado=updated_credit.estado,
                fecha_desembolso=updated_credit.fecha_desembolso,
                created_at=updated_credit.created_at
            )
            
        except Exception as e:
            raise Exception(f"Error al actualizar el crédito: {str(e)}")
    
    async def delete_credit(self, credit_id: int) -> bool:
        """Delete credit"""
        try:
            # Check if credit exists
            credit = await self._credit_repository.get_by_id(credit_id)
            if not credit:
                return False
            
            return await self._credit_repository.delete(credit_id)
            
        except Exception as e:
            raise Exception(f"Error al eliminar el crédito: {str(e)}")
    
    async def get_credits_by_client(self, client_id: int) -> List[CreditResponse]:
        """Get all credits for a specific client"""
        try:
            credits = await self._credit_repository.get_by_client_id(client_id)
            
            return [
                CreditResponse(
                    id=credit.id,
                    client_id=credit.client_id,
                    monto_aprobado=credit.monto_aprobado,
                    plazo_meses=credit.plazo_meses,
                    tasa_interes=credit.tasa_interes,
                    estado=credit.estado,
                    fecha_desembolso=credit.fecha_desembolso,
                    created_at=credit.created_at
                )
                for credit in credits
            ]
            
        except Exception as e:
            raise Exception(f"Error al obtener créditos del cliente: {str(e)}")