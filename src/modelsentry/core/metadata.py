import os
import pandas as pd
from typing import Dict, Any

DEFAULT_METADATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'data', 'kpi_metadata.csv')

DEFAULT_KPIS = [
    {
        "kri_name": "Missing Values KRI",
        "dimension": "Qualitativa",
        "sub_dimension": "Data Quality",
        "description": "Avalia o percentual de valores nulos (missing) nas features.",
        "calculation_rationale": "Soma de valores nulos dividida pelo total de observações. Se o percentual de missing for muito alto, a qualidade dos dados está comprometida.",
        "threshold_logic": "risk_score aumenta proporcionalmente conforme o fail_threshold (limite crítico)."
    },
    {
        "kri_name": "Population Stability Index (PSI) KRI",
        "dimension": "Quantitativa",
        "sub_dimension": "Stability",
        "description": "Avalia a estabilidade populacional das features e scores.",
        "calculation_rationale": "O PSI mede o deslocamento da distribuição de uma variável. É avaliada a distribuição de todos os dados de dev vs cada safra de dev, e dev vs cada safra oot. A nota final é a média das notas.",
        "threshold_logic": "PSI <= 0.10: Risco 0 (Nota 100). 0.10 < PSI <= 0.20: Risco 95 (Nota 5). PSI > 0.20: Risco 100 (Nota 0)."
    },
    {
        "kri_name": "AUC-ROC KRI",
        "dimension": "Quantitativa",
        "sub_dimension": "Performance",
        "description": "Mede a capacidade de ordenação (discriminação) do modelo.",
        "calculation_rationale": "A Área sob a Curva ROC (AUC) em amostras out-of-time ou out-of-sample.",
        "threshold_logic": "risk_score aumenta proporcionalmente quando o AUC cai abaixo do min_passed."
    }
]

def initialize_kpi_metadata(path: str = DEFAULT_METADATA_PATH):
    """Cria o arquivo csv com os metadados default caso não exista."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df = pd.DataFrame(DEFAULT_KPIS)
    df.to_csv(path, index=False)
    
def load_kpi_metadata(path: str = DEFAULT_METADATA_PATH) -> pd.DataFrame:
    """Carrega os metadados dos KRIs."""
    if not os.path.exists(path):
        initialize_kpi_metadata(path)
    return pd.read_csv(path)

if __name__ == "__main__":
    initialize_kpi_metadata()
    print(f"Metadata inicializado em {DEFAULT_METADATA_PATH}")
