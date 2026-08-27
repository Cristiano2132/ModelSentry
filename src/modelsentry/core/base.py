from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import pandas as pd

@dataclass
class ValidationResult:
    """Resultado da avaliação de um KRI."""
    name: str
    value: float
    risk_score: float  # Score proporcional de 0 (Melhor) a 100 (Pior)
    dimension: str = "Unknown"
    sub_dimension: str = "Unknown"
    details: Dict[str, Any] = field(default_factory=dict)
    tables: Dict[str, 'pd.DataFrame'] = field(default_factory=dict)

    @property
    def risk_level(self) -> str:
        if self.risk_score <= 20:
            return "Muito Baixo"
        elif self.risk_score <= 40:
            return "Baixo"
        elif self.risk_score <= 60:
            return "Médio"
        elif self.risk_score <= 80:
            return "Alto"
        else:
            return "Crítico"

class KRI:
    """Classe base para todos os Key Risk Indicators (testes)."""
    
    def __init__(self, name: str, description: str, dimension: str = "Unknown", sub_dimension: str = "Unknown"):
        self.name = name
        self.description = description
        self.dimension = dimension
        self.sub_dimension = sub_dimension
        
    def evaluate(self, df: pd.DataFrame, config: Dict[str, Any]) -> ValidationResult:
        """
        Executa a lógica de validação.
        A ser implementado pelas subclasses.
        
        Args:
            df: DataFrame contendo os dados.
            config: Dicionário contendo meta-informações das colunas (ex: target_col, score_col).
            
        Returns:
            ValidationResult com o status e valor da métrica.
        """
        raise NotImplementedError("As subclasses devem implementar o método evaluate.")
