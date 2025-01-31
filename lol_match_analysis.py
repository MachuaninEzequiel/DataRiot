import pandas as pd
import matplotlib.pyplot as plt
import os

# Leer los datos del archivo CSV
GAME_NAME = 'Naxeron'
TAG_LINE = 'LAS'
player_name = 'Naxeron'  # Reemplaza con el nombre del jugador específico
csv_file = f'match_history_{GAME_NAME}_{TAG_LINE}.csv'
data = pd.read_csv(csv_file)

# Imprimir los nombres de las columnas para verificar
print("Columnas disponibles en el DataFrame:")
print(data.columns)

# Filtrar los datos por el jugador específico

player_data = data[data['Invocador'] == player_name].copy()

# Contar la cantidad de partidas disponibles
total_partidas = len(player_data)
print(f"Total de partidas disponibles para {player_name}: {total_partidas}")

# Solicitar al usuario que ingrese el rango de partidas que desea visualizar
start_partida = int(input(f"Ingrese el número de la partida inicial (1 a {total_partidas}): "))
max_end_partida = min(start_partida + 9, total_partidas)
end_partida = int(input(f"Ingrese el número de la partida final (máximo {max_end_partida}): "))

while end_partida > max_end_partida:
    print(f"El número de la partida final no puede ser mayor a {max_end_partida}. Por favor, ingrese nuevamente.")
    end_partida = int(input(f"Ingrese el número de la partida final (máximo {max_end_partida}): "))

# Filtrar los datos según el rango especificado
partidas_seleccionadas = player_data.iloc[start_partida-1:end_partida].copy()

# Asignar roles a los jugadores
roles = ['TOP', 'JUNGLA', 'MID', 'ADC', 'SUPPORT']
data['Rol'] = data.groupby('Match ID').cumcount().map(lambda x: roles[x % 5])

# Filtrar los datos nuevamente para incluir la columna 'Rol'
player_data = data[data['Invocador'] == player_name].copy()
partidas_seleccionadas = player_data.iloc[start_partida-1:end_partida].copy()

# Identificar al oponente con el mismo rol en cada partida
opponent_data = []
for match_id, role in zip(partidas_seleccionadas['Match ID'], partidas_seleccionadas['Rol']):
    opponent = data[(data['Match ID'] == match_id) & (data['Rol'] == role) & (data['Invocador'] != player_name)]
    if not opponent.empty:
        opponent = opponent.iloc[0]
        opponent_data.append(opponent)

# Convertir los datos del oponente a un DataFrame
opponent_df = pd.DataFrame(opponent_data)

# Concatenar los datos del jugador y del oponente verticalmente
combined_data = pd.concat([partidas_seleccionadas, opponent_df], ignore_index=True)

# Crear la carpeta para guardar los gráficos
output_dir = os.path.join('assets', f"{GAME_NAME}_{TAG_LINE}_{player_name}")
os.makedirs(output_dir, exist_ok=True)

# Guardar el DataFrame en un archivo CSV
output_csv = os.path.join(output_dir, 'datos_filtrados.csv')
combined_data.to_csv(output_csv, index=False)
print(f"Datos filtrados guardados en {output_csv}")

# Crear una nueva columna que combine el nombre del campeón y el rol
partidas_seleccionadas.loc[:, 'Campeón y Rol'] = partidas_seleccionadas['Campeón'] + ' (' + partidas_seleccionadas['Rol'] + ')'

# Crear una nueva columna que combine el nombre del campeón, el rol y el ID de la partida
partidas_seleccionadas.loc[:, 'Campeón y Rol por Partida'] = partidas_seleccionadas['Match ID'] + ' - ' + partidas_seleccionadas['Campeón y Rol']

# Crear DataFrames y gráficos

# Gráfico de KDA (Kills/Deaths/Assists)
partidas_seleccionadas.loc[:, 'KDA'] = partidas_seleccionadas['K/D/A'].apply(lambda x: sum(map(int, x.split('/'))))
plt.figure(figsize=(10, 6))
plt.plot(partidas_seleccionadas['Campeón y Rol por Partida'], partidas_seleccionadas['KDA'], marker='o')
plt.title(f'KDA por partida (Partidas {start_partida} a {end_partida})')
plt.xlabel('Campeón y Rol por Partida')
plt.ylabel('KDA')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'kda_por_partida.png'))
plt.show()

