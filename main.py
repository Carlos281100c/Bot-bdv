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
    return "¡Bot activo y depurando chats!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- Configuración de Credenciales ---
TELEGRAM_TOKEN = '8338001754:AAF3y73oDviZ2MaPa0YX9Xm06IguL8RFTys'
CHAT_ID = '6257969943'
API_ID = 38117391
API_HASH = 'd6c8c66bf42e53f2c0ef54a6d11c6378'

client = TelegramClient('sesion_carlos', API_ID, API_HASH)

GRUPOS_USERNAMES = ['E_positivo', 'SubastasVE', 'subastasBCV']
ENLACE_INVITACION = 'https://t.me/+ad6dNv0My50yZjIx'

chats_permitidos_ids = set()

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
        # Imprimimos CADA chat que emita un mensaje para ver su ID en vivo en los logs de Render
        print(f"Mensaje detectado -> chat_id: {event.chat_id} | texto: {event.text}")

        # Si coincide con nuestros IDs permitidos, o si queremos forzar la captura temporalmente para probar:
        if event.chat_id in chats_permitidos_ids:
            chat = await event.get_chat()
            titulo_chat = getattr(chat, 'title', 'Comunidad/Grupo')
            texto = event.text or "[Multimedia/Sin texto]"
            
            await asyncio.to_thread(enviar_mensaje_sync, f"⚡ **ALERTA [{titulo_chat}]** ⚡\n\n{texto}")
            
    except Exception as e:
        print(f"Error procesando mensaje: {e}")

async def main():
    global chats_permitidos_ids

    web_thread = Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()

    await client.start()
    print("Cliente conectado. Resolviendo entidades...")

    # Resolver canales públicos
    for username in GRUPOS_USERNAMES:
        try:
            entity = await client.get_entity(username)
            chats_permitidos_ids.add(entity.id)
            print(f"Público OK -> {username} ID: {entity.id}")
        except Exception as e:
            print(f"Error en {username}: {e}")

    # Resolver comunidad privada por enlace
    try:
        entity_privada = await client.get_entity(ENLACE_INVITACION)
        chats_permitidos_ids.add(entity_privada.id)
        print(f"¡Comunidad Privada OK! ID: {entity_privada.id}")
    except Exception as e:
        print(f"No se pudo resolver el enlace privado directamente: {e}")
        # Plan B: Buscamos en las diálogos recientes en los que participas
        async for dialog in client.iter_dialogs(limit=30):
            if dialog.is_group or dialog.is_channel:
                # Añadimos los chats activos temporalmente para mapearlos
                chats_permitidos_ids.add(dialog.id)
                print(f"Chat añadido desde diálogos: {dialog.name} (ID: {dialog.id})")

    print(f"IDs permitidos finales cargados: {chats_permitidos_ids}")
    print("¡Escuchando eventos en tiempo real!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
