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
    return "¡Bot activo y rápido!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- Configuración de Credenciales ---
TELEGRAM_TOKEN = '8338001754:AAF3y73oDviZ2MaPa0YX9Xm06IguL8RFTys'
CHAT_ID = '6257969943'
API_ID = 38117391
API_HASH = 'd6c8c66bf42e53f2c0ef54a6d11c6378'

client = TelegramClient('sesion_carlos', API_ID, API_HASH)

# Lista completa de canales y grupos a monitorear
GRUPOS_MONITOR = ['E_positivo', 'SubastasVE', 'subastasBCV']

def enviar_mensaje_sync(texto):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': texto, 'parse_mode': 'Markdown'}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f'Error al enviar: {e}')

@client.on(events.NewMessage)
async def procesar_mensaje(event):
    try:
        chat = await event.get_chat()
        username_chat = getattr(chat, 'username', None)
        titulo_chat = getattr(chat, 'title', 'Chat')

        # Compara sin importar mayúsculas/minúsculas
        if username_chat and any(username_chat.lower() == g.lower() for g in GRUPOS_MONITOR):
            texto = event.text or "[Multimedia/Sin texto]"
            # Envía de forma inmediata sin bloquear el flujo principal
            await asyncio.to_thread(enviar_mensaje_sync, f"⚡ **ALERTA [{titulo_chat}]** ⚡\n\n{texto}")
            
    except Exception as e:
        print(f"Error: {e}")

async def main():
    # 1. Iniciar servidor Flask en segundo plano
    web_thread = Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()

    # 2. Iniciar cliente de Telegram
    await client.start()
    print("Bot activo monitoreando múltiples grupos a máxima velocidad...")
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
