import os
import sqlite3
import pandas as pd
from modelsentry.core.base import ValidationResult
from modelsentry.io.writer import save_summary_to_sqlite, save_artifacts_to_csv
from modelsentry.viz.plots import plot_kri_summary, plot_psi_mensal

def test_io_and_viz():
    # Setup dummy result with a table
    df_dummy = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
    result = ValidationResult(
        name="Test KRI",
        value=0.5,
        risk_score=50,
        tables={"test_table": df_dummy}
    )
    results = [result]
    
    db_path = "test_temp.db"
    artifacts_dir = "test_temp_artifacts"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    try:
        # Test Writers
        save_summary_to_sqlite(results, db_path)
        save_artifacts_to_csv(results, artifacts_dir)
        
        # Verify db contents
        with sqlite3.connect(db_path) as conn:
            summary = pd.read_sql_query("SELECT * FROM validation_summary", conn)
            assert len(summary) == 1
            assert summary.iloc[0]['risk_score'] == 50
            
        # Verify artifact csv
        file_name = f"{result.name.replace(' ', '_').replace('/', '_')}_test_table.csv"
        csv_path = os.path.join(artifacts_dir, file_name)
        assert os.path.exists(csv_path)
        table_artifact = pd.read_csv(csv_path)
        assert len(table_artifact) == 2
        assert 'a' in table_artifact.columns
            
        # Test Viz (just check if they run without error)
        fig1 = plot_kri_summary(results)
        assert fig1 is not None
        
        # PSI needs specific structure
        result_psi = ValidationResult(
            name="PSI", value=0.1, risk_score=20,
            tables={"psi_mensal": pd.DataFrame({'amostra': ['oot'], 'safra': ['2024-01'], 'psi_score': [0.1], 'risco_kri': [20.0]})},
            details={"warning_threshold": 0.10, "fail_threshold": 0.20}
        )
        fig2 = plot_psi_mensal(result_psi)
        assert fig2 is not None

    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
        import shutil
        if os.path.exists(artifacts_dir):
            shutil.rmtree(artifacts_dir)
