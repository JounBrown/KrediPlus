import enum
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, ForeignKey, Boolean, Enum
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .connection import Base


class ApplicationModel(Base):
    """SQLAlchemy model for loan applications (maps to 'LoanApplication' table)"""
    __tablename__ = "LoanApplication"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    name = Column(Text, nullable=False)
    cedula = Column(Text, nullable=False)
    convenio = Column(Text, nullable=True)
    telefono = Column(Text, nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)


class ClientModel(Base):
    """SQLAlchemy model for clients (maps to 'Client' table)"""
    __tablename__ = "Client"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    nombre_completo = Column(Text, nullable=False)
    cedula = Column(Text, nullable=False, unique=True)
    email = Column(Text, nullable=False)
    telefono = Column(Text, nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    direccion = Column(Text, nullable=False)
    info_adicional = Column(JSON, nullable=True)
    
    # Relationship with credits and documents
    credits = relationship("CreditModel", back_populates="client")
    documents = relationship("ClientDocumentModel", back_populates="client")


class CreditModel(Base):
    """SQLAlchemy model for credits (maps to 'Credit' table)"""
    __tablename__ = "Credit"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    monto_aprobado = Column(Float, nullable=False)
    plazo_meses = Column(Integer, nullable=False)
    tasa_interes = Column(Float, nullable=False)
    estado = Column(Text, nullable=False, default="pendiente")
    fecha_desembolso = Column(Date, nullable=True)
    client_id = Column(Integer, ForeignKey("Client.id"), nullable=False)
    
    # Relationship with client and documents
    client = relationship("ClientModel", back_populates="credits")
    documents = relationship("ClientDocumentModel", back_populates="credit")


class AdminModel(Base):
    """SQLAlchemy model for admins (maps to 'Admin' table)"""
    __tablename__ = "Admin"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    email = Column(Text, nullable=False, unique=True)
    name = Column(Text, nullable=False)


class CreditSimulatorModel(Base):
    """SQLAlchemy model for credit simulator (maps to 'Credit_simulator' table)"""
    __tablename__ = "Credit_simulator"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    tasa_interes_mensual = Column(Float, nullable=False)
    monto_minimo = Column(Float, nullable=False)
    monto_maximo = Column(Float, nullable=False)
    plazos_disponibles = Column(JSON, nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)


class DocumentTypeEnum(enum.Enum):
    """Enum for document types"""
    CEDULA_FRENTE = "CEDULA_FRENTE"
    CEDULA_REVERSO = "CEDULA_REVERSO"
    COMPROBANTE_INGRESOS = "COMPROBANTE_INGRESOS"
    CERTIFICADO_LABORAL = "CERTIFICADO_LABORAL"
    SOLICITUD_CREDITO_FIRMADA = "SOLICITUD_CREDITO_FIRMADA"
    PAGARE_FIRMADO = "PAGARE_FIRMADO"
    COMPROBANTE_DOMICILIO = "COMPROBANTE_DOMICILIO"
    EXTRACTO_BANCARIO = "EXTRACTO_BANCARIO"
    OTRO = "OTRO"


class ClientDocumentModel(Base):
    """SQLAlchemy model for client documents (maps to 'client_documents' table)"""
    __tablename__ = "client_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    file_name = Column(Text, nullable=False)
    storage_path = Column(Text, nullable=False)
    document_type = Column(Enum(DocumentTypeEnum, name="document_type_enum"), nullable=False)
    client_id = Column(Integer, ForeignKey("Client.id"), nullable=False)
    credit_id = Column(Integer, ForeignKey("Credit.id"), nullable=True)
    
    # Relationships
    client = relationship("ClientModel", back_populates="documents")
    credit = relationship("CreditModel", back_populates="documents")