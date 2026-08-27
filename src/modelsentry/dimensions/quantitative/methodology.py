from typing import Any, Dict
import pandas as pd
from modelsentry.core.base import KRI, ValidationResult

class VIF_KRI(KRI):
    """
    KRI Quantitativo (Metodologia): Calcula o Variance Inflation Factor (VIF).
    Verifica se há multicolinearidade alta entre as variáveis do modelo.
    (Implementação Dummy)
    """
    def __init__(self, max_vif: float = 5.0):
        super().__init__(
            name="Variance Inflation Factor (VIF) KRI",
            description="Avalia a multicolinearidade entre as features preditivas.",
            dimension="Quantitativa",
            sub_dimension="Methodology"
        )
        self.max_vif = max_vif
        
    def evaluate(self, df: pd.DataFrame, config: Dict[str, Any]) -> ValidationResult:
        simulated_max_vif = 3.2
        
        # Mapeamento do VIF para risco (proporcional ao max_vif permitido)
        t4 = self.max_vif
        t3 = self.max_vif * 0.8
        t2 = self.max_vif * 0.5
        t1 = self.max_vif * 0.2

        if simulated_max_vif <= t1:
            risk_score = (simulated_max_vif / t1) * 20.0 if t1 > 0 else 0.0
        elif simulated_max_vif <= t2:
            risk_score = 20.0 + ((simulated_max_vif - t1) / (t2 - t1)) * 20.0
        elif simulated_max_vif <= t3:
            risk_score = 40.0 + ((simulated_max_vif - t2) / (t3 - t2)) * 20.0
        elif simulated_max_vif <= t4:
            risk_score = 60.0 + ((simulated_max_vif - t3) / (t4 - t3)) * 20.0
        else:
            diff = simulated_max_vif - t4
            risk_score = min(100.0, 80.0 + (diff / (self.max_vif * 0.5)) * 20.0)
            
        return ValidationResult(
            name=self.name,
            value=simulated_max_vif,
            risk_score=round(risk_score, 2),
            dimension=self.dimension,
            sub_dimension=self.sub_dimension,
            details={"max_vif_allowed": self.max_vif}
        )
