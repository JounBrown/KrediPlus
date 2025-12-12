from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from src.config import DATABASE_URL

# SQLAlchemy base for models
Base = declarative_base()

# Database engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Disable SQL logging for cleaner output
    pool_pre_ping=True,
    pool_recycle=300
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db_session() -> AsyncSession:
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initialize database tables"""
    # Import models to register them with SQLAlchemy
    from . import models
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)