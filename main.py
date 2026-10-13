import asyncio
import requests
from telethon import TelegramClient, events

TELEGRAM_TOKEN = '8338001754:AAF3y73oDviZ2MaPa0YX9Xm06IguL8RFTys'
CHAT_ID = '6257969943'
API_ID = 38117391
API_HASH = 'd6c8c66bf42e53f2c0ef54a6d11c6378'

client = TelegramClient('sesion_carlos', API_ID, API_HASH)
CANAL = 'SubastasVE'
ultimos_mensajes = []

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
    texto_lower = texto.lower()
    palabras_clave = ['abierto', 'intervencion', 'menudeo', 'disponible', 'activo']
    if any(p in texto_lower for p in palabras_clave):
        ultimos_mensajes.append(texto)
        if len(ultimos_mensajes) > 10:
            ultimos_mensajes.pop(0)
        enviar_mensaje(f"🚨 **NUEVA INTERVENCIÓN DETECTADA** 🚨\n\n{texto}")

async def main():
    await client.start()
    print("Escuchador iniciado en la nube...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
