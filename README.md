# DataRiot

LeagueOfLegends-DataManagement

# Proyecto de Análisis de Partidas de League of Legends

Este proyecto contiene scripts y archivos para descargar, procesar y analizar datos de partidas de League of Legends. A continuación se describe brevemente la funcionalidad de cada archivo en la carpeta del proyecto.

## Archivos

- **lol_match_history_in_csv.py**: Este script descarga el historial de partidas de un jugador específico y guarda los detalles en un archivo CSV. Utiliza la API de Riot Games para obtener los datos de las partidas.

- **lol_match_analysis.py**: Este script analiza los datos de las partidas guardadas en el archivo CSV. Genera gráficos y estadísticas descriptivas para visualizar el rendimiento del jugador en diferentes partidas.

## Uso

1. **Descargar el historial de partidas**:

   - Ejecuta `lol_match_history_in_csv.py` para descargar y guardar el historial de partidas en un archivo CSV.

2. **Analizar las partidas**:
   - Ejecuta `lol_match_analysis.py` para generar gráficos y estadísticas descriptivas basadas en los datos de las partidas guardadas en el archivo CSV.

## Requisitos

- Python 3.x
- Bibliotecas: `pandas`, `matplotlib`, `requests`

Puedes instalar las bibliotecas necesarias utilizando `pip`:

```sh
pip install pandas matplotlib requests
```
