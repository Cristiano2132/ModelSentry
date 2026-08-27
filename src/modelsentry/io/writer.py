import sqlite3
import pandas as pd
from typing import List
from modelsentry.core.base import ValidationResult

def save_summary_to_sqlite(results: List[ValidationResult], db_path: str, table_name: str = "validation_summary"):
    """Salva o resumo consolidado dos resultados em uma tabela."""
    data = []
    for r in results:
        data.append({
            "kri_name": r.name,
            "value": r.value,
            "risk_score": r.risk_score,
            "risk_level": r.risk_level
        })
        
    df = pd.DataFrame(data)
    with sqlite3.connect(db_path) as conn:
        df.to_sql(table_name, conn, if_exists="append", index=False)

def save_artifacts_to_csv(results: List[ValidationResult], output_dir: str):
    """Salva as tabelas intermediárias (artifacts) como arquivos CSV."""
    import os
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for r in results:
        for table_name, df in r.tables.items():
            # Salva cada tabela intermediária com um nome descritivo. Ex: KRI_name_table_name.csv
            safe_name = r.name.replace(" ", "_").replace("/", "_")
            file_name = f"{safe_name}_{table_name}.csv"
            file_path = os.path.join(output_dir, file_name)
            df.to_csv(file_path, index=False)

def save_artifacts_to_sqlite(results: List[ValidationResult], db_path: str):
    """Salva as tabelas intermediárias (artifacts) no SQLite."""
    with sqlite3.connect(db_path) as conn:
        for r in results:
            for table_name, df in r.tables.items():
                # Salva cada tabela intermediária com um nome descritivo.
                safe_name = r.name.replace(" ", "_").replace("/", "_")
                full_table_name = f"{safe_name}_{table_name}"
                df.to_sql(full_table_name, conn, if_exists="replace", index=False)
