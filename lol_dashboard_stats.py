import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image

# Configuración
GAME_NAME = 'tukaan'
TAG_LINE = 'tukan'
PLAYER_NAME = 'DONATELL0'  # Cambia esto si es necesario
csv_file = f'match_history_{GAME_NAME}_{TAG_LINE}.csv'
icon_path = 'assets/campeones'
graph_path = os.path.join('assets', f"{GAME_NAME}_{TAG_LINE}_{PLAYER_NAME}")  # Carpeta con gráficos

# Verificar que el CSV existe
if not os.path.exists(csv_file):
    print(f" No se encontró el archivo {csv_file}")
    exit()

# Cargar datos
data = pd.read_csv(csv_file)

# Normalizar nombres de columnas
data.columns = data.columns.str.strip()

# Verificar si la columna 'Invocador' existe
if 'Invocador' not in data.columns:
    print(" La columna 'Invocador' no existe en el CSV.")
    print(f"Columnas disponibles: {data.columns}")
    exit()

# Filtrar datos del jugador
player_data = data[data['Invocador'] == PLAYER_NAME]

if player_data.empty:
    print(f" No se encontraron partidas para {PLAYER_NAME}.")
    exit()

# Crear carpeta de salida
output_dir = os.path.join('assets', 'reportes')
os.makedirs(output_dir, exist_ok=True)

# Archivo PDF de salida
pdf_filename = os.path.join(output_dir, f'dashboard_{PLAYER_NAME}.pdf')

# Crear documento PDF
with PdfPages(pdf_filename) as pdf:
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis("off")

    # Columnas clave a mostrar
    columns_to_show = [
        'Match ID', 'Campeón', 'K/D/A', 'Daño total', 'Oro acumulado', 'Wards Puestos'
    ]
    
    # Redondear valores numéricos
    table_data = player_data[columns_to_show].copy()
    table_data['Daño total'] = table_data['Daño total'].astype(int)
    table_data['Oro acumulado'] = table_data['Oro acumulado'].astype(int)
    table_data['Wards Puestos'] = table_data['Wards Puestos'].astype(int)

    # Crear tabla con pandas
    table = ax.table(cellText=table_data.values, colLabels=table_data.columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.2, 1.2)  # Ajustar tamaño

    ax.set_title(f" Estadísticas Generales de {PLAYER_NAME}", fontsize=14, fontweight="bold", pad=20)
    pdf.savefig(fig)
    plt.close(fig)

    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis("off")

    ax.set_title(f" Campeones Jugados por {PLAYER_NAME}", fontsize=14, fontweight="bold")

    
    players_file = 'assets/reportes/players.txt'

    def agregar_jugador(nombre):
        if not os.path.exists(players_file):
            with open(players_file, 'w') as file:
                file.write(nombre + '\n')
        else:
            with open(players_file, 'r') as file:
                jugadores = file.read().splitlines()
            if nombre not in jugadores:
                with open(players_file, 'a') as file:
                    file.write(nombre + '\n')

    
    agregar_jugador(PLAYER_NAME)

    # Cargar los íconos de los campeones jugados
    champion_icons = []
    for champion in player_data['Campeón'].unique():
        champion_icon = os.path.join(icon_path, f"{champion}.png")
        if os.path.exists(champion_icon):
            img = Image.open(champion_icon)
            champion_icons.append((champion, img))

    # Mostrar los íconos en la página
    x_offset = 50
    y_offset = 200
    for champion, img in champion_icons:
        ax.text(x_offset, y_offset, champion, fontsize=10, fontweight="bold")
        ax.figure.figimage(img, xo=x_offset, yo=y_offset - 80, alpha=0.9, resize=True)
        x_offset += 120  # Espaciado entre imágenes

    pdf.savefig(fig)
    plt.close(fig)

    
    graph_files = [
        "kda_por_partida.png",
        "dano_total_por_partida.png",
        "oro_acumulado_por_partida.png",
        "objetivos_por_partida.png",
        "dano_a_objetivos_por_partida.png",
        "wards_y_vision_score_por_partida.png",
        "pings_por_partida.png",
        "experiencia_y_minions_por_partida.png",
        "tiempo_muerto_por_partida.png",
    ]

    for graph in graph_files:
        graph_path_full = os.path.join(graph_path, graph)
        if os.path.exists(graph_path_full):
            fig, ax = plt.subplots(figsize=(8, 6))
            img = Image.open(graph_path_full)
            ax.imshow(img)
            ax.axis("off")
            ax.set_title(graph.replace("_", " ").replace(".png", "").capitalize(), fontsize=12, fontweight="bold")
            pdf.savefig(fig)
            plt.close(fig)

    print(f" Dashboard guardado en {pdf_filename}")
