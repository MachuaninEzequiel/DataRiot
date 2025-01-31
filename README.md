# LeagueOfLegends DataManagement

## Análisis de Partidas de League of Legends

Este proyecto contiene scripts y archivos para descargar, procesar y analizar datos de partidas de League of Legends. A continuación se describe brevemente la funcionalidad de cada archivo en la carpeta del proyecto.

### Archivos

- **lol_match_history_in_csv.py**: Este script descarga el historial de partidas de un jugador específico y guarda los detalles en un archivo CSV. Utiliza la API de Riot Games para obtener los datos de las partidas.

- **lol_match_analysis.py**: Este script analiza los datos de las partidas guardadas en el archivo CSV. Genera gráficos y estadísticas descriptivas para visualizar el rendimiento del jugador en diferentes partidas.

- **lol_dashboard_stats.py**: Este script genera un dashboard con estadísticas visuales del rendimiento del jugador y guarda el nombre del jugador en `players.txt`.

- **lol_discord_report.py**: Este script configura un bot de Discord que permite a los usuarios solicitar reportes de partidas a través de comandos en Discord.

### Uso

1. **Descargar el historial de partidas**:

   - Ejecuta `lol_match_history_in_csv.py` para descargar y guardar el historial de partidas en un archivo CSV.

2. **Analizar las partidas**:

   - Ejecuta `lol_match_analysis.py` para generar gráficos y estadísticas descriptivas basadas en los datos de las partidas guardadas en el archivo CSV.

3. **Crear el dashboard**:

   - Ejecuta `lol_dashboard_stats.py` para generar un dashboard con estadísticas visuales del rendimiento del jugador. Este script también guarda el nombre del jugador en `players.txt`.

4. **Generar el patrón de análisis**:

   - Asegúrate de que los archivos generados por los scripts anteriores estén en la carpeta `assets/reportes`. Estos archivos incluyen los dashboards y la lista de jugadores (`players.txt`).

5. **Interactuar con el Bot de Discord**:
   - Ejecuta `lol_discord_report.py` para iniciar el bot de Discord.
   - Usa el comando `!reporte` en un canal de texto de Discord donde el bot esté presente para obtener la lista de jugadores disponibles.
   - Usa el comando `!reporte <nombre_del_jugador>` para obtener el reporte de un jugador específico. Reemplaza `<nombre_del_jugador>` con el nombre del jugador para el cual deseas obtener el reporte.

### Requisitos

- Python 3.x
- Bibliotecas: `pandas`, `matplotlib`, `requests`, `discord.py`, `fpdf`

Puedes instalar las bibliotecas necesarias utilizando `pip`:

```sh
pip install pandas matplotlib requests discord.py fpdf
```
