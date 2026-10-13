import os
import asyncio
import requests
from threading import Thread
from flask import Flask
from telethon import TelegramClient, events

# --- Configuración de Flask para Render ---
app = Flask(__name__)

@app.route('/')
def home():
    return "¡Bot activo probando en E_positivo!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- Configuración del Bot ---
TELEGRAM_TOKEN = '8338001754:AAF3y73oDviZ2MaPa0YX9Xm06IguL8RFTys'
CHAT_ID = '6257969943'
API_ID = 38117391
API_HASH = 'd6c8c66bf42e53f2c0ef54a6d11c6378'

client = TelegramClient('sesion_carlos', API_ID, API_HASH)

# Guardaremos el ID numérico del grupo aquí una vez que conecte
target_chat_id = None

def enviar_mensaje(texto):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': texto, 'parse_mode': 'Markdown'}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f'Error: {e}')

@client.on(events.NewMessage)
async def procesar_anuncio(event):
    global target_chat_id
    # Verificamos si el mensaje viene exactamente del grupo E_positivo
    if target_chat_id and event.chat_id == target_chat_id:
        texto = event.text
        enviar_mensaje(f"⚡ **PRUEBA EN VIVO (E_positivo)** ⚡\n\n{texto}")

async def main():
    global target_chat_id
    web_thread = Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()

    # 1. Iniciamos sesión en Telethon
    await client.start()
    print("Escuchador iniciado en la nube...")

    # 2. Buscamos y resolvemos el grupo de forma segura ya estando conectados
    try:
        entity = await client.get_entity('E_positivo')
        target_chat_id = entity.id
        print(f"¡Grupo E_positivo conectado exitosamente con ID: {target_chat_id}!")
    except Exception as e:
        print(f"Error al buscar el grupo E_positivo: {e}")

    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
