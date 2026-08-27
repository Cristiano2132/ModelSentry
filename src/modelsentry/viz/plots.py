import matplotlib.pyplot as plt
from typing import List
from modelsentry.core.base import ValidationResult

def plot_kri_summary(results: List[ValidationResult], title="Resumo de Risco dos Indicadores"):
    """Plota um gráfico de barras com os escores de risco de cada KRI."""
    if not results:
        return None
    names = [r.name.replace(" KRI", "") for r in results]
    scores = [r.risk_score for r in results]
    
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Cores condicionais pelo risco (tons clean)
    colors = []
    for score in scores:
        if score <= 20: colors.append('#1e8449')
        elif score <= 40: colors.append('#2ecc71')
        elif score <= 60: colors.append('#f1c40f')
        elif score <= 80: colors.append('#e67e22')
        else: colors.append('#c0392b')

    bars = ax.barh(names, scores, color=colors, height=0.6, alpha=0.85)
    
    # Remove bordas
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Grid sutil contínuo e em ambos os eixos
    ax.grid(axis='both', linestyle='-', alpha=0.2, color='#898989')
    
    ax.set_xlabel('Risk Score (0-100)', fontsize=11, fontweight='bold', color='#475569')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15, color='#333333')
    ax.set_xlim(0, 100)
    
    # Adicionar o valor exato na ponta de cada barra
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2, f'{width:.1f}', 
                va='center', ha='left', fontsize=10, fontweight='bold', color='#475569')

    plt.tight_layout()
    return fig

def plot_risk_matrix(quali_risk: float, quanti_risk: float):
    """Plota uma matriz de risco Quali x Quanti com 4 níveis."""
    # Estilo geral mais limpo
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    
    def get_risk_idx(score: float):
        if score <= 10: return 0      # Muito Baixo
        elif score <= 25: return 1    # Baixo
        elif score <= 40: return 2    # Médio
        else: return 3                # Alto
        
    quali_idx = get_risk_idx(quali_risk)
    quanti_idx = get_risk_idx(quanti_risk)
    
    labels = ['Muito Baixo', 'Baixo', 'Médio', 'Alto']
    
    # Desenhar o grid 4x4
    for i in range(4):
        for j in range(4):
            # Soma dos índices (1-based: i+1 + j+1), varia de 2 a 8
            soma = (i + 1) + (j + 1)
            if soma == 2:
                color = '#1e8449' # Verde escuro
            elif soma == 3:
                color = '#27ae60' # Verde normal
            elif soma == 4:
                color = '#2ecc71' # Verde leve
            elif soma == 5:
                color = '#f1c40f' # Amarelo/Laranja claro
            elif soma == 6:
                color = '#e67e22' # Laranja
            elif soma == 7:
                color = '#e74c3c' # Vermelho leve
            else:
                color = '#c0392b' # Vermelho forte
                
            ax.add_patch(plt.Rectangle((i, j), 1, 1, facecolor=color, alpha=0.8, edgecolor='white', linewidth=2))
            
    # Plotar o ponto do Modelo
    ax.plot(quali_idx + 0.5, quanti_idx + 0.5, 'ko', markersize=16, markeredgecolor='white', markeredgewidth=2, zorder=5)
    ax.text(quali_idx + 0.5, quanti_idx + 0.65, 'Modelo', fontsize=12, fontweight='bold', ha='center', va='bottom', zorder=5)
    
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_xticks([0.5, 1.5, 2.5, 3.5])
    ax.set_yticks([0.5, 1.5, 2.5, 3.5])
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_yticklabels(labels, fontsize=11)
    ax.set_xlabel('Risco Qualitativo', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_ylabel('Risco Quantitativo', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_title('Matriz de Risco do Modelo', fontsize=14, fontweight='bold', pad=15)
    
    # Remove as bordas externas (spines) e grid
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(False)
    
    # Remove os tracinhos dos eixos mas mantém o texto
    ax.tick_params(axis='both', which='both', length=0)
    
    plt.tight_layout()
    return fig

def plot_psi_mensal(result: ValidationResult):
    """Lê a tabela psi_mensal e plota a evolução do PSI."""
    if "psi_mensal" not in result.tables:
        print("Tabela psi_mensal não encontrada neste resultado.")
        return None
        
    df = result.tables["psi_mensal"]
    if df.empty:
        return None
        
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(11, 5))
    samples = df['amostra'].unique()
    
    # Cores inspiradas no case do Nubank
    colors = ['#8A05BE', '#047857', '#e67e22', '#34495e']
    
    for idx, sample in enumerate(samples):
        df_sample = df[df['amostra'] == sample]
        x = [str(s) for s in df_sample['safra']]
        y = df_sample['psi_score']
        ax.plot(x, y, marker='o', linestyle='-', linewidth=2.5, markersize=8, 
                color=colors[idx % len(colors)], label=f'Amostra: {sample}')
        
    ax.axhline(10.0, color='#f1c40f', linestyle='--', linewidth=1.5, alpha=0.9, label='Atenção (PSI=10%)')
    ax.axhline(20.0, color='#c0392b', linestyle='--', linewidth=1.5, alpha=0.9, label='Crítico (PSI=20%)')
    
    # Limpeza visual: eixos mais fortes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#333333')
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['left'].set_color('#333333')
    ax.spines['left'].set_linewidth(1.5)
    
    # Grid contínuo bem levinho
    ax.grid(axis='both', linestyle='-', alpha=0.5, color='#e5e5e5')
    
    # Ticks discretos
    ax.tick_params(axis='both', which='both', length=4, width=1.5, color='#333333')
    
    ax.set_xlabel('Safra', fontsize=11, fontweight='bold', color='#475569', labelpad=10)
    ax.set_ylabel('PSI Score (%)', fontsize=11, fontweight='bold', color='#475569', labelpad=10)
    ax.set_title('Evolução Mensal do PSI', fontsize=14, fontweight='bold', pad=15, color='#333333')
    ax.set_ylim(bottom=0)
    
    # Rotacionar datas no eixo X para evitar sobreposição
    plt.xticks(rotation=45, ha='right', fontsize=10, color='#475569')
    plt.yticks(fontsize=10, color='#475569')
    
    ax.legend(frameon=True, facecolor='white', edgecolor='#cccccc', fontsize=10, loc='best')
    
    plt.tight_layout()
    return fig

