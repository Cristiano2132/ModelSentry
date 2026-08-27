import pytest
import pandas as pd
from modelsentry.core.suite import ValidationSuite
from modelsentry.dimensions.qualitative.data_quality import MissingValuesKRI, DataTypeKRI
from modelsentry.dimensions.quantitative.performance import AUCROC_KRI, KolmogorovSmirnovKRI
from modelsentry.dimensions.quantitative.stability import PSI_KRI
from modelsentry.dimensions.quantitative.methodology import VIF_KRI

@pytest.fixture
def base_df():
    # DataFrame dummy mínimo para instanciar a suite sem quebrar.
    # Em uma implementação real, conterá os dados do SQLite.
    return pd.DataFrame({
        'var1': [1, 2, 3, 4],
        'amostra': ['dev', 'dev', 'oot', 'oot'],
        'target': [1, 0, 1, 0],
        'score': [0.9, 0.2, 0.8, 0.3],
        'data_ref': ['2023-01-01', '2023-02-01', '2024-01-01', '2024-02-01']
    })

def test_strict_validation_strategy(base_df):
    """
    Testa a capacidade de montar uma estratégia de validação rígida,
    combinando todas as dimensões e vários KRIs com thresholds apertados.
    """
    suite = ValidationSuite(
        df=base_df,
        date_col='data_ref',
        sample_col='amostra',
        target_col='target',
        score_col='score',
        features=['var1']
    )
    
    # Adicionando Dimensão Qualitativa
    suite.add_test(MissingValuesKRI(warning_threshold=0.01, fail_threshold=0.03))
    suite.add_test(DataTypeKRI())
    
    # Adicionando Dimensão Quantitativa (Performance)
    suite.add_test(AUCROC_KRI(min_passed=0.80)) # Exigência alta (nosso dummy retorna 0.75)
    suite.add_test(KolmogorovSmirnovKRI(min_passed=0.40))
    
    # Adicionando Dimensão Quantitativa (Estabilidade)
    suite.add_test(PSI_KRI(ref_sample='dev', eval_samples=['oot']))
    
    # Adicionando Dimensão Quantitativa (Metodologia)
    suite.add_test(VIF_KRI(max_vif=3.0)) # Exigência alta (nosso dummy retorna 3.2)
    
    assert len(suite.tests) == 6
    
    results = suite.run()
    
    # Validações sobre a estratégia:
    assert len(results) == 6
    
    # Procuramos o teste de AUC para garantir que falhou (devido à exigência de 0.80 contra dummy de 0.75)
    auc_result = next(r for r in results if r.name == "AUC-ROC KRI")
    assert auc_result.risk_level == "Crítico"
    
    # Procuramos o teste de VIF para garantir que falhou (exigência 3.0 contra dummy 3.2)
    vif_result = next(r for r in results if r.name == "Variance Inflation Factor (VIF) KRI")
    assert vif_result.risk_level == "Crítico"

def test_quick_validation_strategy(base_df):
    """
    Testa a capacidade de montar uma estratégia leve/rápida,
    selecionando apenas KRIs básicos com thresholds mais relaxados.
    """
    suite = ValidationSuite(
        df=base_df,
        date_col='data_ref',
        sample_col='amostra',
        target_col='target',
        score_col='score',
        features=['var1']
    )
    
    # Adicionando apenas KRIs básicos e thresholds relaxados
    suite.add_test(MissingValuesKRI(warning_threshold=0.10, fail_threshold=0.20))
    suite.add_test(AUCROC_KRI(min_passed=0.60))
    
    assert len(suite.tests) == 2
    
    results = suite.run()
    
    # Com thresholds relaxados, todos devem ter nível de risco "Muito Baixo" com os nossos dummies
    for result in results:
        assert result.risk_level == "Muito Baixo"
