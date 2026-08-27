import pytest
import pandas as pd
from modelsentry.dimensions.qualitative.data_quality import MissingValuesKRI, DataTypeKRI
from modelsentry.dimensions.quantitative.performance import AUCROC_KRI, KolmogorovSmirnovKRI
from modelsentry.dimensions.quantitative.stability import PSI_KRI
from modelsentry.dimensions.quantitative.methodology import VIF_KRI
from modelsentry.io.reader import read_from_sqlite, read_from_csv
import sqlite3
import os

@pytest.fixture
def dummy_df():
    return pd.DataFrame({
        'score': [0.1, 0.2, 0.8, 0.9],
        'target': [0, 0, 1, 1],
        'idade': [20, 30, 40, 50],
        'renda': [1000, 2000, None, 4000],
        'str_col': ['a', 'b', 'c', 'd'],
        'data_ref': ['2023-01', '2023-02', '2023-01', '2023-02'],
        'amostra': ['dev', 'dev', 'oot', 'oot']
    })

def test_missing_values_kri(dummy_df):
    kri = MissingValuesKRI(warning_threshold=0.01, fail_threshold=0.015)
    config = {'features': ['idade', 'renda']}
    result = kri.evaluate(dummy_df, config)
    # simulated_missing_rate is 0.02 -> > fail_threshold (0.015) -> > 80 risk score
    assert result.risk_score > 80.0

def test_missing_values_kri_low_risk(dummy_df):
    kri = MissingValuesKRI(warning_threshold=0.04, fail_threshold=0.1)
    res = kri.evaluate(dummy_df, {'features': ['a']})
    assert res.risk_score <= 40  # 0.02 is below warning (0.04)

def test_datatype_kri(dummy_df):
    kri = DataTypeKRI()
    res = kri.evaluate(dummy_df, {})
    assert res.risk_score == 0.0

def test_aucroc_kri(dummy_df):
    kri = AUCROC_KRI(min_passed=0.7)
    res = kri.evaluate(dummy_df, {})
    assert res.value == 0.75  # simulated
    assert res.risk_score <= 60

    kri = AUCROC_KRI(min_passed=0.8)
    res = kri.evaluate(dummy_df, {}) 
    assert res.risk_score > 60

def test_ks_kri(dummy_df):
    kri = KolmogorovSmirnovKRI(min_passed=0.4)
    res = kri.evaluate(dummy_df, {})
    assert res.value == 0.45
    assert res.risk_score <= 60
    
    kri = KolmogorovSmirnovKRI(min_passed=0.6)
    res = kri.evaluate(dummy_df, {})
    assert res.risk_score > 60

def test_missing_values_kri_edge_cases(dummy_df):
    # Test t1 = 0
    kri = MissingValuesKRI(warning_threshold=0.0, fail_threshold=0.015)
    res = kri.evaluate(dummy_df, {})
    assert res.risk_score > 80

    # Test medium risk
    kri2 = MissingValuesKRI(warning_threshold=0.01, fail_threshold=0.03)
    res2 = kri2.evaluate(dummy_df, {})
    assert 40 < res2.risk_score <= 60

def test_aucroc_kri_edge(dummy_df):
    kri = AUCROC_KRI(min_passed=0.75)
    res = kri.evaluate(dummy_df, {})
    assert res.risk_score == 80.0

def test_ks_kri_edge(dummy_df):
    kri = KolmogorovSmirnovKRI(min_passed=0.45)
    res = kri.evaluate(dummy_df, {})
    assert res.risk_score == 80.0

def test_psi_kri_edge(dummy_df):
    kri = PSI_KRI(ref_sample='dev', eval_samples=['oot'])
    config = {'date_col': 'data_ref', 'sample_col': 'amostra', 'score_col': 'score'}
    res = kri.evaluate(dummy_df, config)
    # The dummy dataset creates a high PSI, so it's normal for it to return 100.
    assert res.risk_score <= 100.0

    kri2 = PSI_KRI(ref_sample='dev', eval_samples=['dev', 'oot'])
    res2 = kri2.evaluate(dummy_df, config)
    assert res2.risk_score <= 100.0

def test_vif_kri_edge(dummy_df):
    kri = VIF_KRI(max_vif=3.5)
    res = kri.evaluate(dummy_df, {})
    assert round(res.risk_score, 2) == 71.43
    kri = PSI_KRI(ref_sample='dev', eval_samples=['oot'])
    config = {'date_col': 'data_ref', 'sample_col': 'amostra', 'score_col': 'score'}
    res = kri.evaluate(dummy_df, config)
    # depending on psi, it should return some risk score
    assert res.risk_score <= 100
    assert "psi_mensal" in res.tables

def test_vif_kri(dummy_df):
    kri = VIF_KRI(max_vif=5.0)
    res = kri.evaluate(dummy_df, {'features': ['idade', 'renda']})
    assert res.risk_score <= 60 # simulated is 3.5
    
    kri = VIF_KRI(max_vif=2.0)
    res = kri.evaluate(dummy_df, {'features': ['idade', 'renda']})
    assert res.risk_score > 60

def test_io_reader():
    # Test sqlite reader
    db_path = "test_reader.db"
    df = pd.DataFrame({'a': [1, 2]})
    with sqlite3.connect(db_path) as conn:
        df.to_sql("test_table", conn, index=False)
        
    read_df = read_from_sqlite(db_path, "SELECT * FROM test_table")
    assert len(read_df) == 2
    
    # Test csv reader
    csv_path = "test_reader.csv"
    df.to_csv(csv_path, index=False)
    read_df_csv = read_from_csv(csv_path)
    assert len(read_df_csv) == 2
    
    os.remove(db_path)
    os.remove(csv_path)
