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
    return "¡Bot activo multi-grupo y comunidad!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- Configuración de Credenciales ---
TELEGRAM_TOKEN = '8338001754:AAF3y73oDviZ2MaPa0YX9Xm06IguL8RFTys'
CHAT_ID = '6257969943'
API_ID = 38117391
API_HASH = 'd6c8c66bf42e53f2c0ef54a6d11c6378'

client = TelegramClient('sesion_carlos', API_ID, API_HASH)

# Canales públicos por su username
GRUPOS_USERNAMES = ['E_positivo', 'SubastasVE', 'subastasBCV']
# Enlace de invitación para la comunidad privada
ENLACE_INVITACION = 'https://t.me/+ad6dNv0My50yZjIx'

# Almacenará los IDs numéricos de todos los chats permitidos
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
        # Si el chat_id está dentro de nuestra lista dinámica permitida, procesamos
        if event.chat_id in chats_permitidos_ids:
            chat = await event.get_chat()
            titulo_chat = getattr(chat, 'title', 'Comunidad/Grupo')
            texto = event.text or "[Multimedia/Sin texto]"
            
            await asyncio.to_thread(enviar_mensaje_sync, f"⚡ **ALERTA [{titulo_chat}]** ⚡\n\n{texto}")
            
    except Exception as e:
        print(f"Error procesando mensaje: {e}")

async def main():
    global chats_permitidos_ids

    # 1. Iniciar servidor Flask en segundo plano
    web_thread = Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()

    # 2. Iniciar cliente de Telegram
    await client.start()
    print("Cliente de Telegram conectado. Resolviendo canales...")

    # 3. Resolver los canales públicos por username
    for username in GRUPOS_USERNAMES:
        try:
            entity = await client.get_entity(username)
            chats_permitidos_ids.add(entity.id)
            print(f"Canal público agregado: {username} (ID: {entity.id})")
        except Exception as e:
            print(f"No se pudo resolver el canal {username}: {e}")

    # 4. Resolver la comunidad privada mediante el enlace de invitación
    try:
        from telethon.tl.functions.messages import ImportChatInviteRequest
        invite_hash = ENLACE_INVITACION.split('+')[-1]
        
        try:
            updates = await client(ImportChatInviteRequest(invite_hash))
            chat_privado = updates.chats[0]
            chats_permitidos_ids.add(chat_privado.id)
            print(f"¡Comunidad privada agregada exitosamente! (ID: {chat_privado.id})")
        except Exception:
            entity_privada = await client.get_entity(ENLACE_INVITACION)
            chats_permitidos_ids.add(entity_privada.id)
            print(f"¡Comunidad privada ya vinculada previamente! (ID: {entity_privada.id})")
            
    except Exception as e:
        print(f"Error al procesar el enlace de invitación privado: {e}")

    print("¡Sistema 100% operativo escuchando todas las fuentes!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
