import discord
import json
import os
from discord.ext import commands


with open("config.json") as f:
    config = json.load(f)
    TOKEN = config["TOKEN"]
    GUILD_ID = config["GUILD_ID"]


intents = discord.Intents.default()
intents.message_content = True  # Habilitar lectura de mensajes

bot = commands.Bot(command_prefix='!', intents=intents)


reports_dir = 'assets/reportes'  
players_file = os.path.join(reports_dir, 'players.txt')  


def leer_lista_jugadores():
    if not os.path.exists(players_file):
        return []
    with open(players_file, 'r') as file:
        jugadores = file.read().splitlines()
    return jugadores

@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} conectado')

@bot.command(name='reporte')
async def enviar_reporte(ctx, player_name: str = None):
    
    jugadores = leer_lista_jugadores()

    
    if player_name is None:
        if not jugadores:
            await ctx.send("⚠️ No hay jugadores disponibles.")
        else:
            jugadores_str = "\n".join(jugadores)
            await ctx.send(f"📋 Lista de jugadores disponibles:\n{jugadores_str}\n\nUsa `!reporte <nombre_del_jugador>` para obtener el reporte de un jugador específico.")
        return

    
    if player_name not in jugadores:
        await ctx.send(f"⚠️ No se encontraron datos para el jugador {player_name}.")
        return

    # Enviar el reporte
    file_path = os.path.join(reports_dir, f'dashboard_{player_name}.pdf')
    if os.path.exists(file_path):
        await ctx.send(f"Aquí tienes tu reporte de partidas para {player_name}:", file=discord.File(file_path))
    else:
        await ctx.send(f"No se encontró el reporte para {player_name}. Asegúrate de generarlo antes de solicitarlo.")

bot.run(TOKEN)