import json

# Ruta del archivo JSON
json_file_path = 'd:/DataRiot/data.json'

# Leer el archivo JSON
with open(json_file_path, 'r') as file:
    data = json.load(file)

# PUUID del jugador específico
target_puuid = "pdmN972ngUQ-JA_vaXJub2NsoIn2CGdFRE0Q1c8NEkYOTpQVgCY1B_srRSF-HF4G4L09ES1cOk_u0A"

# Encontrar el participantId correspondiente al target_puuid
participant_id = None
for i, puuid in enumerate(data['metadata']['participants']):
    if puuid == target_puuid:
        participant_id = i + 1  # Los participantId son 1-indexed
        break

if participant_id is None:
    print(f"No se encontró el participantId para el PUUID {target_puuid}")
else:
    # Contar las posiciones del jugador específico
    position_count = 0

    # Recorrer los frames del timeline
    for frame in data['info']['frames']:
        participant_frame = frame['participantFrames'].get(str(participant_id))
        if participant_frame and 'position' in participant_frame:
            position_count += 1

    print(f"El jugador con PUUID {target_puuid} tiene {position_count} posiciones registradas.")