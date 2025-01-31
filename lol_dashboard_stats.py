import os
from PIL import Image
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Configuración del backend de Matplotlib
plt.switch_backend('Agg')

# Configuración
GAME_NAME = 'Naxeron'
TAG_LINE = 'LAS'
PLAYER_NAME = 'Naxeron'
csv_file = os.path.join('assets', f"{GAME_NAME}_{TAG_LINE}_{PLAYER_NAME}", 'datos_filtrados.csv')
icon_path = 'assets/campeones'
graphs_path = os.path.join('assets', f"{GAME_NAME}_{TAG_LINE}_{PLAYER_NAME}")

if not os.path.exists(csv_file):
    print(f"No se encontró el archivo {csv_file}")
    exit()

data = pd.read_csv(csv_file)
data.columns = data.columns.str.strip()

if 'Invocador' not in data.columns:
    print("La columna 'Invocador' no existe en el CSV.")
    print(f"Columnas disponibles: {data.columns}")
    exit()

player_data = data[data['Invocador'] == PLAYER_NAME].copy()
if player_data.empty:
    print(f"No se encontraron partidas para {PLAYER_NAME}.")
    exit()

# Filtrar los datos del rival directo
enemy_data = data[data['Invocador'] != PLAYER_NAME]

# Asegurarse de que los índices coincidan
enemy_data = enemy_data.set_index(player_data.index)

# Crear columna de victoria o derrota
player_data.loc[:, 'Resultado'] = np.where(player_data['Equipo'] == player_data['Equipo Ganador'], 'Victoria', 'Derrota')

# Crear carpeta de salida
output_dir = os.path.join('assets', 'reportes')
os.makedirs(output_dir, exist_ok=True)

# Archivo PDF de salida
pdf_filename = os.path.join(output_dir, f'dashboard_{PLAYER_NAME}.pdf')

# Función para formatear los datos del jugador y del enemigo
def format_data(player_value, enemy_value):
    return f"{player_value}\n\n{enemy_value}"

# Crear documento PDF
with PdfPages(pdf_filename) as pdf:
    columns_to_show = [
        'Match ID', 'Rol', 'Campeón', 'K/D/A', 'Daño total', 'Oro acumulado', 
        'Wards Puestos', 'Vision Score', 'Total Minions', 'Resultado'
    ]
    
    # Crear tabla con pandas
    table_data = pd.DataFrame()
    table_data['Match ID'] = player_data['Match ID']
    table_data['Rol'] = player_data['Rol']
    table_data['Campeón'] = player_data['Campeón'] + '\nvs\n' + enemy_data['Campeón'].values
    table_data['K/D/A'] = player_data.apply(lambda row: format_data(row['K/D/A'], enemy_data.loc[row.name, 'K/D/A']), axis=1)
    table_data['Daño total'] = player_data.apply(lambda row: format_data(row['Daño total'], enemy_data.loc[row.name, 'Daño total']), axis=1)
    table_data['Oro acumulado'] = player_data.apply(lambda row: format_data(row['Oro acumulado'], enemy_data.loc[row.name, 'Oro acumulado']), axis=1)
    table_data['Wards Puestos'] = player_data.apply(lambda row: format_data(row['Wards Puestos'], enemy_data.loc[row.name, 'Wards Puestos']), axis=1)
    table_data['Vision Score'] = player_data.apply(lambda row: format_data(row['Vision Score'], enemy_data.loc[row.name, 'Vision Score']), axis=1)
    table_data['Total Minions'] = player_data.apply(lambda row: format_data(row['Total Minions'], enemy_data.loc[row.name, 'Total Minions']), axis=1)
    table_data['Resultado'] = player_data['Resultado']
    
    rows_per_page = 20
    total_pages = (len(table_data) + rows_per_page - 1) // rows_per_page
    
    for i in range(total_pages):
        fig, ax = plt.subplots(figsize=(14, 8))  # Hacer la figura más chica
        ax.axis("off")
        page_data = table_data.iloc[i * rows_per_page:(i + 1) * rows_per_page]
        table = ax.table(cellText=page_data.values, colLabels=page_data.columns, cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 3.6)  # Ajustar la escala de la tabla para hacerla más alta
        
        # Ajustar el ancho de las columnas específicas
        for key, cell in table.get_celld().items():
            if key[1] == 0:  # Match ID
                cell.set_width(0.2)
            else:
                cell.set_width(0.1)
        
        
        ax.set_title(f"Estadísticas Generales de {PLAYER_NAME} (Página {i + 1})", fontsize=14, fontweight="bold", pad=30)
        pdf.savefig(fig)
        plt.close(fig)

    # Cargar los íconos de los campeones jugados
    champion_icons = []
    for champion in player_data['Campeón'].unique():
        champion_icon = os.path.join(icon_path, f"{champion}.jpg")
        if os.path.exists(champion_icon):
            img = Image.open(champion_icon)
            img = img.resize((150, 150))  # Redimensionar la imagen a 150x150 píxeles (tres veces más grande que 50x50)
            img_array = np.array(img)  # Convertir la imagen a un array de NumPy
            champion_icons.append((champion, img_array))

    # Crear la figura y el eje para la página de imágenes
    fig, ax = plt.subplots(figsize=(14, 8))  # Ajustar el tamaño de la figura

    # Ocultar el eje de coordenadas
    ax.axis('off')

    # Mostrar los íconos en la página
    x_offset = 10  # Reducir el espacio desde la izquierda
    y_offset = 550  # Reducir el espacio desde el techo
    max_icons_per_row = 5  # Máximo número de íconos por fila
    icon_spacing = 160  # Espaciado entre íconos (150 + 10 de margen)

    for i, (champion, img_array) in enumerate(champion_icons):
        ax.imshow(img_array, extent=(x_offset, x_offset + 150, y_offset - 150, y_offset), aspect='auto')
        ax.text(x_offset + 75, y_offset - 170, champion, fontsize=10, fontweight="bold", ha='center')  # Mover el texto un poco más abajo
        x_offset += icon_spacing  # Espaciado entre imágenes

        # Mover a la siguiente fila si se alcanza el máximo de íconos por fila
        if (i + 1) % max_icons_per_row == 0:
            x_offset = 10
            y_offset -= icon_spacing + 20  # Ajustar el espaciado vertical

    # Ajustar los límites del eje en función del contenido
    ax.set_xlim(0, max(800, x_offset + 150))
    ax.set_ylim(0, max(600, y_offset + 150))

    # Ajustar el tamaño de la figura en función del contenido
    fig.tight_layout()
    pdf.savefig(fig)
    plt.close(fig)

    # Agregar gráficos adicionales
    for graph_file in os.listdir(graphs_path):
        if graph_file.endswith('.png') or graph_file.endswith('.jpg'):
            graph_path = os.path.join(graphs_path, graph_file)
            fig, ax = plt.subplots(figsize=(14, 8))
            img = Image.open(graph_path)
            ax.imshow(img)
            ax.axis('off')
            pdf.savefig(fig)
            plt.close(fig)

players_file = 'assets/reportes/players.txt'
if os.path.exists(players_file):
    with open(players_file, 'r') as f:
        players = f.read().splitlines()
else:
    players = []

if PLAYER_NAME not in players:
    with open(players_file, 'a') as f:
        f.write(f"{PLAYER_NAME}\n")


print(f"Dashboard guardado en {pdf_filename}")
print(f"{PLAYER_NAME} guardado en assets/reportes/players.txt")