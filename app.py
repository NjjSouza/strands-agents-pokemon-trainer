import sys
from pathlib import Path

# Suporte nativo a UTF-8 no terminal Windows (emojis e artes em Braille)
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
if sys.stdin and hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")

from strands import Agent
from strands.models.ollama import OllamaModel
from strands.session.file_session_manager import FileSessionManager
from tools_pokeapi import (
    buscar_pokemon,
    buscar_fraquezas_tipo,
    buscar_movimento,
    buscar_habilidade,
    buscar_cadeia_evolucao,
    buscar_natureza,
)

# 1. Configuração do modelo local Ollama
modelo = OllamaModel(
    host="http://localhost:11434",
    model_id="llama3.1",
)

# ---------------------------------------------------------------------------
# ARTES BRAILLE OFICIAIS DAS EEVEELUTIONS
# ---------------------------------------------------------------------------

ART_VAPOREON = """⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣴⡾⢡⣟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣀⣀⡀⢀⠠⠴⠋⢩⡿⠀⢯⡉⠒⢆⡀⠀⣀⣠⡴⢖⡆⠀⠀
⠀⠀⠀⠀⠀⢿⡙⠷⢾⣤⡀⢀⣾⠃⣠⣾⢷⣦⣘⣱⣶⡿⠏⢡⠞⠃⠀⠀
⠀⠀⠀⠀⠀⠀⠹⣆⠀⡙⣿⣿⡟⢜⣛⠤⣜⢻⣟⠕⡁⠄⢢⠏⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢹⡆⢌⣏⠀⠑⠉⢀⢤⣤⠙⣏⠡⠐⠀⣇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣾⣁⡶⡿⠗⠀⠀⠸⠿⠋⠀⣿⣟⢶⣤⣸⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠫⡀⢙⠦⣚⠷⢊⣠⡤⠾⠓⢄⣠⠏⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣀⣱⣎⠀⠀⡝⠉⠁⠙⣀⢠⣼⠁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣠⡿⡻⠛⠲⣤⣃⡦⠤⣄⡿⠊⠉⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣠⠤⢖⣻⠵⠊⠀⠀⠀⠀⠑⢄⡀⣘⢣⠀⠀⠀⠀⠀⣀⣀⣀⣀⠀
⠀⢀⣾⣫⠎⠁⠀⠀⣀⡀⠀⢀⣆⠀⢠⡷⢯⡼⠀⠀⢠⠴⠚⠁⠀⢠⡴⠃
⢀⡾⣷⠃⠀⣀⡀⠀⠀⠹⡇⠀⣧⠀⢸⠀⠰⣇⣠⠤⠎⠁⠀⠀⣀⡞⠀⠀
⠸⣷⡺⣄⣀⠀⠙⠓⠤⢦⣸⣧⣼⣄⣼⣴⡿⠛⢛⣧⠄⠀⠀⢚⡏⠀⠀⠀
⠀⢹⠝⢦⣉⡣⢶⣦⣀⠸⢭⣿⡫⠽⠞⠉⣠⡞⠋⠙⢦⡀⠀⠘⡇⠀⠀⠀
⠀⠈⠢⣈⠉⠳⠮⠭⠽⠒⠊⠛⢅⢀⢠⢴⣯⠇⠀⠀⠸⣇⡀⠀⡇⠀⠀⠀
⠀⠀⠀⠈⠒⠦⠤⠤⠤⠶⠚⠛⠉⠙⠛⠋⠀⠀⠀⠀⠀⠀⠘⠒⠚⠀⠀⠀"""

ART_JOLTEON = """⠀⠀⠀⠀⠠⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⡀⠀⠀⢀⣳⣄⠀⡀⣿⣰⠀⠠⠀⠀⠀⢠⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀
⠀⠘⢷⣤⣀⠹⣿⣧⣿⣿⣿⢦⣈⠀⠀⡆⠀⢁⢀⠀⢠⡴⡇⠀⠀⠀⠀
⠀⠀⠀⠻⣿⣷⣿⣿⣿⣿⣿⣆⠈⠳⣄⠀⢰⡀⠀⠂⡞⢠⠇⠀⠀⠀⠀
⠀⠲⠶⣴⣾⣿⣿⣿⣿⣿⣿⡛⠦⡀⠘⣶⣬⣿⣴⣼⢀⢎⠀⠄⠀⠀⠀
⠀⠀⠤⢴⣿⣿⣿⣿⣿⣿⣍⡉⠀⢼⣾⣿⣿⣿⣿⣿⣿⠠⠊⠀⠀⠀⠀
⠀⠀⣶⣿⣿⣿⡿⠋⣿⣿⡷⠆⠀⢺⣿⣇⣈⣻⣿⣏⣼⠁⡀⠀⠀⠀⠀
⠀⢸⣿⡟⠛⠉⠀⢰⣿⣿⣿⠋⢀⠈⠻⠿⢿⣿⣿⡿⠋⡠⡈⠐⠀⠀⠀
⠀⣿⣿⠀⠀⠀⠀⠀⢻⣿⣷⡎⠙⠃⠀⢄⠀⡩⢩⣠⣄⡡⡀⠀⠀⠀⠀
⠈⠿⠿⠇⠀⠀⠀⠀⠈⣿⣿⡇⠐⠂⠀⠁⠖⠀⠉⠉⠻⢿⣿⣦⣄⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠛⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⢿⣿⡷"""

