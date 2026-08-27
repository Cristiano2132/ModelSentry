import base64
import io
import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Optional, Any
from modelsentry.core.base import ValidationResult
from modelsentry.viz.plots import plot_kri_summary, plot_risk_matrix, plot_psi_mensal
from modelsentry.core.metadata import load_kpi_metadata
from datetime import datetime
from modelsentry.viz import theme

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Auditoria de Modelo - ModelSentry</title>
    <!-- Mermaid CDN -->
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({{startOnLoad:true}});</script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 40px;
            background-color: {HTML_BG_COLOR};
            color: {HTML_TEXT_COLOR};
        }}
        .container {{
            max-width: 1000px;
            margin: auto;
            background: #fff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .page {{
            margin-bottom: 60px;
            padding-bottom: 40px;
            border-bottom: 3px solid {HTML_TABLE_BORDER};
        }}
        h1 {{
            color: {HTML_TEXT_COLOR};
            border-bottom: 2px solid {HTML_HEADER_COLOR};
            padding-bottom: 10px;
        }}
        h2 {{
            color: {HTML_TEXT_COLOR};
            margin-top: 30px;
            background-color: {HTML_TABLE_BORDER};
            padding: 10px;
            border-radius: 4px;
        }}
        h3 {{
            color: {HTML_HEADER_COLOR};
        }}
        .metadata-card {{
            background-color: {HTML_CARD_BG};
            border: 1px solid {HTML_TABLE_BORDER};
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            line-height: 1.6;
            display: flex;
            justify-content: space-between;
        }}
        .score-card-container {{
            display: flex;
            gap: 20px;
            margin: 20px 0;
        }}
        .score-card {{
            flex: 1;
            text-align: center;
            background-color: {HTML_CARD_BG};
            border: 1px solid {HTML_TABLE_BORDER};
            padding: 20px;
            border-radius: 8px;
        }}
        .score-value {{
            font-size: 2.5em;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            margin-bottom: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid {HTML_TABLE_BORDER};
        }}
        th {{
            background-color: {HTML_TABLE_HEAD_BG};
            color: {HTML_TABLE_HEAD_TEXT};
        }}
        tr:hover {{
            background-color: {HTML_BG_COLOR};
        }}
        .chart-container {{
            text-align: center;
            margin: 20px 0;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .mermaid-container {{
            margin: 20px 0;
            padding: 15px;
            background: {HTML_CARD_BG};
            border: 1px solid {HTML_TABLE_BORDER};
            border-radius: 4px;
            text-align: center;
        }}
        .storytelling {{
            background-color: {HTML_CARD_BG};
            padding: 15px;
            border-left: 5px solid {HTML_HEADER_COLOR};
            margin: 20px 0;
            font-style: italic;
            border-top: 1px solid {HTML_TABLE_BORDER};
            border-right: 1px solid {HTML_TABLE_BORDER};
            border-bottom: 1px solid {HTML_TABLE_BORDER};
        }}
    </style>
</head>
<body>
    <div class="container">
        
        <!-- PÁGINA 1: Sumário Executivo -->
        <div class="page" id="page-1">
            <h1>Relatório de Auditoria - ModelSentry</h1>
            
            <div class="metadata-card">
                <div>
                    <strong>Modelo:</strong> {model_name} <br>
                    <strong>Data:</strong> {val_date}
                </div>
                <div>
                    <strong>Amostra:</strong> {sources_str}
                </div>
            </div>
            
            <h2>Sumário Executivo</h2>
            
            <div class="score-card-container">
                <div class="score-card">
                    <h3>Risco Global</h3>
                    <div class="score-value" style="color: {global_color};">{global_risk}</div>
                </div>
                <div class="score-card">
                    <h3>Risco Qualitativo</h3>
                    <div class="score-value" style="color: {quali_color};">{quali_risk}</div>
                </div>
                <div class="score-card">
                    <h3>Risco Quantitativo</h3>
                    <div class="score-value" style="color: {quanti_color};">{quanti_risk}</div>
                </div>
            </div>

            <div class="chart-container">
                <h3>Posição Atual do Modelo (Matriz de Risco)</h3>
                <img src="data:image/png;base64,{risk_matrix_b64}" alt="Matriz de Risco">
            </div>
            
            <h3>Hierarquia da Validação</h3>
            <div class="mermaid-container">
                <div class="mermaid">
{mermaid_graph}
                </div>
            </div>
        </div>

        <!-- PÁGINA 2: Detalhamento Qualitativo -->
        <div class="page" id="page-2">
            <h2>Detalhamento Qualitativo</h2>
            
            <div class="storytelling">
                A dimensão qualitativa avalia aspectos como qualidade de dados, explicabilidade e governança.
                Abaixo apresentamos o consolidado das subdimensões qualitativas e o detalhamento dos KPIs avaliados.
            </div>
            
            <div class="chart-container">
                {quali_summary_chart}
            </div>
            
            <h3>Tabela de Indicadores Qualitativos</h3>
            <table>
                <tr>
                    <th>Sub-dimensão</th>
                    <th>KPI</th>
                    <th>Valor Base</th>
                    <th>Nota (Risco)</th>
                    <th>Nível</th>
                </tr>
                {quali_table_rows}
            </table>
            
            {quali_details}
        </div>

        <!-- PÁGINA 3: Detalhamento Quantitativo -->
        <div class="page" id="page-3">
            <h2>Detalhamento Quantitativo</h2>
            
            <div class="storytelling">
                A dimensão quantitativa avalia a performance estatística, métricas de estabilidade e calibração do modelo.
            </div>
            
            <div class="chart-container">
                {quanti_summary_chart}
            </div>
            
            <h3>Tabela de Indicadores Quantitativos</h3>
            <table>
                <tr>
                    <th>Sub-dimensão</th>
                    <th>KPI</th>
                    <th>Valor Base</th>
                    <th>Nota (Risco)</th>
                    <th>Nível</th>
                </tr>
                {quanti_table_rows}
            </table>
            
            {quanti_details}
        </div>

        <!-- PÁGINA 4: Referência de KPIs -->
        <div class="page" id="page-4">
            <h2>Referência de KPIs Utilizados</h2>
            
            <div class="storytelling">
                Glossário contendo as definições, raciocínio de cálculo e lógicas de limites de todos os KPIs disponíveis no report, extraído do dicionário de metadados.
            </div>
            
            <table>
                <tr>
                    <th>Dimensão</th>
                    <th>Sub-dimensão</th>
                    <th>KRI Name</th>
                    <th>Descrição & Raciocínio de Cálculo</th>
                    <th>Lógica de Threshold (Nota)</th>
                </tr>
                {reference_table_rows}
            </table>
        </div>

    </div>
</body>
</html>
"""

def _fig_to_b64(fig) -> str:
    if fig is None:
        return ""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def _get_color(score: float) -> str:
    if score <= 20: return theme.RISK_COLORS['level_1']
    elif score <= 40: return theme.RISK_COLORS['level_2']
    elif score <= 60: return theme.RISK_COLORS['level_3']
    elif score <= 80: return theme.RISK_COLORS['level_4']
    return theme.RISK_COLORS['level_5']

def _generate_mermaid_graph(suite: Any, results: List[ValidationResult]) -> str:
    lines = ["graph TD"]
    lines.append("    Global[\"Risco Global\"]")
    idx = 1
    
    hierarchy = {}
    for r in results:
        dim = r.dimension
        sub = r.sub_dimension
        if dim not in hierarchy:
            hierarchy[dim] = {}
        if sub not in hierarchy[dim]:
            hierarchy[dim][sub] = []
        hierarchy[dim][sub].append(r)
        
    weights_config = getattr(suite, 'custom_weights', {}) or {}
    
    # Calculate dimension weights
    configured_dims = [d for d in hierarchy.keys() if d in weights_config and isinstance(weights_config[d], dict) and 'weight' in weights_config[d]]
    unconfigured_dims = [d for d in hierarchy.keys() if d not in configured_dims]
    sum_configured_dim_weights = sum(weights_config[d]['weight'] for d in configured_dims)
    remaining_dim_weight = max(0.0, 1.0 - sum_configured_dim_weights)
    default_dim_weight = remaining_dim_weight / len(unconfigured_dims) if unconfigured_dims else 0.0

    for dim, subs in hierarchy.items():
        dim_id = f"D{idx}"
        idx += 1
        dim_w = weights_config.get(dim, {}).get('weight', default_dim_weight) if isinstance(weights_config.get(dim), dict) else default_dim_weight
        lines.append(f"    Global -->|\"{dim_w*100:.0f}%\"| {dim_id}[\"{dim}\"]")
        
        dim_config = weights_config.get(dim, {})
        sub_weights_config = dim_config.get('sub_dimensions', {}) if isinstance(dim_config, dict) else {}
        
        configured_subs = [s for s in subs.keys() if s in sub_weights_config and isinstance(sub_weights_config[s], dict) and 'weight' in sub_weights_config[s]]
        unconfigured_subs = [s for s in subs.keys() if s not in configured_subs]
        sum_configured_sub_weights = sum(sub_weights_config[s]['weight'] for s in configured_subs)
        remaining_sub_weight = max(0.0, 1.0 - sum_configured_sub_weights)
        default_sub_weight = remaining_sub_weight / len(unconfigured_subs) if unconfigured_subs else 0.0
        
        for sub, kris in subs.items():
            sub_id = f"S{idx}"
            idx += 1
            sub_w = sub_weights_config.get(sub, {}).get('weight', default_sub_weight) if isinstance(sub_weights_config.get(sub), dict) else default_sub_weight
            lines.append(f"    {dim_id} -->|\"{sub_w*100:.0f}%\"| {sub_id}[\"{sub}\"]")
            
            sub_config = sub_weights_config.get(sub, {}) if isinstance(sub_weights_config, dict) else {}
            kri_weights_config = sub_config.get('kris', {}) if isinstance(sub_config, dict) else {}
            
            configured_kris = [k for k in kris if k.name in kri_weights_config]
            unconfigured_kris = [k for k in kris if k.name not in kri_weights_config]
            sum_configured_kri_weights = sum(kri_weights_config[k.name] for k in configured_kris)
            remaining_kri_weight = max(0.0, 1.0 - sum_configured_kri_weights)
            default_kri_weight = remaining_kri_weight / len(unconfigured_kris) if unconfigured_kris else 0.0
            
            for k in kris:
                kri_id = f"K{idx}"
                idx += 1
                kri_w = kri_weights_config.get(k.name, default_kri_weight)
                lines.append(f"    {sub_id} -->|\"{kri_w*100:.0f}%\"| {kri_id}[\"{k.name}\"]")
                
    return "\n".join(lines)

def generate_html_report(suite: Any, results: List[ValidationResult], global_risk: float, output_path: str, metadata: Optional[dict] = None):
    
    if not metadata:
        metadata = {}
    
    # Exec Summary Metadata
    model_name = metadata.get("model_name", "Modelo Desconhecido")
    val_date = metadata.get("validation_date", datetime.now().strftime("%Y-%m-%d %H:%M"))
    sources_str = ", ".join(metadata.get("data_sources", [])) if metadata.get("data_sources") else "N/A"
    
    # Calculate Quali and Quanti average risks
    quali_results = [r for r in results if r.dimension == "Qualitativa"]
    quanti_results = [r for r in results if r.dimension == "Quantitativa"]
    
    quali_risk = sum(r.risk_score for r in quali_results) / len(quali_results) if quali_results else 0.0
    quanti_risk = sum(r.risk_score for r in quanti_results) / len(quanti_results) if quanti_results else 0.0
    
    # Matriz de Risco
    fig_matrix = plot_risk_matrix(quali_risk, quanti_risk)
    risk_matrix_b64 = _fig_to_b64(fig_matrix)
    
    # Process Quali Results
    fig_quali_summ = plot_kri_summary(quali_results, title="Risco Qualitativo por Indicador")
    quali_summary_chart = f'<img src="data:image/png;base64,{_fig_to_b64(fig_quali_summ)}">' if fig_quali_summ else ""
    
    quali_table_rows = ""
    quali_details = ""
    for r in quali_results:
        val_str = f"{r.value:.4f}" if isinstance(r.value, (int, float)) else str(r.value)
        quali_table_rows += f"<tr><td>{r.sub_dimension}</td><td>{r.name}</td><td>{val_str}</td><td>{r.risk_score:.2f}</td><td>{r.risk_level}</td></tr>"
        quali_details += f"<h4>{r.name}</h4><p>Risco avaliado: <b>{r.risk_score:.2f} ({r.risk_level})</b>. Valor base: {val_str}</p>"
        # Se quiser renderizar tabelas extras (opcional)
        for tname, tdf in r.tables.items():
            quali_details += f"<h5>{tname}</h5>{tdf.to_html(index=False)}"
            
    # Process Quanti Results
    fig_quanti_summ = plot_kri_summary(quanti_results, title="Risco Quantitativo por Indicador")
    quanti_summary_chart = f'<img src="data:image/png;base64,{_fig_to_b64(fig_quanti_summ)}">' if fig_quanti_summ else ""
    
    quanti_table_rows = ""
    quanti_details = ""
    for r in quanti_results:
        val_str = f"{r.value:.4f}" if isinstance(r.value, (int, float)) else str(r.value)
        quanti_table_rows += f"<tr><td>{r.sub_dimension}</td><td>{r.name}</td><td>{val_str}</td><td>{r.risk_score:.2f}</td><td>{r.risk_level}</td></tr>"
        quanti_details += f"<h4>{r.name}</h4><p>Risco avaliado: <b>{r.risk_score:.2f} ({r.risk_level})</b>. Valor médio/base: {val_str}</p>"
        
        # Injetar os detalhes de DEV e OOT pro PSI se existirem
        if "dev_stability_risk" in r.details:
            quanti_details += f"<ul><li>Risco Estabilidade DEV: {r.details['dev_stability_risk']:.2f}</li>"
            quanti_details += f"<li>Risco Estabilidade OOT: {r.details['oot_stability_risk']:.2f}</li></ul>"
        
        if r.name == "Population Stability Index (PSI) KRI":
            fig_psi = plot_psi_mensal(r)
            if fig_psi:
                quanti_details += f'<div class="chart-container"><img src="data:image/png;base64,{_fig_to_b64(fig_psi)}"></div>'
                
        for tname, tdf in r.tables.items():
            quanti_details += f"<h5>{tname}</h5>{tdf.to_html(index=False, classes='dataframe')}"

    # Process References from Metadata
    try:
        df_meta = load_kpi_metadata()
        reference_table_rows = ""
        for _, row in df_meta.iterrows():
            reference_table_rows += f"<tr><td>{row['dimension']}</td><td>{row['sub_dimension']}</td><td>{row['kri_name']}</td>"
            reference_table_rows += f"<td>{row['description']}<br><br><i>Raciocínio:</i> {row['calculation_rationale']}</td>"
            reference_table_rows += f"<td>{row['threshold_logic']}</td></tr>"
    except Exception as e:
        reference_table_rows = f"<tr><td colspan='5'>Erro ao carregar dicionário de metadados: {e}</td></tr>"

    html_content = HTML_TEMPLATE.format(
        model_name=model_name,
        val_date=val_date,
        sources_str=sources_str,
        global_risk=f"{global_risk:.2f}",
        global_color=_get_color(global_risk),
        quali_risk=f"{quali_risk:.2f}",
        quali_color=_get_color(quali_risk),
        quanti_risk=f"{quanti_risk:.2f}",
        quanti_color=_get_color(quanti_risk),
        risk_matrix_b64=risk_matrix_b64,
        mermaid_graph=_generate_mermaid_graph(suite, results),
        quali_summary_chart=quali_summary_chart,
        quali_table_rows=quali_table_rows,
        quali_details=quali_details,
        quanti_summary_chart=quanti_summary_chart,
        quanti_table_rows=quanti_table_rows,
        quanti_details=quanti_details,
        reference_table_rows=reference_table_rows,
        HTML_BG_COLOR=theme.HTML_BG_COLOR,
        HTML_TEXT_COLOR=theme.HTML_TEXT_COLOR,
        HTML_HEADER_COLOR=theme.HTML_HEADER_COLOR,
        HTML_CARD_BG=theme.HTML_CARD_BG,
        HTML_TABLE_HEAD_BG=theme.HTML_TABLE_HEAD_BG,
        HTML_TABLE_HEAD_TEXT=theme.HTML_TABLE_HEAD_TEXT,
        HTML_TABLE_BORDER=theme.HTML_TABLE_BORDER
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    return output_path
