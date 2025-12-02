from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import DEBUG, HOST, PORT

app = FastAPI(
    title="KrediPlus RAG Backend",
    description="Backend RAG con Supabase Auth y OpenAI",
    version="0.1.0",
    debug=DEBUG
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