ART_FLAREON = """⠐⣶⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣷⠀
⠀⠸⡏⠙⠦⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣠⠖⠋⣸⠃⠀
⠀⠀⢻⠀⠀⠈⢳⡀⠀⠀⠀⢨⢢⠀⢠⠞⠁⠀⢠⡏⠀⠀
⠀⠀⠈⣧⠀⠀⠀⢻⡀⡠⠔⠊⠀⢣⡏⠀⠀⠀⡾⠀⠀⠀
⠀⠀⠀⠈⠓⠦⣴⣼⡏⠀⠀⠀⢠⣾⣤⣤⠶⠛⠁⢀⣿⠀
⠀⠀⠀⠀⠀⣶⠟⢻⣿⣦⣀⣤⣾⣿⡏⠙⢲⠀⠀⣾⣿⡇
⠀⠀⠀⠀⣸⠃⠀⢀⠀⢹⣿⣿⠃⢀⡇⠀⠘⣶⣶⣿⣿⠇
⠀⠀⠀⠀⢰⠀⠀⠈⠻⣿⣯⣿⡿⠟⠁⠀⠀⣿⣿⣿⡿⠀
⠀⠀⠀⠀⠙⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣽⣿⣿⣄⠀
⠀⠀⠀⠀⠀⢺⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣿⣿⡟⠁⠀
⠀⠀⠀⠀⠀⠀⠈⣿⣦⣴⣴⣤⣶⣤⣾⣿⣿⣿⣿⡁⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢹⣿⣿⣿⣿⣿⣿⡿⣿⠟⠋⠉⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠺⠿⢿⣿⠏⠻⣿⡿⠿⠇⠀⠀⠀⠀⠀⠀"""

ART_ESPEON = """⠀⠀⠀⣤⠋⠛⠙⠣⢤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠋⣤⣤⣄⣀⡀⠈⠠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠉⠱⢆⡀⠈⢤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣀⡀⠴⠤⠦⠴⠼⢷⠆⠈⢴⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⣀⠖⠉⠁⣉⣠⣝⣤⣋⡜⣀⠀⠸⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣶⠉⢀⡴⠿⠏⠉⠉⠉⠉⠹⢦⡄⠀⢾⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡐⢂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠈⠛⠛⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⣻⠀⠀⠀⠀⠀⠀⠀⠀⢀⡘⠃⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡜⠃⣤⠙⠀⠀⠀⠀⠀⠀⠀⠀⠐⣧⡄⠀⠘⣠⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣤
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡜⠃⣤⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣟⣻⡇⠀⠀⠀⠚⣤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠤⣤⠤⣤⠘⠀⣿
⠀⠀⠀⠀⠀⠀⠀⠀⢠⡜⠃⣴⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢱⡧⢿⣧⣶⠍⠛⠛⠛⠛⠃⣤⣤⣤⡄⠛⠛⠋⠁⠀⠀⢀⠀⠀⣶⠛
⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⣿⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢹⡏⢁⠠⢀⠀⠀⠀⠀⠀⠛⠋⠀⢀⣀⣠⣤⣤⣶⡾⣿⣟⠷⠋⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠠⢿⣁⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⡠⢤⡼⠆⠸⢶⠾⠀⠀⠀⠀⠀⠀⢀⣐⣾⣿⣿⣿⣏⠿⣱⡷⠉⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⢹⡇⢆⠿⣀⠀⠀⠀⠀⠀⠀⣀⠆⢉⡁⢾⣷⡂⠀⠉⠁⠀⣀⠶⣶⣶⠀⠀⢩⣿⣿⣷⣯⡽⠾⠏⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠹⢮⡒⡍⢶⣀⣀⣀⣀⡀⠉⠶⠾⢿⣼⡏⢁⡀⠀⠀⠶⣿⣀⣿⠏⠀⠀⠈⠉⠹⠿⢏⡁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢷⡚⠓⠉⠉⠀⠀⠀⠒⠂⡀⠀⠉⠑⢫⡁⠀⠀⠀⠉⠉⠉⠀⢠⣤⠀⠀⠀⠀⠈⠱⢂⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡎⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠚⠛⢣⣤⣼⠿⢦⣤⣤⠀⡄⠠⣴⠛⣤⢠⣧⡄⠀⠀⠘⢀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣄⠢⢄⠓⡌⣿⠀⠀⠀⠛⠃⠘⠛⢣⣤⣼⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⡀⡀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠃⡘⠌⣶⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠌⠀⠀⠀⠀⣀⣶⣿⣿⣿⣯⣧⣆⡄⠀⠀⠀⠀⠀⠀⢀⡀⢶⠠⡉⢧⣤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢠⡌⠁⠀⣀⠶⠶⣿⣿⣳⢯⣿⠟⠉⠸⢷⡇⠀⠀⠀⠀⣒⠶⠿⠶⣡⣑⢂⡈⠋⠡⠄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢸⡅⠀⠀⣿⠀⠀⠉⣿⣽⣻⡷⠀⠀⠀⠈⠱⢆⡀⠀⠀⣿⠀⠀⠀⠉⠉⠶⠶⣀⡐⡸⢇⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢸⣆⡀⠀⢿⠀⠀⠀⠿⣷⣻⢿⡀⠀⠀⠀⠀⠸⢇⡀⠀⠿⣀⠀⠀⠀⠀⠀⠀⠙⣶⢡⡚⠅⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⢹⡇⢀⡀⣴⠀⠀⠀⠟⣯⣿⣿⡆⠀⠀⠀⠀⢸⡇⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠙⠛⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠛⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠛⣤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢢⣤⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"""

