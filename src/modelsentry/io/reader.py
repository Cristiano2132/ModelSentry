import sqlite3
import pandas as pd

def read_from_sqlite(db_path: str, query: str) -> pd.DataFrame:
    """Lê os dados de um banco SQLite e retorna como DataFrame."""
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(query, conn)
    return df

def read_from_csv(file_path: str, **kwargs) -> pd.DataFrame:
    """Lê os dados de um arquivo CSV e retorna como DataFrame."""
    return pd.read_csv(file_path, **kwargs)
