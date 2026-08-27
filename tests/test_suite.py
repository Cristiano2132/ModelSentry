import pytest
import pandas as pd
from modelsentry.core.suite import ValidationSuite
from modelsentry.core.base import ValidationResult
from modelsentry.dimensions.quantitative.performance import AUCROC_KRI

@pytest.fixture
def dummy_data():
    """Cria um dataframe falso para os testes estruturais."""
    return pd.DataFrame({
        'var1': [1, 2, 3],
        'amostra': ['dev', 'dev', 'oot'],
        'target': [1, 0, 1],
        'score': [0.9, 0.1, 0.8],
        'data_ref': ['2023-01-01', '2023-02-01', '2024-01-01']
    })

def test_validation_suite_initialization(dummy_data):
    """Testa se a suite é inicializada corretamente."""
    suite = ValidationSuite(
        df=dummy_data,
        date_col='data_ref',
        sample_col='amostra',
        target_col='target',
        score_col='score',
        features=['var1']
    )
    
    assert suite.df.equals(dummy_data)
    assert suite.config['date_col'] == 'data_ref'
    assert len(suite.tests) == 0

def test_add_kri_and_run(dummy_data):
    """Testa se conseguimos adicionar um KRI e rodar a validação."""
    suite = ValidationSuite(
        df=dummy_data,
        date_col='data_ref',
        sample_col='amostra',
        target_col='target',
        score_col='score',
        features=['var1']
    )
    
    kri = AUCROC_KRI(min_passed=0.70)
    suite.add_test(kri)
    
    assert len(suite.tests) == 1
    
    results = suite.run()
    
    assert len(results) == 1
    assert isinstance(results[0], ValidationResult)
    assert results[0].name == "AUC-ROC KRI"
    assert results[0].risk_level == "Médio"
    assert results[0].value == 0.75

def test_hierarchical_weights():
    # Simulando resultados
    res1 = ValidationResult("KRI_1", 1.0, 40.0, "Qualitativa", "Data Quality")
    res2 = ValidationResult("KRI_2", 1.0, 60.0, "Qualitativa", "Data Quality")
    # Qualitativa -> Data Quality KRI_1 e KRI_2
    
    res3 = ValidationResult("KRI_3", 1.0, 80.0, "Quantitativa", "Performance")
    res4 = ValidationResult("KRI_4", 1.0, 100.0, "Quantitativa", "Performance") 
    res5 = ValidationResult("KRI_5", 1.0, 20.0, "Quantitativa", "Stability")
    
    # Global default: todas as notas são tiradas por média igualitária
    suite = ValidationSuite(pd.DataFrame(), 'd', 's', 't', 'sc', [])
    global_risk = suite.calculate_global_risk([res1, res2, res3, res4, res5])
    # Quali DQ avg: (40+60)/2 = 50 -> Quali = 50
    # Quanti Perf avg: (80+100)/2 = 90. Stability = 20. Quanti = (90+20)/2 = 55
    # Global = (50+55)/2 = 52.5
    assert global_risk == 52.5
    
    # Custom weights
    custom_weights = {
        "Qualitativa": {
            "weight": 0.2
            # Sem sub_dimensions (Data Quality divide por igual = 100%)
            # Sem kris (KRI_1 e KRI_2 dividem 50/50, média = 50)
            # Quali final = 50.0
        },
        "Quantitativa": {
            "weight": 0.8,
            "sub_dimensions": {
                "Performance": {
                    "weight": 0.75,
                    "kris": {
                        "KRI_3": 0.8,
                        "KRI_4": 0.2
                    }
                    # Perf = 80*0.8 + 100*0.2 = 64 + 20 = 84.0
                },
                "Stability": {
                    "weight": 0.25
                    # Stability = 20.0
                }
            }
            # Quanti final = 84.0*0.75 + 20.0*0.25 = 63.0 + 5.0 = 68.0
        }
    }
    # Global = (50*0.2 + 68*0.8) / 1.0 = 10 + 54.4 = 64.4
    
    suite2 = ValidationSuite(pd.DataFrame(), 'd', 's', 't', 'sc', [], custom_weights=custom_weights)
    global_risk2 = suite2.calculate_global_risk([res1, res2, res3, res4, res5])
    
    assert global_risk2 == 64.4

def test_calculate_global_risk_empty():
    suite = ValidationSuite(pd.DataFrame(), 'd', 's', 't', 'sc', [])
    assert suite.calculate_global_risk([]) == 0.0