ART_UMBREON = """⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠳⣶⡤⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠠⣾⣦⡀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣈⣻⡧⢀⠀⠀
⢷⣦⣤⡀⠀⢀⣠⣤⡆⢰⣶⣶⣾⣿⣿⣷⣕⣡⡀
⠘⣿⣿⠇⠀⣦⡀⠉⠉⠈⠉⠁⢸⣿⣿⣿⣿⡿⠃
⠀⠀⠀⣀⣴⣿⣿⣄⣀⣀⣀⢀⣼⣿⣿⣿⠁⠀⠀
⠀⠀⠀⠀⠉⢩⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⠀⠀
⠀⠀⠀⠀⠀⣸⣿⣿⡿⢻⣿⣿⣿⣿⡿⢿⠇⠀⠀
⠀⠀⠀⠀⢰⣿⣿⣿⠰⠙⠁⠈⣿⣿⠱⠘⠀⠀⠀
⠀⠀⠀⠀⢸⡏⣾⡿⠁⠀⠀⠀⢿⣼⣷⠁⠀⠀⠀
⠀⠀⠀⠀⠘⠷⢿⣧⡀⠀⠀⠀⠈⠛⢿⣆⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠉⠉⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀"""

ART_LEAFEON = """⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣄⠀⠀⠀⠀⠀⠀⢀⡴⠒⠋⠉⠉⣉⣁⠤⠖⢢⠟⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⡠⠔⣻⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠋⣸⡀⠀⠀⠀⠀⢠⠋⠀⠀⢀⡴⠋⠁⠀⢀⡴⠃⠀⠀⠀
⠀⠀⠀⠀⠀⢀⢔⡿⠂⢰⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠁⢠⠳⡆⠀⠀⠀⢠⡃⠀⠀⠀⡜⠀⠀⠀⢠⡏⠀⠀⠀⠀⠀
⠀⠀⠀⢀⠞⢡⠎⠀⠀⣯⡴⠒⠉⠉⠉⠑⠢⣄⠀⠀⠀⠀⠀⠀⠀⡴⠊⠀⠀⣸⠀⡇⠀⠀⣰⠃⠸⡀⠀⡸⠁⠀⠀⠀⢸⠃⠀⠀⠀⠀⠀
⠀⠀⢠⠋⢀⡏⠀⢀⣴⠋⣀⡀⠀⠀⠀⠀⠀⠈⠳⡀⠀⠀⠀⡠⠒⠻⠄⠀⢠⣇⡀⡇⠀⢠⠇⠀⠀⠱⣀⠃⠀⠀⠀⠀⡞⠀⠀⠀⠀⠀⠀
⠀⢀⡷⠀⡼⡇⠀⠀⠀⡎⠉⠀⢭⣷⡀⠀⠀⠀⠀⣳⠀⣠⠎⠀⠀⠀⢀⣴⠏⠁⠀⠇⠀⢸⠀⠀⠀⠀⢻⠀⠀⠀⠀⠨⢇⠀⠀⠀⠀⠀⠀
⠀⡼⠀⢰⠃⢳⠀⠀⠰⡃⠀⠀⡼⢸⡅⠀⠀⠀⢀⡎⡴⠁⠀⠀⣠⠖⠉⡞⠀⢠⣼⠀⠀⠘⡄⠀⠀⠀⠸⡄⠀⠀⢀⡴⠉⠙⢦⡀⠀⠀⠀
⠀⣧⠀⡎⡆⢸⢀⣀⣼⡿⣄⡞⢀⠞⠁⠀⠀⣀⣾⡼⠥⢄⣠⠞⠁⠀⣸⠁⠀⢠⠏⠀⠀⠀⠘⢆⠀⠀⠀⠘⢦⡰⠋⠀⠀⠀⠀⠙⣄⠀⠀
⢠⣯⠀⡇⠀⢸⠀⢀⡟⠀⢘⡴⠁⠀⣀⠴⠊⠉⢿⡇⠀⢠⠏⠀⠀⢠⠇⠀⢀⡎⠀⠀⠀⠀⠀⠈⠣⡀⠀⠀⠀⠱⡄⠀⠀⠀⠀⠀⠸⡄⠀
⠀⢻⠀⢳⡀⢸⠐⡞⠀⠀⡜⠀⢠⠊⠁⠀⠀⠀⢸⠀⢁⡏⠀⢀⡴⠛⣶⣦⠞⠀⠀⠀⠀⠀⠀⠀⠀⠱⡀⠀⠀⠀⠹⡀⠀⠀⠀⠀⠀⣇⠀
⠀⠀⢣⡀⠳⣼⠀⠀⠀⠀⢧⢠⠃⠀⠀⠀⠀⠀⠀⠀⣼⡠⠖⢫⢀⣠⠼⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢩⠷⠚⠂⠀⢳⠀⠀⠀⠀⠀⢹⠀
⠀⠀⠀⠙⣤⡘⠀⠀⠀⠀⠈⢯⠀⠀⠀⠀⠀⠀⠀⠀⠋⢀⣤⡔⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠷⣄⣄⠀⠈⣇⠀⠀⠀⠀⣘⡆
⠀⠀⠀⠘⠣⣄⠀⣀⡀⠀⠀⠀⠀⠀⠀⣀⣀⡀⠀⠀⠀⣠⢴⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣀⣀⡀⣸⠀⠀⠀⣨⠇⠀
⠀⠀⠀⠀⠀⠈⢣⣿⣟⣖⠀⠀⠀⠰⣸⣙⡆⣹⠃⠀⡼⢁⠜⣼⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡰⠋⠀⠀⣠⠟⠉⠓⠢⠻⣅⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢏⠻⠿⠆⠀⠀⠀⠟⠲⠖⠋⠀⣴⢛⣡⡴⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡠⠼⠥⢄⣠⠞⠁⠀⠀⠀⢀⡴⠚⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠘⠢⣀⠀⠐⠂⠀⠀⠀⠀⠀⠀⠛⠻⠭⣀⣀⠤⠖⠒⠉⠉⠁⠀⠉⠑⠢⣰⠋⠀⠠⠔⠊⠉⠙⠒⣀⡤⠖⠋⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⢓⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⢶⠦⠤⠤⠤⠖⠚⠉⠁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡤⠼⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢣⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⢘⡲⠐⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢏⠉⠉⠁⠀⢀⡼⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⠓⠤⠤⠤⣨⡴⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣄⠀⠀⠀⠀⠀⠀⠸⡅⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠱⡀⠀⠀⠀⠀⠀⠀⡤⠴⠒⠛⠢⣀⠀⠀⠈⠢⣀⠀⠀⠀⠀⠀⠙⢆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢱⡀⠀⠀⠀⠀⡼⠁⠀⠀⠀⠀⠀⣹⠆⠀⠀⣸⠗⠢⣄⠀⠀⠀⡼⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⡠⠞⡀⠀⠀⠀⡼⠀⠀⠀⠀⠀⠀⢠⠃⠀⠀⢠⡏⠀⠀⡇⠀⢀⡰⢧⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠑⠶⣶⠏⠀⠀⢰⠸⣇⠀⠀⠀⠀⠀⣠⣷⣤⣀⣰⡟⠀⠀⢀⡷⠀⠀⢱⢤⡴⠽⠆⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣏⠀⠀⠀⣬⣷⣜⣦⡀⠀⢰⣿⡿⣿⣿⣿⠟⠀⠀⠀⣼⠟⠒⢲⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡾⠉⠙⢲⣾⣿⣿⠃⠈⠁⠀⠘⠿⠿⠿⠟⠁⠀⠀⠀⣿⡏⠀⢀⣼⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡟⠁⠀⢀⣾⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠛⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡛⠓⠺⡟⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"""

