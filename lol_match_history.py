import requests
from requests.utils import quote
import json

with open("config.json") as f:
    config = json.load(f)
    API_KEY = config["API_KEY"]
REGION = 'europe'  # Región para las cuentas (americas, europe, asia, etc.)
GAME_NAME = 'EL EKOINOMISTA'  # Reemplaza con el gameName del Riot ID
TAG_LINE = 'EUW'  # Reemplaza con el tagLine del Riot ID (ej: EUW, NA1, etc.)

# URL base de la API
BASE_URL = f'https://{REGION}.api.riotgames.com'

# Obtener el PUUID usando el Riot ID
def get_puuid_by_riot_id(game_name, tag_line):
    url = f'{BASE_URL}/riot/account/v1/accounts/by-riot-id/{quote(game_name)}/{quote(tag_line)}'
    headers = {
        'X-Riot-Token': API_KEY
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lanza una excepción si el código de estado no es 200
        return response.json()['puuid']
    except requests.exceptions.HTTPError as err:
        print(f'Error HTTP al obtener el PUUID: {err}')
        print(f'URL de la solicitud: {url}')
    except KeyError:
        print('Error: No se encontró el campo "puuid" en la respuesta.')
    except Exception as err:
        print(f'Error inesperado al obtener el PUUID: {err}')
    return None

# Obtener la lista de IDs de las últimas partidas
def get_match_ids(puuid, count=10):
    url = f'https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids'
    headers = {
        'X-Riot-Token': API_KEY
    }
    params = {
        'count': count  # Número de partidas a obtener
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Lanza una excepción si el código de estado no es 200
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f'Error HTTP al obtener las partidas: {err}')
    except Exception as err:
        print(f'Error inesperado al obtener las partidas: {err}')
    return None

# Obtener detalles de una partida específica
def get_match_details(match_id):
    url = f'https://{REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}'
    headers = {
        'X-Riot-Token': API_KEY
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lanza una excepción si el código de estado no es 200
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f'Error HTTP al obtener los detalles de la partida: {err}')
    except Exception as err:
        print(f'Error inesperado al obtener los detalles de la partida: {err}')
    return None

# Mostrar información de la partida
def display_match_details(match_details):
    if match_details:
        print(f"Partida ID: {match_details['metadata']['matchId']}")
        print(f"Modo de juego: {match_details['info']['gameMode']}")
        print(f"Duración: {match_details['info']['gameDuration']} segundos")
        print("Jugadores:")
        for participant in match_details['info']['participants']:
            print(f" - {participant['riotIdGameName']}#{participant['riotIdTagline']} ({participant['championName']}) - KDA: {participant['kills']}/{participant['deaths']}/{participant['assists']}")
    else:
        print("No se encontraron detalles de la partida.")

# Función principal
def main():
    # Obtener el PUUID usando el Riot ID
    puuid = get_puuid_by_riot_id(GAME_NAME, TAG_LINE)
    if puuid:
        print(f"PUUID obtenido: {puuid}")
        # Obtener la lista de IDs de las últimas partidas
        match_ids = get_match_ids(puuid)
        if match_ids:
            print("Últimas partidas:")
            for i, match_id in enumerate(match_ids):
                print(f"{i + 1}. {match_id}")
            
            # Seleccionar una partida
            try:
                selected_index = int(input("Selecciona el número de la partida para ver detalles: ")) - 1
                if 0 <= selected_index < len(match_ids):
                    match_id = match_ids[selected_index]
                    # Obtener detalles de la partida seleccionada
                    match_details = get_match_details(match_id)
                    display_match_details(match_details)
                else:
                    print("Selección inválida.")
            except ValueError:
                print("Entrada inválida. Debes ingresar un número.")
        else:
            print("No se encontraron partidas recientes.")
    else:
        print("No se pudo obtener el PUUID del invocador.")

if __name__ == '__main__':
    main()