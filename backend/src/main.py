from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import DEBUG, HOST, PORT, CORS_ORIGINS
from src.api.routes.loan_applications import router as loan_applications_router
from src.api.routes.clients import router as clients_router
from src.api.routes.credits import router as credits_router
from src.api.routes.credit_simulator import router as credit_simulator_router
from src.api.routes.documents import router as documents_router


app = FastAPI(
    title="KrediPlus RAG Backend",
    description="Backend RAG con Supabase Auth y OpenAI",
    version="0.1.0",
    debug=DEBUG
)

# CORS Configuration - Only allow specific frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(loan_applications_router, prefix="/api/v1")
app.include_router(clients_router, prefix="/api/v1")
app.include_router(credits_router, prefix="/api/v1")
app.include_router(credit_simulator_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "KrediPlus RAG Backend is running",
        "version": "0.1.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG
    )
