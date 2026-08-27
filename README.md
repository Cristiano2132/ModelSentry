# ModelSentry

ModelSentry é uma biblioteca em Python focada na validação de modelos de Machine Learning (foco inicial em Regressão Logística). 
A biblioteca permite montar uma suíte de validação com testes customizados baseados em Key Risk Indicators (KRIs), divididos em dimensões Qualitativas e Quantitativas.

## Características Principais

*   **Foco no Pandas:** A entrada primária da biblioteca é um DataFrame Pandas contendo todos os dados necessários (features, target, predições, datas).
*   **Modularidade:** A arquitetura permite registrar e configurar apenas os KRIs desejados.
*   **Dimensões:**
    *   **Qualitativa:** Foco em testes de dados (Data Quality).
    *   **Quantitativa:** Foco na performance do modelo, estabilidade ao longo do tempo e metodologia.

## Estrutura do Projeto

O projeto utiliza o `uv` como gerenciador de dependências.

*   `src/modelsentry/`: Contém o código-fonte principal da biblioteca.
    *   `core/`: Abstrações principais (`ValidationSuite`, `KRI`, `ValidationResult`).
    *   `dimensions/`: Implementações dos testes separados por dimensões (Qualitativa, Quantitativa).
*   `tests/`: Testes unitários para validar a estrutura da biblioteca.
*   `simulacao.py`: Script para simular o processo de modelagem e salvar os dados no SQLite.
*   `data/`: Diretório para armazenar o banco SQLite simulado.

## Instalação e Configuração

Pré-requisitos: `uv` instalado no ambiente.

```bash
uv sync
```

## Como Usar (Exemplo de API)

```python
import pandas as pd
from modelsentry.core.suite import ValidationSuite
from modelsentry.dimensions.quantitative.performance import DiscriminationKRI

# Carregar os dados
df = pd.read_csv("meus_dados.csv")

# Instanciar a suite com a configuração do dataframe
suite = ValidationSuite(
    df=df,
    date_col='data_ref',
    sample_col='amostra', # 'dev' ou 'oot'
    target_col='target',
    score_col='score',
    features=['var1', 'var2', 'var3']
)

# Adicionar KRIs
suite.add_test(DiscriminationKRI(min_passed=0.70))

# Executar
resultados = suite.run()
```
