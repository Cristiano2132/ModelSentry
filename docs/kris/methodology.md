# Dimensão Metodológica

Indicadores quantitativos que avaliam a consistência dos parâmetros internos e validações metodológicas do modelo (geralmente aplicável a modelos estatísticos lineares e logísticos).

## `VIF_KRI`

Calcula o Variance Inflation Factor para averiguar altas correlações (multicolinearidade) entre as variáveis, o que desestabiliza coeficientes beta.

- **Proporcionalidade de Risco**: Crescimento direto.
- **Parâmetros**:
  - `max_vif` (Padrão: 5.0).
- **Escala de Risco**:
  - Tendo `max_vif` como baliza (Score = 60/80 - Alto), a biblioteca define dinamicamente os limiares. VIFs na ordem de 0 a `max_vif * 0.2` possuem risco desprezível (Muito Baixo). VIFs estourando consideravelmente o limite resultam em risco Crítico.
