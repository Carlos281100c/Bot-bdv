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
    return "¡Bot inteligente filtrando BDV activo!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- Configuración de Credenciales ---
TELEGRAM_TOKEN = '8338001754:AAF3y73oDviZ2MaPa0YX9Xm06IguL8RFTys'
CHAT_ID = '6257969943'
API_ID = 38117391
API_HASH = 'd6c8c66bf42e53f2c0ef54a6d11c6378'

client = TelegramClient('sesion_carlos', API_ID, API_HASH)

# Canales públicos prioritarios
GRUPOS_MONITOR = ['E_positivo', 'SubastasVE', 'subastasBCV']

# Palabras clave obligatorias para que una notificación sea considerada relevante (en minúsculas)
PALABRAS_CLAVE = [
    'abrio', 'abrió', 'bdv', 'banco de venezuela', 'comprar', 'compra', 
    'intervencion', 'intervención', 'mesa', 'tasa', 'divisas', 'disponible'
]

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
        titulo_chat = getattr(chat, 'title', 'Comunidad/Grupo')
        texto = event.text or ""
        texto_lower = texto.lower()

        # 1. Si viene de los canales oficiales de subastas/alertas, lo mandamos de una vez
        if username_chat and any(username_chat.lower() == g.lower() for g in GRUPOS_MONITOR):
            if texto.strip():
                await asyncio.to_thread(enviar_mensaje_sync, f"⚡ **ALERTA OFICIAL [{titulo_chat}]** ⚡\n\n{texto}")

        # 2. Si viene de la comunidad privada (u otros grupos), aplicamos el filtro inteligente
        elif event.is_group or event.is_channel:
            # Verificamos si el mensaje contiene al menos una de las palabras clave del BDV
            es_relevante = any(palabra in texto_lower for palabra in PALABRAS_CLAVE)
            
            if es_relevante:
                await asyncio.to_thread(enviar_mensaje_sync, f"🚨 **¡POSIBLE APERTURA BDV! [{titulo_chat}]** 🚨\n\n{texto}")

    except Exception as e:
        print(f"Error procesando mensaje: {e}")

async def main():
    web_thread = Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()

    await client.start()
    print("¡Bot inteligente conectado y filtrando mensajes de ruido!")
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
