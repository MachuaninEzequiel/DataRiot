import requests
import time
import json

API_LOCAL = "http://127.0.0.1:2999/liveclientdata/allgamedata"
output_file = "game_tracking.json"

def get_game_data():
    try:
        response = requests.get(API_LOCAL)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error en la API: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("El juego no está en ejecución.")
    return None

def track_game():
    data_log = []
    print("Esperando que inicie la partida...")
    
    while True:
        game_data = get_game_data()
        
        if game_data:
            timestamp = time.time()
            players = game_data.get("allPlayers", [])

            tracked_data = []
            for player in players:
                tracked_data.append({
                    "timestamp": timestamp,
                    "position": player["position"]
                })
            
            data_log.append(tracked_data)

            
            with open(output_file, 'w') as f:
                json.dump(data_log, f, indent=4)
        
        time.sleep(0.5) 

if __name__ == "__main__":
    track_game()