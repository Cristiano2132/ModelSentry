import os
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression

# Criação do diretório de dados
os.makedirs("data", exist_ok=True)

print("Iniciando a simulação de dados...")

# 1. Gerar features e target usando make_classification
# 20 features conforme solicitado
X, y = make_classification(
    n_samples=16000, 
    n_features=20, 
    n_informative=15, 
    n_redundant=5,
    weights=[0.8, 0.2], 
    random_state=42
)

# Nomes das colunas
feature_cols = [f'var_{i+1}' for i in range(20)]
df = pd.DataFrame(X, columns=feature_cols)
df['target'] = y

# 2. Dividir em Dev (12.000, representando 1 ano) e OOT (4.000, representando 4 meses)
df_dev = df.iloc[:12000].copy()
df_oot = df.iloc[12000:].copy()

df_dev['amostra'] = 'dev'
df_oot['amostra'] = 'oot'

# 3. Gerar datas para simular 1 ano de Dev e 4 meses de OOT
start_dev = datetime(2023, 1, 1)
dev_dates = [start_dev + timedelta(days=np.random.randint(0, 365)) for _ in range(12000)]
df_dev['data_ref'] = dev_dates

start_oot = datetime(2024, 1, 1)
oot_dates = [start_oot + timedelta(days=np.random.randint(0, 120)) for _ in range(4000)]
df_oot['data_ref'] = oot_dates

# 4. Treinar modelo Logístico no Dev e gerar 'score'
model = LogisticRegression(max_iter=1000)
model.fit(df_dev[feature_cols], df_dev['target'])

# Gerar score (probabilidade da classe 1) para Dev e OOT
df_dev['score'] = model.predict_proba(df_dev[feature_cols])[:, 1]
df_oot['score'] = model.predict_proba(df_oot[feature_cols])[:, 1]

# 5. Juntar tudo num DataFrame único
df_final = pd.concat([df_dev, df_oot], ignore_index=True)

# Converter datetime para string para salvar no SQLite mais facilmente
df_final['data_ref'] = df_final['data_ref'].dt.strftime('%Y-%m-%d')

# 6. Salvar em SQLite
db_path = "data/simulacao.db"
conn = sqlite3.connect(db_path)
df_final.to_sql('model_data', conn, index=False, if_exists='replace')
conn.close()

print(f"Simulação concluída! Dados salvos em {db_path}")
print(f"Total de registros: {len(df_final)}")
print(f"Registros DEV: {len(df_dev)}")
print(f"Registros OOT: {len(df_oot)}")
print(f"Colunas: {df_final.columns.tolist()}")
