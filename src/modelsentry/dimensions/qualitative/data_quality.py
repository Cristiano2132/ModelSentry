from typing import Any, Dict
import pandas as pd
from modelsentry.core.base import KRI, ValidationResult

class MissingValuesKRI(KRI):
    """
    KRI Qualitativo: Verifica o percentual de dados faltantes (missing).
    (Implementação Dummy)
    """
    def __init__(self, warning_threshold: float = 0.05, fail_threshold: float = 0.10):
        super().__init__(
            name="Missing Values KRI",
            description="Verifica se o percentual de dados nulos nas features excede o aceitável.",
            dimension="Qualitativa",
            sub_dimension="Data Quality"
        )
        self.warning_threshold = warning_threshold
        self.fail_threshold = fail_threshold
        
    def evaluate(self, df: pd.DataFrame, config: Dict[str, Any]) -> ValidationResult:
        # Lógica dummy: Simula que encontrou 2% de missings
        simulated_missing_rate = 0.02
        
        # Calcula limites com base nas thresholds
        t1 = self.warning_threshold / 2.0
        t2 = self.warning_threshold
        t3 = (self.warning_threshold + self.fail_threshold) / 2.0
        t4 = self.fail_threshold

        if simulated_missing_rate <= t1:
            risk_score = (simulated_missing_rate / t1) * 20.0 if t1 > 0 else 0.0
        elif simulated_missing_rate <= t2:
            risk_score = 20.0 + ((simulated_missing_rate - t1) / (t2 - t1)) * 20.0
        elif simulated_missing_rate <= t3:
            risk_score = 40.0 + ((simulated_missing_rate - t2) / (t3 - t2)) * 20.0
        elif simulated_missing_rate <= t4:
            risk_score = 60.0 + ((simulated_missing_rate - t3) / (t4 - t3)) * 20.0
        else:
            diff = simulated_missing_rate - t4
            risk_score = min(100.0, 80.0 + (diff / 0.10) * 20.0)
            
        return ValidationResult(
            name=self.name,
            value=simulated_missing_rate,
            risk_score=round(risk_score, 2),
            dimension=self.dimension,
            sub_dimension=self.sub_dimension,
            details={"fail_threshold": self.fail_threshold}
        )

class DataTypeKRI(KRI):
    """
    KRI Qualitativo: Verifica se os tipos de dados batem com o esperado.
    (Implementação Dummy)
    """
    def __init__(self):
        super().__init__(
            name="Data Type KRI",
            description="Valida integridade dos tipos de dados nas colunas numéricas.",
            dimension="Qualitativa",
            sub_dimension="Data Quality"
        )
        
    def evaluate(self, df: pd.DataFrame, config: Dict[str, Any]) -> ValidationResult:
        return ValidationResult(
            name=self.name,
            value=1.0,  # 1.0 = 100% aderente
            risk_score=0.0,
            dimension=self.dimension,
            sub_dimension=self.sub_dimension
        )