# Gráfico de daño total
plt.figure(figsize=(10, 6))
plt.plot(partidas_seleccionadas['Campeón y Rol por Partida'], partidas_seleccionadas['Daño total'], marker='o', color='red')
plt.title(f'Daño total por partida (Partidas {start_partida} a {end_partida})')
plt.xlabel('Campeón y Rol por Partida')
plt.ylabel('Daño total')
plt.xticks(rotation=90)
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'dano_total_por_partida.png'))
plt.show()

# Gráfico de oro acumulado
plt.figure(figsize=(10, 6))
plt.plot(partidas_seleccionadas['Campeón y Rol por Partida'], partidas_seleccionadas['Oro acumulado'], marker='o', color='gold')
plt.title(f'Oro acumulado por partida (Partidas {start_partida} a {end_partida})')
plt.xlabel('Campeón y Rol por Partida')
plt.ylabel('Oro acumulado')
plt.xticks(rotation=90)
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'oro_acumulado_por_partida.png'))
plt.show()

# Gráfico de objetivos del juego (torres, dragones, barones)
plt.figure(figsize=(10, 6))
plt.plot(partidas_seleccionadas['Campeón y Rol por Partida'], partidas_seleccionadas['Torre Destruida'], marker='o', label='Torres')
plt.plot(partidas_seleccionadas['Campeón y Rol por Partida'], partidas_seleccionadas['Dragon Kills'], marker='o', label='Dragones')
plt.plot(partidas_seleccionadas['Campeón y Rol por Partida'], partidas_seleccionadas['Barón Kills'], marker='o', label='Barones')
plt.title(f'Objetivos del juego por partida (Partidas {start_partida} a {end_partida})')
plt.xlabel('Campeón y Rol por Partida')
plt.ylabel('Cantidad')
plt.legend()
plt.xticks(rotation=90)
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'objetivos_por_partida.png'))
plt.show()

# Gráfico de daño a objetivos del juego (torres, dragones, barones)
plt.figure(figsize=(10, 6))
plt.plot(partidas_seleccionadas['Campeón y Rol por Partida'], partidas_seleccionadas['Daño a Torres'], marker='o', label='Daño a Torres')
plt.plot(partidas_seleccionadas['Campeón y Rol por Partida'], partidas_seleccionadas['Daño a Dragones/Barones'], marker='o', label='Daño a Dragones/Barones')
plt.title(f'Daño a objetivos del juego por partida (Partidas {start_partida} a {end_partida})')
plt.xlabel('Campeón y Rol por Partida')
plt.ylabel('Daño')
plt.legend()
plt.xticks(rotation=90)
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'dano_a_objetivos_por_partida.png'))
plt.show()

# Gráfico de wards (colocados, destruidos y vision score)
plt.figure(figsize=(10, 6))
plt.plot(partidas_seleccionadas['Campeón y Rol por Partida'], partidas_seleccionadas['Wards Puestos'], marker='o', label='Wards colocados')
plt.plot(partidas_seleccionadas['Campeón y Rol por Partida'], partidas_seleccionadas['Wards Destruidos'], marker='o', label='Wards destruidos')
plt.plot(partidas_seleccionadas['Campeón y Rol por Partida'], partidas_seleccionadas['Vision Score'], marker='o', label='Vision Score')
plt.title(f'Wards y Vision Score por partida (Partidas {start_partida} a {end_partida})')
plt.xlabel('Campeón y Rol por Partida')
plt.ylabel('Cantidad')
plt.legend()
plt.xticks(rotation=90)
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'wards_y_vision_score_por_partida.png'))
plt.show()

# Gráfico de pings
plt.figure(figsize=(10, 6))
plt.plot(partidas_seleccionadas['Campeón y Rol por Partida'], partidas_seleccionadas['Pings - All In'], marker='o', label='All In')
plt.plot(partidas_seleccionadas['Campeón y Rol por Partida'], partidas_seleccionadas['Pings - Assist Me'], marker='o', label='Assist Me')
plt.plot(partidas_seleccionadas['Campeón y Rol por Partida'], partidas_seleccionadas['Pings - Enemy Missing'], marker='o', label='Enemy Missing')
plt.title(f'Pings por partida (Partidas {start_partida} a {end_partida})')
plt.xlabel('Campeón y Rol por Partida')
plt.ylabel('Cantidad')
plt.legend()
plt.xticks(rotation=90)
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'pings_por_partida.png'))
plt.show()

