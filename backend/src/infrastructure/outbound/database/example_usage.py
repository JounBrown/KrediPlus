"""
Example of how to use the LoanApplication repository with dependency injection
This shows how all the pieces fit together
"""

from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities.loan_application import LoanApplication
from src.application.services.loan_application_service import LoanApplicationService
from src.application.dtos.loan_application_dtos import CreateLoanApplicationRequest
from .loan_application_repository import SupabaseLoanApplicationRepository
from .connection import AsyncSessionLocal


async def example_create_loan_application():
    """Example of creating a loan application"""
    
    # 1. Get database session
    async with AsyncSessionLocal() as db_session:
        try:
            # 2. Create repository implementation (adapter)
            loan_repo = SupabaseLoanApplicationRepository(db_session)
            
            # 3. Create application service (use case)
            loan_service = LoanApplicationService(loan_repo)
            
            # 4. Create request DTO
            request = CreateLoanApplicationRequest(
                name="Juan Pérez",
                cedula="12345678",
                convenio="Empresa ABC",
                telefono="3001234567",
                fecha_nacimiento=date(1990, 5, 15),
                monto_solicitado=5000000.0,
                plazo=24
            )
            
            # 5. Execute use case
            response = await loan_service.create_application(request)
            
            # 6. Commit transaction
            await db_session.commit()
            
            print(f"✅ Solicitud creada: ID {response.id}")
            print(f"   Cuota estimada: ${response.estimated_monthly_payment:,.2f}")
            
            return response
            
        except Exception as e:
            # 7. Rollback on error
            await db_session.rollback()
            print(f"❌ Error: {e}")
            raise


async def example_list_client_applications():
    """Example of listing client applications"""
    
    async with AsyncSessionLocal() as db_session:
        try:
            # Create repository and service
            loan_repo = SupabaseLoanApplicationRepository(db_session)
            loan_service = LoanApplicationService(loan_repo)
            
            # Get applications for a client
            from src.application.dtos.loan_application_dtos import ListClientLoanApplicationsRequest
            
            request = ListClientLoanApplicationsRequest(
                cedula="12345678",
                skip=0,
                limit=10
            )
            
            response = await loan_service.list_client_applications(request)
            
            print(f"✅ Encontradas {response.total} solicitudes")
            for app in response.applications:
                print(f"   - ID {app.id}: {app.estado} - ${app.monto_solicitado:,.2f}")
            
            return response
            
        except Exception as e:
            print(f"❌ Error: {e}")
            raise


async def example_update_application_status():
    """Example of updating application status"""
    
    async with AsyncSessionLocal() as db_session:
        try:
            loan_repo = SupabaseLoanApplicationRepository(db_session)
            loan_service = LoanApplicationService(loan_repo)
            
            # Approve an application
            response = await loan_service.approve_application(application_id=1)
            
            await db_session.commit()
            
            print(f"✅ Solicitud {response.id} aprobada")
            print(f"   Estado: {response.estado}")
            
            return response
            
        except Exception as e:
            await db_session.rollback()
            print(f"❌ Error: {e}")
            raise


# This is how you would use it in FastAPI endpoints:
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db_session, SupabaseLoanApplicationRepository
from ..services import LoanApplicationService

async def get_loan_service(db: AsyncSession = Depends(get_db_session)) -> LoanApplicationService:
    loan_repo = SupabaseLoanApplicationRepository(db)
    return LoanApplicationService(loan_repo)

@app.post("/applications/")
async def create_application(
    request: CreateLoanApplicationRequest,
    loan_service: LoanApplicationService = Depends(get_loan_service)
):
    return await loan_service.create_application(request)
"""