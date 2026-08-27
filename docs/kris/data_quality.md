# Dimensão de Qualidade de Dados (Data Quality)

Esta dimensão aloca-se no grupo de indicadores Qualitativos, focando na sanidade da estrutura dos dados.

## `MissingValuesKRI`

Verifica a proporção de valores faltantes/nulos (Null/NaN) no dataset.

- **Proporcionalidade de Risco**: O risco cresce conforme o percentual de dados nulos avança em direção aos limites.
- **Parâmetros**:
  - `warning_threshold` (Padrão: 0.05): Taxa de aviso (começa a marcar como Médio risco).
  - `fail_threshold` (Padrão: 0.10): Taxa de falha (marca risco Alto/Crítico).
  
## `DataTypeKRI`

Verifica a integridade dos tipos de colunas, garantindo que colunas esperadas como numéricas não estejam repletas de strings ou objetos mistos (Ex: "R$ 10,00").

- **Proporcionalidade de Risco**: Como trata-se de um teste estrutural binário, a aderência gera um score `0` (Muito Baixo). Em casos onde a biblioteca é estendida com contagem de violações, o score cresce para 100 mediante violações do tipo esperado.
