import os
import asyncio
import requests
from threading import Thread
from flask import Flask
from telethon import TelegramClient, events

# --- Configuración de Flask para el puerto web de Render ---
app = Flask(__name__)

@app.route('/')
def home():
    return "¡Bot multi-grupo de Telegram activo en Render!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- Configuración de tus credenciales ---
TELEGRAM_TOKEN = '8338001754:AAF3y73oDviZ2MaPa0YX9Xm06IguL8RFTys'
CHAT_ID = '6257969943'
API_ID = 38117391
API_HASH = 'd6c8c66bf42e53f2c0ef54a6d11c6378'

client = TelegramClient('sesion_carlos', API_ID, API_HASH)

# Lista de grupos o canales que quieres monitorear simultáneamente
# Puedes agregar tantos usernames sin el '@' como quieras en esta lista:
GRUPOS_MONITOR = ['E_positivo', 'SubastasVE']

def enviar_mensaje(texto):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': texto, 'parse_mode': 'Markdown'}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f'Error al enviar alerta: {e}')

@client.on(events.NewMessage)
async def procesar_mensaje(event):
    try:
        # Obtenemos la información del chat donde se escribió el mensaje
        chat = await event.get_chat()
        username_chat = getattr(chat, 'username', None)
        titulo_chat = getattr(chat, 'title', 'Chat sin título')

        # Verificamos si el mensaje viene de alguno de los grupos de nuestra lista
        if username_chat and username_chat in GRUPOS_MONITOR:
            texto = event.text or "[Contenido multimedia / sin texto]"
            
            # Filtro opcional por palabras clave si el grupo es muy ruidoso, 
            # o lo dejamos directo para que te avise de todo lo que escriban:
            enviar_mensaje(f"🚨 **ALERTA DESDE [{titulo_chat}]** 🚨\n\n{texto}")
            
    except Exception as e:
        print(f"Error procesando evento: {e}")

async def main():
    # 1. Levantar servidor web para Render
    web_thread = Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()
    print("Servidor web iniciado en segundo plano.")

    # 2. Iniciar cliente de Telethon
    await client.start()
    print("Cliente de Telegram conectado exitosamente. Monitoreando grupos...")
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
