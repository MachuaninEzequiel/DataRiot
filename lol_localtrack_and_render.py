import requests
import time
import json
import numpy as np
import cv2
import matplotlib.pyplot as plt

API_LOCAL = "http://127.0.0.1:2999/liveclientdata/allgamedata"
MAP_SIZE = (14870, 14881)  
VIDEO_SIZE = (800, 800)  
time_interval = 0.5

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

def transform_position(position):
    """
    Transforma la posición del juego a coordenadas dentro de la imagen.
    """
    x = int((position['x'] / MAP_SIZE[0]) * VIDEO_SIZE[0])
    y = int((1 - (position['y'] / MAP_SIZE[1])) * VIDEO_SIZE[1])  
    return (x, y)

def draw_map(player_positions):
    """
    Dibuja un frame con las posiciones de los jugadores en el mapa.
    """
    frame = np.ones((VIDEO_SIZE[1], VIDEO_SIZE[0], 3), dtype=np.uint8) * 50  
    
    for player in player_positions:
        pos = transform_position(player["position"])
        cv2.circle(frame, pos, 10, (0, 255, 0), -1)  
    
    return frame

def track_and_render():
    print("Esperando que inicie la partida...")
    cv2.namedWindow("Mapa en Vivo", cv2.WINDOW_NORMAL)
    
    while True:
        game_data = get_game_data()
        
        if game_data:
            players = game_data.get("allPlayers", [])
            player_positions = [{"position": p["position"]} for p in players]
            frame = draw_map(player_positions)
            
            cv2.imshow("Mapa en Vivo", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        time.sleep(time_interval)
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    track_and_render()