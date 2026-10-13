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
    return "¡Bot activo probando en grupo concurrido!" 

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- Configuración del Bot ---
TELEGRAM_TOKEN = '8338001754:AAF3y73oDviZ2MaPa0YX9Xm06IguL8RFTys'
CHAT_ID = '6257969943'
API_ID = 38117391
API_HASH = 'd6c8c66bf42e53f2c0ef54a6d11c6378'

client = TelegramClient('sesion_carlos', API_ID, API_HASH)

# Grupo público y muy activo para la prueba
CANAL = 'TelethonChat'

def enviar_mensaje(texto):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': texto, 'parse_mode': 'Markdown'}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f'Error: {e}')

@client.on(events.NewMessage(chats=CANAL))
async def procesar_anuncio(event):
    texto = event.text
    # Reenvía los mensajes del grupo a tu Telegram privado
    enviar_mensaje(f"⚡ **PRUEBA EN VIVO (TelethonChat)** ⚡\n\n{texto}")

async def main():
    web_thread = Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()

    await client.start()
    print("Escuchando el grupo activo TelethonChat...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