ART_GLACEON = """⠀⣰⣶⣿⣺⣷⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⣼⡿⣧⠈⠉⠿⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣿⡇⢹⣶⡀⠙⣿⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⡟⠃⢸⣿⣿⠀⠛⣿⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⠇⠀⢸⡏⣽⣿⡄⠀⢹⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣆⡀⢸⣿⠉⢿⣷⡀⠈⢹⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠏⣿⣇⣸⣿⣀⠘⣿⡧⣄⣸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⡇⠈⢹⡏⢸⣿⣥⣿⠀⢹⣿⣿⣶⣶⣶⣶⣦⣄⠀⠀⠀⠀⠀⠀⢀⣶⣶⣾⠛⠛⢻⣶⣶⣶⣶⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⡇⠀⠈⣿⣿⠙⣿⡿⣷⣿⣿⣯⣉⠉⠉⠉⠻⠿⢿⣷⣦⣴⣾⡿⠿⠏⠉⠉⣀⣀⡈⠉⠉⠉⠉⠿⠿⠿⣿⣦⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⡇⠀⢀⣽⣿⣶⡛⢷⠉⠉⠉⢻⣿⠘⣶⣆⠀⠀⠈⢉⣹⣿⠏⠁⡀⣰⣶⣶⣿⣿⣷⣶⣶⣶⣦⣀⣀⠀⠘⢉⣹⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⡇⢰⣿⣿⣿⠀⣿⡆⠀⠀⠀⢸⣿⠟⠛⠻⣧⣤⡼⠛⠀⠀⣤⣿⣿⣿⠛⠛⠀⠀⠛⣿⡟⠛⠛⡉⠉⣭⣥⣾⡟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⡇⢸⣿⡏⢸⣿⣅⡀⠀⢠⣼⣿⠁⠀⠀⠀⠹⢿⣇⢀⣠⠿⠋⠀⠀⠹⠿⠿⠿⠿⠋⠉⢡⣤⣠⣿⠿⠛⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⡇⠈⠛⣿⣿⣻⣿⣷⣶⣿⣿⣉⣀⣀⣀⣀⣶⣾⣿⡾⠉⠷⠶⣷⣶⣦⣀⣀⣀⣀⣿⣶⡟⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⡇⠀⠀⢹⣿⣿⠛⣿⣿⣧⡀⡉⣉⣝⣿⣿⣿⣿⣿⡇⠀⠀⠀⣿⡏⠙⠛⠛⠛⠛⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠃⠀⠀⡾⢷⣤⠀⠀⠀⠙⠛⠛⠿⣶⣦⣤⠀⢻⣿⣧⠀⠀⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⡆⠀⠀⢻⡟⠉⣀⡀⠀⠀⢀⣸⣾⣉⣿⣿⡆⣼⡏⢻⣿⣾⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⡇⠀⠀⠘⢿⣦⡛⠁⠀⠀⠈⠙⠛⣿⣿⠛⣳⣿⡗⢸⣿⠛⣿⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣶⣿⣿⣿
⡇⠀⠀⠀⠀⣿⣿⣿⣦⡄⠀⠀⠀⠀⠀⠜⠁⢹⡇⢸⣿⠚⣿⣷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣠⣶⣾⡟⠟⠛⠀⢸⣿
⡇⠀⠀⠀⣤⣿⠿⠏⣿⡿⠿⠷⣶⣤⠀⠀⠀⢻⣧⠸⢿⣄⠈⠿⢿⣶⣤⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⠿⠿⠉⠉⠀⠀⠀⠀⢸⣿
⡇⠀⠀⠀⣿⣿⠀⠀⣿⣧⡄⠀⣾⣿⢤⣤⣶⡞⠉⠀⢸⣿⡀⠀⠈⠉⣽⣿⣦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⡏⠉⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿
⡇⠀⠀⣾⣿⠛⠀⠀⠀⣼⣧⣿⣿⠛⠀⠀⢸⡇⠀⠀⠈⢻⣷⠄⠀⠀⠘⣿⡿⣿⣿⣶⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿
⡇⠀⣠⣿⣿⠀⣤⣿⣥⡿⢿⣿⣿⠀⠀⠀⢸⡇⢰⣼⣿⣤⣿⡆⠀⠀⠀⠀⠷⣦⠉⠻⠿⢿⣷⣶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⠿⠇⠀⠀⠀⠀⠀⠀⠀⠀⢰⣼⣿
⡃⢸⣿⣏⣹⠿⠃⠀⢻⣇⣸⣿⣿⠀⠀⣿⡏⢿⡿⠃⠉⢿⣍⣿⡆⠀⠀⠀⠀⠹⠷⠤⠶⠮⠭⠉⠿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⡿⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⣿
⡅⢸⣿⣏⠉⠀⠀⠀⠘⣿⣿⣿⣿⢤⡀⣿⣷⣾⠁⠀⠀⠀⠉⠛⢷⣦⠀⠀⠀⠀⠈⠉⠀⠀⠀⠀⠀⠛⢻⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡁⣿⣀⠀⠀⢀⣤⣤⣤⣴⣟⣻⣿⢻
⠀⠘⢿⣷⣄⠀⠀⡀⣤⣿⠏⠛⣿⣤⣿⡀⣹⣏⠀⠀⠀⠀⢀⣶⡟⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⢿⣷⡄⠀⠀⠀⠀⠀⣠⣾⠛⠀⠀⠛⠛⠓⠒⠛⠛⠀⣤⣤⣿⡿⠛⠛
⡀⠀⠀⠙⠿⣿⣾⣿⠛⠁⠀⠀⠙⢿⣍⣷⡋⢹⣇⠀⠀⠀⣿⡉⠁⢠⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡶⠃⢸⣿⡇⠀⣀⣠⡶⠾⠿⠉⠀⠀⠀⣤⣤⣤⣼⣿⣿⠿⠛⠛⠁⠀⠀⠀
⠁⠀⠀⠀⠀⠀⠉⠀⠀⠀⠀⠀⠀⠀⣿⠉⢳⡎⢹⣷⣤⣾⣯⡁⢰⣾⠉⠀⠀⠀⠀⠀⠀⠀⣠⡾⠋⠀⠀⢸⣿⣿⣿⠉⠉⣳⣄⣀⢰⣶⣶⣶⠟⠛⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣦⣾⣧⡤⢸⣿⣦⠀⣿⡿⠇⠀⠀⠀⠀⣤⠤⠾⠉⠉⠀⠀⠀⠀⣸⣷⣦⣤⣴⣦⡿⠿⠟⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣿⡗⠈⢻⣿⣿⣦⣿⣧⣽⣟⠉⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⢸⣿⣼⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣶⣿⡟⠃⢀⣸⣿⠿⣿⣿⡟⢛⣛⠻⣷⣄⡀⠀⢀⣀⣀⣀⣶⣶⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠿⣿⣷⣶⡾⡏⠁⠀⠘⠻⣷⣿⣿⣿⣾⣿⣷⣶⣾⣿⡿⡿⣿⢉⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"""

