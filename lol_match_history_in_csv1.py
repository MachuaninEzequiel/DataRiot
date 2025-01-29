import requests
import json
import csv
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

# Extraer datos avanzados del equipo
def extract_team_stats(team):
    return {
        "Barones capturados": team['objectives']['baron']['kills'],
        "Dragones capturados": team['objectives']['dragon']['kills'],
        "Heraldos capturados": team['objectives']['riftHerald']['kills'],
        "Torres destruidas": team['objectives']['tower']['kills'],
        "Inhibidores destruidos": team['objectives']['inhibitor']['kills'],
        "Asesinatos del equipo": team['objectives']['champion'].get('kills', 0)  # Usar .get para evitar KeyError
    }

# Extraer datos avanzados del jugador
def extract_player_stats(participant, team_total_damage, team_kills):
    return {
        "Campeón": participant['championName'],
        "Rol": participant.get('individualPosition', ""),
        "Oro por minuto": round(participant['goldEarned'] / max(1, participant['timePlayed'] / 60), 2),
        "Daño infligido (%)": round(participant['totalDamageDealtToChampions'] / max(1, team_total_damage) * 100, 2),
        "Control de masas (s)": participant['timeCCingOthers'],
        "Curación realizada": participant['totalHeal'],
        "Escudos otorgados": participant['totalHealsOnTeammates'],
        "Centinelas colocados": participant['wardsPlaced'],
        "Centinelas destruidos": participant['wardsKilled'],
        "Tiempo muerto (s)": participant['totalTimeSpentDead'],
        "Participación en asesinatos": round((participant['kills'] + participant['assists']) / max(1, team_kills) * 100, 2)
    }

# Extraer eventos importantes del timeline
def extract_timeline_events(timeline):
    events = {
        "Primer asesinato": None,
        "Primer dragón": None,
        "Primer barón": None,
        "Primera torre": None
    }

    for frame in timeline['info']['frames']:
        for event in frame['events']:
            if event['type'] == 'CHAMPION_KILL' and not events["Primer asesinato"]:
                events["Primer asesinato"] = event['timestamp'] // 1000  # Convertir a segundos
            elif event['type'] == 'ELITE_MONSTER_KILL':
                if event['monsterType'] == 'DRAGON' and not events["Primer dragón"]:
                    events["Primer dragón"] = event['timestamp'] // 1000
                elif event['monsterType'] == 'BARON_NASHOR' and not events["Primer barón"]:
                    events["Primer barón"] = event['timestamp'] // 1000
            elif event['type'] == 'BUILDING_KILL' and event['buildingType'] == 'TOWER' and not events["Primera torre"]:
                events["Primera torre"] = event['timestamp'] // 1000

    return events

# Calcular tiempos en base y distancia recorrida aproximada
def calculate_movement_and_base_time(participant_frames):
    time_in_base = 0
    total_distance = 0

    for i, frame in enumerate(participant_frames[:-1]):
        next_frame = participant_frames[i + 1]
        xp, yp = frame['position']['x'], frame['position']['y']
        xn, yn = next_frame['position']['x'], next_frame['position']['y']

        if xp == 0 and yp == 0:
            time_in_base += 1.5  # Asumimos 1.5 segundos por frame en base
        else:
            total_distance += ((xn - xp) ** 2 + (yn - yp) ** 2) ** 0.5

    return round(time_in_base, 2), round(total_distance, 2)

# Guardar los datos en un archivo CSV
def save_to_csv(match_details, timeline):
    match_id = match_details['metadata']['matchId']
    participants = match_details['info']['participants']
    teams = match_details['info']['teams']

    timeline_events = extract_timeline_events(timeline)

    # Crear o abrir archivo CSV
    filename = "match_history_csv1.csv"
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Encabezados
        if file.tell() == 0:  # Si el archivo está vacío, agregar encabezados
            writer.writerow([
                "Match ID", "Equipo", "Jugador", "Campeón", "Rol",
                "Oro por minuto", "Daño infligido (%)", "Control de masas (s)",
                "Curación realizada", "Escudos otorgados", "Centinelas colocados",
                "Centinelas destruidos", "Tiempo muerto (s)", "Participación en asesinatos",
                "Barones capturados", "Dragones capturados", "Heraldos capturados",
                "Torres destruidas", "Inhibidores destruidos", "Primer asesinato",
                "Primer dragón", "Primer barón", "Primera torre", "Tiempo en base (s)",
                "Distancia total (px)"
            ])

        # Agregar datos por equipo y jugador
        for team in teams:
            team_stats = extract_team_stats(team)
            team_id = team['teamId']

            for participant in participants:
                if participant['teamId'] == team_id:
                    player_stats = extract_player_stats(participant, team['objectives']['champion'].get('damage', 0), team_stats['Asesinatos del equipo'])
                    participant_id = participant['participantId']
                    participant_frames = [frame['participantFrames'][str(participant_id)] for frame in timeline['info']['frames'] if str(participant_id) in frame['participantFrames']]
                    time_in_base, total_distance = calculate_movement_and_base_time(participant_frames)

                    writer.writerow([
                        match_id, "Blue" if team_id == 100 else "Red", participant['summonerName'],
                        player_stats['Campeón'], player_stats['Rol'], player_stats['Oro por minuto'],
                        player_stats['Daño infligido (%)'], player_stats['Control de masas (s)'],
                        player_stats['Curación realizada'], player_stats['Escudos otorgados'],
                        player_stats['Centinelas colocados'], player_stats['Centinelas destruidos'],
                        player_stats['Tiempo muerto (s)'], player_stats['Participación en asesinatos'],
                        team_stats['Barones capturados'], team_stats['Dragones capturados'],
                        team_stats['Heraldos capturados'], team_stats['Torres destruidas'],
                        team_stats['Inhibidores destruidos'], timeline_events['Primer asesinato'],
                        timeline_events['Primer dragón'], timeline_events['Primer barón'],
                        timeline_events['Primera torre'], time_in_base, total_distance
                    ])

# Función principal
def main():
    puuid = get_puuid_by_riot_id(GAME_NAME, TAG_LINE)
    if puuid:
        match_ids = get_match_ids(puuid, count=5)  # Cambia el número de partidas según lo necesites
        if match_ids:
            for match_id in match_ids:
                match_details = get_match_details(match_id)
                timeline = get_match_timeline(match_id)
                if match_details and timeline:
                    save_to_csv(match_details, timeline)

if __name__ == '__main__':
    main()