# Gráfico de experiencia y cantidad de minions
factor = 0.1  # Factor para ajustar la escala de la experiencia
plt.figure(figsize=(10, 6))
plt.plot(partidas_seleccionadas['Campeón y Rol por Partida'], partidas_seleccionadas['Experiencia'] * factor, marker='o', label=f'Experiencia (x{factor})')
plt.plot(partidas_seleccionadas['Campeón y Rol por Partida'], partidas_seleccionadas['Total Minions'], marker='o', label='Total Minions')
plt.title(f'Experiencia y Total Minions por partida (Partidas {start_partida} a {end_partida})')
plt.xlabel('Campeón y Rol por Partida')
plt.ylabel('Cantidad')
plt.legend()
plt.xticks(rotation=90)
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'experiencia_y_minions_por_partida.png'))
plt.show()

# Gráfico de tiempo muerto
plt.figure(figsize=(10, 6))
plt.plot(partidas_seleccionadas['Campeón y Rol por Partida'], partidas_seleccionadas['Total Time Dead'], marker='o', color='purple')
plt.title(f'Tiempo muerto por partida (Partidas {start_partida} a {end_partida})')
plt.xlabel('Campeón y Rol por Partida')
plt.ylabel('Tiempo muerto (s)')
plt.xticks(rotation=90)
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'tiempo_muerto_por_partida.png'))
plt.show()

# Estadísticas descriptivas
stats = partidas_seleccionadas.describe()
# Guardar estadísticas en un archivo CSV
stats.to_csv(os.path.join(output_dir, 'estadisticas_descriptivas.csv'))

print(f"Gráficos y estadísticas generados y guardados en {output_dir} correctamente.")

# Leer las estadísticas descriptivas
stats_file = os.path.join(output_dir, 'estadisticas_descriptivas.csv')
stats_data = pd.read_csv(stats_file, index_col=0)

# Crear gráficos a partir de las estadísticas descriptivas

# Gráfico de media de las estadísticas de daño
plt.figure(figsize=(10, 6))
stats_data.loc['mean', ['Daño total', 'Daño a Torres', 'Daño a Dragones/Barones']].plot(kind='bar', color='skyblue')
plt.title('Media de las estadísticas de daño')
plt.xlabel('Estadística')
plt.ylabel('Valor medio')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'media_estadisticas_dano.png'))
plt.show()

# Gráfico de media de las estadísticas de oro y experiencia
plt.figure(figsize=(10, 6))
stats_data.loc['mean', ['Oro acumulado', 'Experiencia']].plot(kind='bar', color='gold')
plt.title('Media de las estadísticas de oro y experiencia')
plt.xlabel('Estadística')
plt.ylabel('Valor medio')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'media_estadisticas_oro_experiencia.png'))
plt.show()

# Gráfico de media de las estadísticas de objetivos
plt.figure(figsize=(10, 6))
stats_data.loc['mean', ['Torre Destruida', 'Dragon Kills', 'Barón Kills']].plot(kind='bar', color='green')
plt.title('Media de las estadísticas de objetivos')
plt.xlabel('Estadística')
plt.ylabel('Valor medio')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'media_estadisticas_objetivos.png'))
plt.show()

# Gráfico de media de las estadísticas de wards y vision score
plt.figure(figsize=(10, 6))
stats_data.loc['mean', ['Wards Puestos', 'Wards Destruidos', 'Vision Score']].plot(kind='bar', color='purple')
plt.title('Media de las estadísticas de wards y vision score')
plt.xlabel('Estadística')
plt.ylabel('Valor medio')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'media_estadisticas_wards_vision.png'))
plt.show()

# Gráfico de media de las estadísticas de pings
plt.figure(figsize=(10, 6))
stats_data.loc['mean', ['Pings - All In', 'Pings - Assist Me', 'Pings - Enemy Missing']].plot(kind='bar', color='orange')
plt.title('Media de las estadísticas de pings')
plt.xlabel('Estadística')
plt.ylabel('Valor medio')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'media_estadisticas_pings.png'))
plt.show()

# Gráfico de media de las estadísticas de tiempo muerto
plt.figure(figsize=(10, 6))
stats_data.loc['mean', ['Total Time Dead']].plot(kind='bar', color='red')
plt.title('Media de las estadísticas de tiempo muerto')
plt.xlabel('Estadística')
plt.ylabel('Valor medio')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'media_estadisticas_tiempo_muerto.png'))
plt.show()