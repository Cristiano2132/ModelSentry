# Dimensão de Estabilidade

Aloca indicadores quantitativos que monitoram *Data Drift* ou estabilidade populacional entre a base original de Desenvolvimento (DEV) e a Out-of-Time ou Produção (OOT).

## `PSI_KRI`

Mede o Population Stability Index do escore do modelo, binando as previsões em quantis (ex: decis).
Valores mais altos significam deslocamento intenso (drift).

- **Proporcionalidade de Risco**: Crescimento direto. Quanto maior o PSI, maior o escore de risco.
- **Parâmetros**:
  - `warning_threshold` (Padrão: 0.10).
  - `fail_threshold` (Padrão: 0.25).
- **Escala de Risco**:
  - Se o drift atinge o warning, a biblioteca computa risco equivalente a **Médio**.
  - Passando da marca de fail (0.25), o risco sobe intensamente para o patamar **Alto** a **Crítico**.