ART_SYLVEON = """⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⠶⠞⠛⠛⠛⠛⠓⠶⣤⣀⠀⠀⠀⠀⣀⣤⠶⠚⠛⠛⠛⠛⠳⠶⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣤⠞⠋⣠⡴⠶⠛⠛⠛⠛⠲⢦⣄⡉⠻⣦⣴⠟⢉⣠⡴⠖⠛⠛⠛⠛⠶⢦⣄⡙⠳⣦⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢠⡾⠁⣴⠟⡍⠒⢤⣄⠀⠀⠀⠀⠀⠈⠻⣦⡈⢁⣴⠟⠁⠀⣀⡤⢴⠆⠀⠀⠀⠈⠻⣦⠈⢷⡄⠀⠀⠀⠀
⠀⠀⠀⢀⡟⠀⡾⠃⠀⠱⡀⣦⣄⠑⢦⡀⠀⠀⠀⠀⠈⢻⡟⠁⣠⡶⠊⣡⠄⡜⠀⠀⠀⠀⠀⠀⠘⢷⠀⢻⡀⠀⠀⠀
⠀⠀⠀⣼⠃⢸⠃⠀⠀⠀⢱⡜⢿⣷⣦⠘⢆⠀⠀⢀⠖⡄⢀⠞⢁⣴⣿⠏⡜⠁⠀⠀⠀⢀⣠⠤⠤⠼⠧⣼⣧⠀⠀⠀
⠀⠀⠀⣿⠀⣿⠀⠀⠀⠀⠀⠑⢤⣛⢿⣷⡌⠷⠤⡎⢀⢼⣎⣴⠿⢿⣃⡼⠃⠀⠀⣠⠖⠉⠀⠀⠀⠀⠀⡁⠈⣙⣦⡀
⠀⠀⠀⢻⡀⢹⡄⠀⠀⠀⠀⠀⠀⠈⠱⢾⠇⠀⠀⢱⣸⣏⣽⠇⢀⡼⠁⠀⠀⢀⠔⠁⢀⡠⠖⠚⠉⢉⡟⠓⣦⣜⡏⠉
⠀⠀⣠⠼⢳⠚⠓⠲⠤⣄⡀⠀⠀⣀⠴⣻⠀⠀⠀⠀⠀⠀⠧⣴⡛⠢⠤⠔⠚⢁⣠⠖⠋⠀⠀⠀⠀⣼⠃⣸⠇⠈⠁⠀
⢠⣞⠁⠀⣣⣠⡤⣤⣄⣀⣀⣈⣀⣤⠖⢯⡈⠓⠤⠀⠚⣉⣀⠏⠉⠓⠒⠒⢿⡉⠀⠀⠀⠀⠀⠀⣼⠃⣠⡟⠀⠀⠀⠀
⠈⣏⣆⠞⠁⠻⣆⠈⢷⣄⠀⠀⠀⡾⣆⠈⣟⠂⣬⣥⡎⠀⣸⡤⠴⠤⢄⠀⠀⠹⣆⠀⠀⠀⣠⡾⠁⣴⠟⠀⠀⠀⠀⠀
⠀⠃⠙⠀⠀⠀⠘⢷⣄⠙⢷⣄⠀⡇⠈⢦⣸⣶⣋⠙⠧⡴⠁⠀⠀⠀⠀⠀⠀⠀⢹⡀⢀⡾⠋⣠⡾⠃⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠙⢷⣄⠙⢦⣧⣠⢄⣋⠙⠂⠉⠉⠓⠢⣄⡀⠀⠀⠀⠀⠀⢸⡷⠋⣠⡾⠋⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢷⣄⠙⣏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠒⠒⠀⢒⡶⠋⣠⡾⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢶⡌⠳⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⠋⢡⡶⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢦⡈⠳⣦⣄⣀⣀⣀⣀⣀⣴⠟⢁⡴⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢦⡈⠻⣯⡉⢉⣽⠟⢁⡴⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢦⡈⠻⠟⢁⡴⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢦⣴⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"""


