import requests
import json
import csv
import os
from requests.utils import quote

# Cargar la clave de API desde un archivo seguro
with open("config.json") as f:
    config = json.load(f)
    API_KEY = config["API_KEY"]

REGION = 'americas'
GAME_NAME = 'Naxeron'
TAG_LINE = 'LAS'
BASE_URL = f'https://{REGION}.api.riotgames.com'
SEASON = '13'  # Temporada actual

# Obtener el PUUID por Riot ID
def get_puuid_by_riot_id(GAME_NAME, TAG_LINE):
    url = f'{BASE_URL}/riot/account/v1/accounts/by-riot-id/{quote(GAME_NAME)}/{quote(TAG_LINE)}'
    headers = {'X-Riot-Token': API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['puuid']
    except Exception as err:
        print(f"Error al obtener el PUUID: {err}")
        return None


# Obtener la lista de IDs de partidas
def get_match_ids(puuid, count=25):
    url = f'https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids'
    headers = {'X-Riot-Token': API_KEY}
    params = {'count': count}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as err:
        print(f"Error al obtener los IDs de partidas: {err}")
        return None

# Obtener detalles de una partida
def get_match_details(match_id):
    url = f'https://{REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}'
    headers = {'X-Riot-Token': API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as err:
        print(f"Error al obtener los detalles de la partida: {err}")
        return None

# Descargar datos de ítems
def download_item_data():
    url = "https://ddragon.leagueoflegends.com/cdn/13.1.1/data/en_US/item.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['data']
    except Exception as err:
        print(f"Error al descargar los datos de ítems: {err}")
        return None

# Descargar datos de runas
def download_rune_data():
    url = "https://ddragon.leagueoflegends.com/cdn/13.1.1/data/en_US/runesReforged.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as err:
        print(f"Error al descargar los datos de runas: {err}")
        return None

# Obtener el nombre del ítem por su ID
def get_item_name(item_id, item_data):
    return item_data.get(str(item_id), {}).get('name', 'Desconocido')

# Obtener el nombre y subnombre de las runas correctamente
def get_rune_details(participant, rune_data):
    primary_rune_id = participant.get('perk0', 0)  # Keystone
    secondary_tree_id = participant.get('perkSubStyle', 0)  # Subárbol

    primary_rune_name = "Desconocido"
    secondary_tree_name = "Desconocido"

    # Buscar la Keystone en la estructura de runas
    for tree in rune_data:
        for slot in tree['slots']:
            for rune in slot['runes']:
                if rune['id'] == primary_rune_id:
                    primary_rune_name = rune['name']

    # Buscar el nombre del subárbol
    for tree in rune_data:
        if tree['id'] == secondary_tree_id:
            secondary_tree_name = tree['name']

    return f"{primary_rune_name} ({secondary_tree_name})"

# Guardar información en un archivo CSV
def save_to_csv(match_details, item_data, rune_data, csv_file=f'match_history_{GAME_NAME}_{TAG_LINE}.csv'):
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Encabezados actualizados
        if not file_exists:
            writer.writerow([
                "Match ID", "Duración (s)", "Modo de juego", "Parche", "Equipo Ganador",
                "Equipo", "Invocador", "Campeón", "Runas", "Hechizos", "K/D/A",
                "Daño total", "Daño recibido", "Oro acumulado", "Objetos",
                "Racha Asesinatos", "Daño a Torres", "Daño a Dragones/Barones",
                "Asistencias", "Barón Kills", "Nivel de recompensa", "Experiencia", "Nivel",
                "Pings - All In", "Pings - Assist Me", "Pings - Enemy Missing",
                "Kills", "Deaths", "Double Kills", "Triple Kills", "Quadra Kills", "Penta Kills",
                "Dragon Kills", "Inhibitor Kills", "Torre Destruida", "Nexus Kills",
                "Total Minions", "Total Heal", "Total CC", "Total Time Dead", "Vision Score",
                "Wards Puestos", "Wards Destruidos"
            ])
        
        # Detalles de los jugadores
        for participant in match_details['info']['participants']:
            summoner_name = participant['summonerName']

            # Convertir IDs de ítems a nombres
            items = ', '.join([get_item_name(participant.get(f'item{i}', 0), item_data) for i in range(7)])

            # Convertir IDs de runas a nombres y subnombres
            runes = get_rune_details(participant, rune_data)

            kda = f"{participant['kills']}/{participant['deaths']}/{participant['assists']}"

            # Escribir datos en CSV
            writer.writerow([
                match_details['metadata']['matchId'],
                match_details['info']['gameDuration'],
                match_details['info']['gameMode'],
                match_details['info']['gameVersion'],
                'Blue' if match_details['info']['teams'][0]['win'] else 'Red',
                'Blue' if participant['teamId'] == 100 else 'Red',
                summoner_name,
                participant['championName'],
                runes,  # Runas en formato original con nombres
                f"{participant['summoner1Id']}, {participant['summoner2Id']}",
                kda,
                participant['totalDamageDealtToChampions'],
                participant['totalDamageTaken'],
                participant['goldEarned'],
                items,  # Nombres de los objetos en lugar del ID
                participant['largestKillingSpree'],
                participant['damageDealtToTurrets'],
                participant['damageDealtToObjectives'],
                participant['assists'],
                participant['baronKills'],
                participant['bountyLevel'],
                participant['champExperience'],
                participant['champLevel'],
                participant['allInPings'],
                participant['assistMePings'],
                participant['enemyMissingPings'],
                participant['kills'],
                participant['deaths'],
                participant['doubleKills'],
                participant['tripleKills'],
                participant['quadraKills'],
                participant['pentaKills'],
                participant['dragonKills'],
                participant['inhibitorKills'],
                participant['turretKills'],
                participant['nexusKills'],
                participant['totalMinionsKilled'],
                participant['totalHeal'],
                participant['totalTimeCCDealt'],
                participant['totalTimeSpentDead'],
                participant['visionScore'],
                participant['wardsPlaced'],
                participant['wardsKilled']
            ])
    print(f"Información guardada en {csv_file}.")

# Función principal
def main():
    item_data = download_item_data()
    rune_data = download_rune_data()

    
    puuid = get_puuid_by_riot_id(GAME_NAME, TAG_LINE)
    match_ids = get_match_ids(puuid, count=25)

    for match_id in match_ids:
        match_details = get_match_details(match_id)
        if match_details:
            save_to_csv(match_details, item_data, rune_data)

if __name__ == '__main__':
    main()
