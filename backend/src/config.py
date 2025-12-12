import os
from dotenv import load_dotenv

load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", SUPABASE_KEY or SUPABASE_SERVICE_KEY)

# OpenAI Configuration (for future RAG implementation)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "")
if not DATABASE_URL and SUPABASE_URL:
    # Extract database URL from Supabase URL if needed
    DATABASE_URL = SUPABASE_URL.replace("https://", "postgresql://postgres:")

# JWT Configuration (para Supabase Auth)
# Nota: Supabase maneja la expiración automáticamente
JWT_ALGORITHM = "HS256"  # Supabase usa HS256
JWT_AUDIENCE = "authenticated"  # Audience estándar de Supabase

# Server Configuration
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Pagination defaults
DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", "100"))

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS","https://krediplus-frontend.onrender.com,http://localhost:3000,http://localhost:5173").split(",")