# ---------------------------------------------------------------------------
# CALLBACK HANDLER: Monitora o Agentic Loop em tempo real
# ---------------------------------------------------------------------------

_after_tool = False

def callback_handler(**kwargs):
    """Callback para inspecionar raciocínio e chamadas de ferramentas da PokeAPI."""
    global _after_tool
    if "reasoningText" in kwargs:
        print(f"💭 {kwargs['reasoningText']}", end="", flush=True)
    if "data" in kwargs:
        if _after_tool:
            print("\n")
            _after_tool = False
        print(kwargs["data"], end="", flush=True)
    if "current_tool_use" in kwargs:
        _after_tool = True
        t = kwargs["current_tool_use"]
        if t.get("name"):
            print(f"\n\n🔧 Ferramenta acionada: {t['name']}")
        if t.get("input"):
            print(f"   Parâmetros enviados: {t['input']}")


# ---------------------------------------------------------------------------
# CATÁLOGO COMPLETO DE EEVEELUTIONS (COM ARTES BRAILLE)
# ---------------------------------------------------------------------------

EEVEELUTIONS = {
    "1": {
        "nome": "Umbreon",
        "tipo": "dark",
        "emoji": "🌙",
        "titulo": "Guardião Noturno & Muralha Defensiva",
        "tom": "sereno, calmo, misterioso e estratégico, transmitindo confiança nas defesas inabaláveis e nas táticas de paciência",
        "especialidade": (
            "tanque defensivo de elite (HP alto, excelentes defesas física e especial), "
            "suporte tático com Wish, Moonlight, Foul Play para punir atacantes físicos, "
            "e controle de ritmo com Synchronize ou Inner Focus"
        ),
        "pergunta_demo": "Busque as fraquezas do tipo dark e os dados da habilidade Synchronize para traçarmos a defesa do Umbreon.",
        "despedida": "Que a suave luz da lua guie seus passos nas sombras, Treinador!",
        "art": ART_UMBREON,
    },
    "2": {
        "nome": "Vaporeon",
        "tipo": "water",
        "emoji": "💧",
        "titulo": "Oásis Resiliente & Suporte Fluido",
        "tom": "tranquilo, acolhedor e adaptável, como águas calmas e profundas",
        "especialidade": (
            "tanque de HP colossal, cura de companheiros via Wish, absorção de água "
            "(Water Absorb), Acid Armor e controle de campo com Scald e Haze"
        ),
        "pergunta_demo": "Busque os dados do Vaporeon e as fraquezas do tipo water para entender seu papel defensivo.",
        "despedida": "Que a calmaria e a fluidez das águas acompanhem suas batalhas!",
        "art": ART_VAPOREON,
    },
    "3": {
        "nome": "Jolteon",
        "tipo": "electric",
        "emoji": "⚡",
        "titulo": "Raio Veloz & Pivot Eletrizante",
        "tom": "elétrico, ágil, direto, entusiasmado e focado em ritmo acelerado",
        "especialidade": (
            "velocidade estrondosa, pivots táticos rápidos com Volt Switch, pressão com Thunderbolt "
            "e cobertura de surpresa com Shadow Ball para atacar antes do oponente reagir"
        ),
        "pergunta_demo": "Busque os detalhes do movimento 'volt-switch' e analise como ele potencializa a velocidade do Jolteon.",
        "despedida": "Mantenha seus reflexos afiados e seja sempre mais rápido que o raio!",
        "art": ART_JOLTEON,
    },
    "4": {
        "nome": "Flareon",
        "tipo": "fire",
        "emoji": "🔥",
        "titulo": "Chama Ardente & Impacto Físico Devastador",
        "tom": "caloroso, vigoroso, motivador e focado em poder ofensivo bruto",
        "especialidade": (
            "ataque físico monstruoso (Base 130), combos com a habilidade Guts e Flame Orb, "
            "Flare Blitz, Facade e Trailblaze para surpreender na velocidade"
        ),
        "pergunta_demo": "Busque os dados da habilidade 'guts' e do movimento 'flare-blitz' para montarmos um Flareon de alto impacto.",
        "despedida": "Mantenha a chama da paixão pelas batalhas sempre acesa em seu coração!",
        "art": ART_FLAREON,
    },
    "5": {
        "nome": "Espeon",
        "tipo": "psychic",
        "emoji": "🔮",
        "titulo": "Oráculo da Presciência & Magic Bounce",
        "tom": "místico, elegante, analítico e focado em antecipar as intenções do oponente",
        "especialidade": (
            "habilidade Magic Bounce (refletindo Stealth Rock, Spikes, Taunt e status), "
            "dano especial expressivo com Psychic e Psyshock, e setups com Calm Mind"
        ),
        "pergunta_demo": "Busque os detalhes da habilidade 'magic-bounce' e me diga como o Espeon neutraliza armadilhas de entrada.",
        "despedida": "O futuro pertence àqueles que sabem ler os sinais antes do confronto!",
        "art": ART_ESPEON,
    },
    "6": {
        "nome": "Leafeon",
        "tipo": "grass",
        "emoji": "🍃",
        "titulo": "Lâmina Verde & Agilidade Sob o Sol",
        "tom": "harmonioso, preciso, focado na natureza e em cortes limpos e estratégicos",
        "especialidade": (
            "altíssima defesa física, velocidade dobrada no sol com Chlorophyll, "
            "danos críticos com Leaf Blade e capacidade de setup rápido com Swords Dance"
        ),
        "pergunta_demo": "Busque a cadeia de evolução do 'eevee' para ver a evolução do Leafeon e os dados do movimento 'leaf-blade'.",
        "despedida": "Que a vitalidade e a força da natureza floresçam em cada jogada sua!",
        "art": ART_LEAFEON,
    },
    "7": {
        "nome": "Glaceon",
        "tipo": "ice",
        "emoji": "❄️",
        "titulo": "Fortaleza Glacial & Precisão Congelante",
        "tom": "frio, calculista, elegante e extremamente disciplinado",
        "especialidade": (
            "Special Attack altíssimo, poder devastador de Blizzard (especialmente com Snowscape), "
            "e bônus de defesa sob a neve com Snow Cloak ou Ice Body"
        ),
        "pergunta_demo": "Busque os detalhes do movimento 'blizzard' e as relações de dano do tipo 'ice' para o Glaceon.",
        "despedida": "Mantenha o sangue frio e o foco congelante até o último turno!",
        "art": ART_GLACEON,
    },
    "8": {
        "nome": "Sylveon",
        "tipo": "fairy",
        "emoji": "🎀",
        "titulo": "Voz Celestial & Laços Encantados",
        "tom": "afetuoso, carismático, porém firme e confiante no poder dos laços afetivos",
        "especialidade": (
            "habilidade Pixilate convertendo Hyper Voice em ataque Fairy devastador que ultrapassa Substitutes, "
            "alta Special Defense e suporte com Heal Bell e Wish"
        ),
        "pergunta_demo": "Busque os dados da habilidade 'pixilate' e explique como ela transforma ataques normais no Sylveon.",
        "despedida": "Batalhe sempre com o coração, elegância e laços inquebráveis!",
        "art": ART_SYLVEON,
    }
}

