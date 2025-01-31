import pandas as pd
import os

# Cargar datos
GAME_NAME = 'Naxeron'
TAG_LINE = 'LAS'
csv_file = f'match_history_{GAME_NAME}_{TAG_LINE}.csv'
data = pd.read_csv(csv_file)

# Crear carpeta para reportes
output_dir = os.path.join('assets', 'reportes')
os.makedirs(output_dir, exist_ok=True)

# Función para detectar patrones de juego
def detectar_patrones(df):
    patrones = []
    for player in df['Invocador'].unique():
        player_data = df[df['Invocador'] == player]
        early_deaths = player_data[player_data['Total Time Dead'] < 300]  # Muertes tempranas
        low_vision = player_data[player_data['Wards Puestos'] < 5]  # Baja visión
        
        mensaje = f"{player}: "
        if len(early_deaths) > 3:
            mensaje += "Muere demasiado en los primeros minutos. "
        if len(low_vision) > 3:
            mensaje += "Debe colocar más wards. "
        
        if mensaje != f"{player}: ":
            patrones.append(mensaje)
    
    return patrones

# Detectar patrones en los datos
patrones_encontrados = detectar_patrones(data)

# Guardar el análisis en un archivo
with open(os.path.join(output_dir, 'analisis_patrones.txt'), 'w') as f:
    for patron in patrones_encontrados:
        f.write(patron + '\n')

print("Análisis de patrones guardado en assets/reportes/analisis_patrones.txt")
