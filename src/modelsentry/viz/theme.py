# Centralização das configurações de paleta de cores e temas visuais
# Estilo Executivo e Acessível (Colorblind-friendly / Okabe-Ito palette)

# HTML Global Colors
HTML_BG_COLOR = '#fcebeb' # Fundo bem claro do pallete
HTML_TEXT_COLOR = '#3c463c' # Charcoal esverdeado escuro
HTML_HEADER_COLOR = '#475571' # Azul principal solicitado
HTML_CARD_BG = '#ffffff'
HTML_TABLE_HEAD_BG = '#475571'
HTML_TABLE_HEAD_TEXT = '#ffffff'
HTML_TABLE_BORDER = '#aebfce' # Azul claro
HTML_LINK_COLOR = '#6592b7'

# Cores base para os gráficos
TEXT_COLOR = '#3c463c'
SPINE_COLOR = '#475571'
GRID_COLOR = '#aebfce'

# Cores para níveis de risco (Barras KRI)
RISK_COLORS = {
    'level_1': '#6aa9a7', # Teal
    'level_2': '#ecd03b', # Amarelo
    'level_3': '#ef683f', # Laranja
    'level_4': '#965959', # Vermelho/Marrom
    'level_5': '#591836'  # Vinho Escuro
}

# Cores para a Matriz de Risco (baseado na soma dos eixos: 2 a 8)
MATRIX_COLORS = {
    2: '#6aa9a7', # Teal
    3: '#a4e0c0', # Mint
    4: '#ecd03b', # Amarelo
    5: '#cc9f2f', # Mostarda Escuro
    6: '#ef683f', # Laranja
    7: '#965959', # Vermelho/Marrom
    8: '#591836'  # Vinho Escuro
}

# Cores para linhas (Evolução PSI)
LINE_COLORS = [
    '#475571', # Azul
    '#ef683f', # Laranja
    '#6aa9a7', # Teal
    '#965959'  # Vermelho/Marrom
]

# Linhas de Alerta
ALERT_ATTENTION = '#ecd03b' # Amarelo
ALERT_CRITICAL = '#965959'  # Vermelho/Marrom
