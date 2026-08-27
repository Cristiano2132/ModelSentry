import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath('src'))

from modelsentry.core.suite import ValidationSuite
from modelsentry.dimensions.quantitative.stability import PSI_KRI
from modelsentry.dimensions.quantitative.performance import AUCROC_KRI, KolmogorovSmirnovKRI
from modelsentry.dimensions.quantitative.methodology import VIF_KRI
from modelsentry.dimensions.qualitative.data_quality import MissingValuesKRI
from modelsentry.reporting.generator import generate_html_report

import sqlite3

conn = sqlite3.connect('data/simulacao.db')
df_simulado = pd.read_sql('SELECT * FROM tb_dados_escorados', conn)
conn.close()

features_list = [col for col in df_simulado.columns if col.startswith('var_')]

suite = ValidationSuite(
    df=df_simulado,
    date_col='data_ref',
    sample_col='amostra',
    target_col='target',
    score_col='score',
    features=features_list
)

suite.add_test(MissingValuesKRI(fail_threshold=0.15))
suite.add_test(KolmogorovSmirnovKRI(min_passed=0.4))
suite.add_test(PSI_KRI(ref_sample='dev', eval_samples=['oot']))
suite.add_test(VIF_KRI(max_vif=5.0))

resultados = suite.run()
global_risk = suite.calculate_global_risk(resultados)

print(f"Risco Global: {global_risk}")

generate_html_report(suite, resultados, global_risk, "report.html")
print("Relatório gerado com sucesso!")
