import requests
import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.stats import gaussian_kde
from requests.utils import quote

# Cargar la clave de API desde un archivo seguro
with open("config.json") as f:
    config = json.load(f)
    API_KEY = config["API_KEY"]

REGION = 'europe'
GAME_NAME = 'EL EKOINOMISTA'
TAG_LINE = 'EUW'
BASE_URL = f'https://{REGION}.api.riotgames.com'

# Obtener el PUUID por Riot ID
def get_puuid_by_riot_id(game_name, tag_line):
    url = f'{BASE_URL}/riot/account/v1/accounts/by-riot-id/{quote(game_name)}/{quote(tag_line)}'
    headers = {'X-Riot-Token': API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['puuid']
    except Exception as e:
        print(f"Error al obtener el PUUID: {e}")
        return None

# Obtener IDs de las últimas partidas
def get_match_ids(puuid, count=10):
    url = f'https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids'
    headers = {'X-Riot-Token': API_KEY}
    params = {'count': count}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error al obtener las partidas: {e}")
        return None

# Obtener detalles de una partida
def get_match_details(match_id):
    url = f'https://{REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}'
    headers = {'X-Riot-Token': API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error al obtener los detalles de la partida: {e}")
        return None

# Obtener detalles del timeline de una partida
def get_match_timeline(match_id):
    url = f'https://{REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline'
    headers = {'X-Riot-Token': API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error al obtener el timeline: {e}")
        return None

# Generar mapa de calor basado en posiciones de un jugador
def generate_heatmap(timeline, participant_id, output_file="heatmap.png"):
    positions = []

    # Extraer las posiciones del jugador del timeline
    for frame in timeline['info']['frames']:
        participant_frame = frame['participantFrames'].get(str(participant_id))
        if participant_frame:
            position = participant_frame.get('position')
            if position:
                positions.append((position['x'], position['y']))

    if not positions:
        print("No se encontraron posiciones para el jugador seleccionado.")
        return

    # Separar las coordenadas X e Y
    x_coords, y_coords = zip(*positions)

    # Aplicar KDE para suavizar los puntos
    xy = np.vstack([x_coords, y_coords])
    density = gaussian_kde(xy)(xy)

    # Crear el gráfico de mapa de calor
    plt.figure(figsize=(10, 8))

    # KDE Plot con barra de color activada
    sns.kdeplot(
        x=x_coords, 
        y=y_coords, 
        cmap="hot", 
        fill=True, 
        levels=50, 
        thresh=0, 
        cbar=True  # Esto activa la barra de color
    )

    plt.title("Mapa de calor de posiciones del jugador")
    plt.xlabel("Coordenada X")
    plt.ylabel("Coordenada Y")

    # Guardar el archivo o mostrar
    if output_file:
        plt.savefig(output_file)
        print(f"Mapa de calor guardado en {output_file}")
    else:
        plt.show()

# Función principal
def main():
    # Obtener PUUID del jugador
    puuid = get_puuid_by_riot_id(GAME_NAME, TAG_LINE)
    if not puuid:
        return

    # Obtener IDs de las últimas partidas
    match_ids = get_match_ids(puuid, count=1)  # Solo obtener la última partida
    if not match_ids:
        return

    match_id = match_ids[0]

    # Obtener detalles de la partida
    match_details = get_match_details(match_id)
    if not match_details:
        return

    # Encontrar el participant_id del jugador
    participant_id = None
    for participant in match_details['info']['participants']:
        if participant['puuid'] == puuid:
            participant_id = participant['participantId']
            break

    if participant_id is None:
        print("No se encontró al jugador en los detalles de la partida.")
        return

    # Obtener timeline de la partida
    timeline = get_match_timeline(match_id)
    if not timeline:
        return

    # Generar el mapa de calor
    generate_heatmap(timeline, participant_id, output_file="heatmap.png")

if __name__ == "__main__":
    main()