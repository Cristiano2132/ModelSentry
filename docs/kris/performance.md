# Dimensão de Performance

Aloca indicadores Quantitativos responsáveis por garantir a força preditiva ou capacidade de ordenação do modelo.

> **Importante**: Nas métricas de performance, valores altos são desejados. Por conta disso, o `risk_score` cresce de maneira **inversamente proporcional** à métrica, de forma que quanto menor for a sua AUC, maior será o Risco.

## `AUCROC_KRI`

Mede a Área sob a Curva ROC (AUC).
- **Parâmetros**: 
  - `min_passed` (Padrão: 0.70).
- **Escala de Risco**: 
  - Baseado no `min_passed`, a métrica cria faixas dinâmicas espaçadas de 0.05 a 0.15 para suavizar o crescimento do risco desde o cenário ideal até as quedas abaixo do mínimo. O que for estritamente abaixo do `min_passed` já é classificado com score superior a 60 (Risco Alto).

## `KolmogorovSmirnovKRI`

Mede a métrica de separação máxima KS.
- **Parâmetros**: 
  - `min_passed` (Padrão: 0.30).
- **Escala de Risco**: 
  - Análogo à AUC, espaçado de forma que métricas consideravelmente acima de `min_passed` sejam avaliadas como Risco Baixo/Muito Baixo, e violações subam para Alto/Crítico.
