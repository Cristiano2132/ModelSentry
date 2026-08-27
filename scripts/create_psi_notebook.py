import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

text_cell = "## Validação Manual do PSI\nEste notebook calcula o PSI mensalmente (dev e oot) em relação ao global de dev, sem usar a biblioteca do ModelSentry."

code_cell_1 = """import pandas as pd
import numpy as np
import sqlite3

# Conectar ao banco simulado
conn = sqlite3.connect('../data/simulacao.db')
df = pd.read_sql('SELECT * FROM tb_dados_escorados', conn)
conn.close()

# Mostrar a distribuição de dados por safra
display(df.groupby(['data_ref', 'amostra']).size().reset_index(name='qtd'))
"""

code_cell_2 = """def calculate_psi(expected, actual, bins=10):
    # Calcula decis usando os dados de referência (usando decis quebra em 10 quantis)
    # Aqui estamos usando a função np.histogram que quebra em 10 intervalos iguais (bins=10).
    # Uma implementação clássica de PSI costuma usar decis (quantis). Vamos testar das duas formas!
    
    # Abordagem 1: Bins iguais (a que estamos usando no momento)
    expected_counts, bin_edges = np.histogram(expected.dropna(), bins=bins, density=False)
    actual_counts, _ = np.histogram(actual.dropna(), bins=bin_edges, density=False)
    
    expected_pct = expected_counts / len(expected)
    actual_pct = actual_counts / len(actual)
    
    # Previne divisão por zero e log(0)
    expected_pct = np.where(expected_pct == 0, 0.0001, expected_pct)
    actual_pct = np.where(actual_pct == 0, 0.0001, actual_pct)
    
    psi = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
    return psi * 100 # Em percentual
"""

code_cell_3 = """df_ref = df[df['amostra'] == 'dev']
expected_scores = df_ref['score']

resultados = []
for data_ref, group in df.groupby('data_ref'):
    psi_val = calculate_psi(expected_scores, group['score'])
    amostra_tipo = group['amostra'].iloc[0]
    resultados.append({'data_ref': data_ref, 'amostra': amostra_tipo, 'psi_pct': psi_val})

df_psi = pd.DataFrame(resultados).sort_values('data_ref')
display(df_psi)
"""

code_cell_4 = """# Abordagem 2: Quebrando por Decis Reais (qcut)
# Pode ser que os intervalos iguais do np.histogram estejam deixando bins vazios e inflando o PSI

def calculate_psi_deciles(expected, actual, q=10):
    # Define os decis com base na distribuição de referência
    _, bin_edges = pd.qcut(expected, q=q, retbins=True, duplicates='drop')
    
    # Ajusta os limites para englobar os dados de atual que possam fugir dos extremos
    bin_edges[0] = -np.inf
    bin_edges[-1] = np.inf
    
    # Calcula as distribuições
    expected_counts = pd.cut(expected, bins=bin_edges).value_counts(sort=False).values
    actual_counts = pd.cut(actual, bins=bin_edges).value_counts(sort=False).values
    
    expected_pct = expected_counts / len(expected)
    actual_pct = actual_counts / len(actual)
    
    expected_pct = np.where(expected_pct == 0, 0.0001, expected_pct)
    actual_pct = np.where(actual_pct == 0, 0.0001, actual_pct)
    
    psi = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
    return psi * 100

resultados_decis = []
for data_ref, group in df.groupby('data_ref'):
    psi_val = calculate_psi_deciles(expected_scores, group['score'])
    amostra_tipo = group['amostra'].iloc[0]
    resultados_decis.append({'data_ref': data_ref, 'amostra': amostra_tipo, 'psi_pct_deciles': psi_val})

df_psi_decis = pd.DataFrame(resultados_decis).sort_values('data_ref')
display(df_psi_decis)
"""

nb['cells'] = [
    nbf.v4.new_markdown_cell(text_cell),
    nbf.v4.new_code_cell(code_cell_1),
    nbf.v4.new_code_cell(code_cell_2),
    nbf.v4.new_code_cell(code_cell_3),
    nbf.v4.new_code_cell(code_cell_4)
]

with open('examples/03_manual_psi_validation.ipynb', 'w') as f:
    nbf.write(nb, f)
    
print("Notebook 03_manual_psi_validation.ipynb criado com sucesso.")