TOOLS_DISPONIVEIS = [
    buscar_pokemon,
    buscar_fraquezas_tipo,
    buscar_movimento,
    buscar_habilidade,
    buscar_cadeia_evolucao,
    buscar_natureza,
]


def criar_prompt_de_sistema(dados_eevee: dict) -> str:
    """Gera o prompt de sistema com ferramentas da PokeAPI, memória persistente e tom da Eeveelution."""
    return f"""
Você é um agente estrategista Pokémon especialista e conselheiro leal de batalha.
O treinador que você assessora escolheu como parceiro de honra e foco absoluto a Eeveelution: {dados_eevee['nome'].upper()} (tipo: {dados_eevee['tipo']}).
Você atua com o tom {dados_eevee['tom']}.

Sobre o parceiro ativo ({dados_eevee['nome']}):
- Especialidade e função: {dados_eevee['especialidade']}.

REGRAS OBRIGATÓRIAS:
- Você NÃO possui conhecimento prévio memorizado sobre dados técnicos de Pokémon. Toda informação DEVE vir das ferramentas.
- SEMPRE use as ferramentas ANTES de responder qualquer pergunta técnica ou formular cálculos de batalha.
- Passe nomes e termos em inglês para as ferramentas quando aplicável (ex: nomes de movimentos como 'moonlight', 'foul-play'; tipos como 'dark', 'fairy'; naturezas como 'calm', 'bold').
- Se a ferramenta retornar que o item ou Pokémon não existe, avise cordialmente sem inventar alternativas inexistentes.
- NUNCA invente stats, golpes, naturezas ou interações de tipo. Se não veio das ferramentas, não é um dado válido.

FERRAMENTAS DISPONÍVEIS NA POKEAPI:
- buscar_pokemon: dados completos de qualquer Pokémon (tipos, stats base, habilidades, movimentos principais, peso, altura)
- buscar_fraquezas_tipo: relações completas de dano de um tipo (forte contra, fraco contra, resistente, imune)
- buscar_movimento: detalhes de ataques (poder, precisão, classe physical/special/status, prioridade, efeito)
- buscar_habilidade: efeito detalhado de uma habilidade e quem a possui
- buscar_cadeia_evolucao: árvore evolutiva completa a partir de um Pokémon base
- buscar_natureza: efeitos nos atributos (+10% e -10%) de uma Nature competitiva

MEMÓRIA DE CONVERSAÇÃO (PASSO 5):
- Você possui memória contínua das mensagens anteriores desta sessão. Lembre-se do que já foi discutido, dos planos traçados e das preferências do treinador.
- Use o contexto passado para enriquecer os conselhos sem precisar pedir que o treinador repita tudo.

SEUS OBJETIVOS:
1. Usar as ferramentas apropriadas para embasar todas as suas análises competitivas.
2. Identificar fortalezas, fraquezas e coberturas valorizando as qualidades de {dados_eevee['nome']} e o time de Eeveelutions.
3. Responder sempre em Português Brasileiro, de forma didática, dinâmica e inspiradora.
4. Manter as respostas concisas (no máximo 2 a 3 parágrafos por turno).
5. Enriquecer as análises utilizando emojis temáticos de Pokémon e combate (incluindo o seu emoji {dados_eevee['emoji']}, ⚔️, 🛡️, etc.) para tornar a leitura mais visual e cativante.
"""


