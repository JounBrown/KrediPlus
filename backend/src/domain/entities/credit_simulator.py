from datetime import datetime
from typing import List, Optional


class CreditSimulator:
    """Credit Simulator domain entity"""
    
    def __init__(
        self,
        id: Optional[int] = None,
        tasa_interes_mensual: float = 0.013,
        monto_minimo: float = 100000,
        monto_maximo: float = 100000000,
        plazos_disponibles: List[int] = None,
        created_at: Optional[datetime] = None
    ):
        self.id = id
        self.tasa_interes_mensual = tasa_interes_mensual
        self.monto_minimo = monto_minimo
        self.monto_maximo = monto_maximo
        self.plazos_disponibles = plazos_disponibles or [6, 12, 18, 24, 36, 48, 60, 72]
        self.created_at = created_at or datetime.now()
    
    def validate(self) -> bool:
        """Validate simulator configuration"""
        if self.tasa_interes_mensual <= 0 or self.tasa_interes_mensual > 0.1:
            return False
        
        if self.monto_minimo <= 0 or self.monto_maximo <= 0:
            return False
        
        if self.monto_minimo >= self.monto_maximo:
            return False
        
        if not self.plazos_disponibles or len(self.plazos_disponibles) == 0:
            return False
        
        if any(plazo <= 0 or plazo > 120 for plazo in self.plazos_disponibles):
            return False
        
        return True
    
    def calculate_monthly_payment(self, monto: float, plazo_meses: int) -> float:
        """Calculate monthly payment using this configuration"""
        if plazo_meses not in self.plazos_disponibles:
            raise ValueError(f"Plazo {plazo_meses} no está disponible")
        
        if monto < self.monto_minimo or monto > self.monto_maximo:
            raise ValueError(f"Monto debe estar entre {self.monto_minimo} y {self.monto_maximo}")
        
        if self.tasa_interes_mensual == 0:
            return monto / plazo_meses
        
        factor = (1 + self.tasa_interes_mensual) ** plazo_meses
        cuota = monto * (self.tasa_interes_mensual * factor) / (factor - 1)
        
        return round(cuota, 2)