def escolher_eeveelution() -> dict:
    """Apresenta o menu para o usuário selecionar qual Eeveelution estará em foco."""
    print("\n" + "=" * 70)
    print("🐾 CENTRO TÁTICO EEVEELUTIONS - SELEÇÃO DE PARCEIRO 🐾")
    print("=" * 70)
    print("Escolha qual Eeveelution será o foco da sua estratégia hoje:\n")

    for key, info in EEVEELUTIONS.items():
        destaque = " (⭐ Favorito deste usuário)" if info["nome"] == "Umbreon" else ""
        print(f"  [{key}] {info['emoji']} {info['nome']} ({info['tipo'].title()}) - {info['titulo']}{destaque}")

    print("\n" + "-" * 70)
    escolha = input("Digite o número (1-8) ou nome [Padrão: 1 - Umbreon]: ").strip().lower()

    for key, info in EEVEELUTIONS.items():
        if escolha == key or escolha == info["nome"].lower():
            return info

    return EEVEELUTIONS["1"]


def instanciar_agente(dados_eevee: dict) -> Agent:
    """Cria e retorna o agente configurado com modelo, prompt, ferramentas e memória de sessão."""
    system_prompt = criar_prompt_de_sistema(dados_eevee)

    # Cada Eeveelution possui seu próprio histórico de memória persistente
    session_id = f"chat_{dados_eevee['nome'].lower()}"
    session_manager = FileSessionManager(
        session_id=session_id,
        storage_dir="./sessions",
    )

    return Agent(
        model=modelo,
        system_prompt=system_prompt,
        tools=TOOLS_DISPONIVEIS,
        session_manager=session_manager,
        callback_handler=callback_handler,
    )


def exibir_badge_resposta(dados_eevee: dict):
    """Exibe o avatar Braille e cabeçalho temático no momento da resposta do parceiro."""
    print("\n" + "─" * 60)
    print(f"{dados_eevee['emoji']}  {dados_eevee['nome'].upper()} ── {dados_eevee['titulo']}")
    print("─" * 60)
    print(dados_eevee["art"])
    print("─" * 60)
    print(f"🐾 Estrategista ({dados_eevee['nome']}): ", end="", flush=True)


def main():
    dados_eevee = escolher_eeveelution()
    nome = dados_eevee["nome"]
    emoji = dados_eevee["emoji"]

    agente = instanciar_agente(dados_eevee)

    print("\n" + "=" * 70)
    print(f"{emoji} PARCEIRO INVOCADO: {nome.upper()} ({dados_eevee['tipo'].title()}) {emoji}")
    print(f"Título: {dados_eevee['titulo']}")
    print("Comandos: 'sair' para encerrar | 'trocar' para mudar de parceiro | 'arte' para rever a arte")
    print("=" * 70)

    # Exibe a arte de entrada do Pokémon escolhido
    print("\n" + dados_eevee["art"] + "\n")

    # Demonstração contextualizada inicial
    pergunta_inicial = dados_eevee["pergunta_demo"]
    print(f"{emoji} Treinador: {pergunta_inicial}")
    exibir_badge_resposta(dados_eevee)
    agente(pergunta_inicial)
    print("\n\n" + "=" * 70 + "\n")

    # Loop de conversação interativa
    while True:
        try:
            pergunta = input(f"{emoji} Treinador: ")
        except (KeyboardInterrupt, EOFError):
            print(f"\n{dados_eevee['despedida']}")
            break

        pergunta_limpa = pergunta.strip().lower()

        if pergunta_limpa in ("sair", "exit", "quit"):
            print(dados_eevee["despedida"])
            break

        if pergunta_limpa in ("arte", "art", "desenho"):
            print("\n" + dados_eevee["art"] + "\n")
            continue

        if pergunta_limpa in ("trocar", "switch", "mudar"):
            dados_eevee = escolher_eeveelution()
            emoji = dados_eevee["emoji"]
            nome = dados_eevee["nome"]
            agente = instanciar_agente(dados_eevee)
            print(f"\n{emoji} Agora o foco estratégico está em {nome.upper()}! {emoji}\n")
            print(dados_eevee["art"] + "\n")
            continue

        if not pergunta.strip():
            continue

        # Exibe o card/avatar Braille antes da resposta estratégica da Eeveelution
        exibir_badge_resposta(dados_eevee)
        agente(pergunta)
        print("\n")


if __name__ == "__main__":
    main()
