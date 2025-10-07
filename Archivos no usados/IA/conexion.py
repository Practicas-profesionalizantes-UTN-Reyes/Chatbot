import os
import json
import asyncio
import threading
import concurrent.futures
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from pyngrok import ngrok
import requests
from waitress import serve   # ✅ en lugar de app.run()

from principal import responder_a_consulta, inicializar_bot

# --- Archivos ---
RESPUESTAS_FILE = "respuestas.json"

def cargar_respuestas():
    """
    Carga las respuestas guardadas en un archivo JSON.
    Si no existe o está vacío, devuelve {}.
    """
    if os.path.exists(RESPUESTAS_FILE):
        with open(RESPUESTAS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def guardar_respuesta(pregunta, respuesta):
    """
    Guarda una nueva pregunta y su respuesta en el archivo JSON.
    Se guarda la pregunta en minúsculas para evitar duplicados.
    """
    data = cargar_respuestas()
    data[pregunta.lower()] = respuesta
    with open(RESPUESTAS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- Abre túnel con ngrok ---
tunnel = ngrok.connect(addr=5000, proto="http", bind_tls=True)
public_url = tunnel.public_url
WEBHOOK_URL = f"{public_url}/webhook"
print("🌍 Webhook público:", WEBHOOK_URL)

# --- Configuración ---
TOKEN = "7640980967:AAH2dSSczf-a6_3DSGNMZoDfOkABEou7onc"

# --- Inicializar Flask ---
app = Flask(__name__)

# --- Inicializar Bot ---
tg_app = Application.builder().token(TOKEN).build()

# Loop exclusivo para el bot
bot_loop = asyncio.new_event_loop()

# --- Pool de hilos para consultas simultáneas ---
executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)  # ✅ hasta 10 en paralelo

# --- Handlers de comandos ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start → mensaje de bienvenida"""
    await update.message.reply_text("¡Hola! Soy tu asistente virtual 🤖 \nPara saber las consultas más utilizadas: /consultas")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help → lista de comandos"""
    await update.message.reply_text("Comandos: /start /help /status /consultas")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /status → verifica si el bot está en funcionamiento"""
    await update.message.reply_text("✅ Bot en funcionamiento")

# --- Menú de consultas frecuentes ---
async def menu_consultas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /consultas → muestra botones con preguntas frecuentes"""
    keyboard = [
        [KeyboardButton("¿Quiénes pueden solicitarlo?")],
        [KeyboardButton("¿Cómo me inscribo a nuevas materias?")],
        [KeyboardButton("¿Cómo puedo solicitar una constancia de alumno regular?")],
        [KeyboardButton("¿Cómo puedo presentar una solicitud para una revisión de examen o nota en una materia?")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Elige una consulta:", reply_markup=reply_markup)

# --- IA responde mensajes ---
async def responder_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler principal:
    1. Busca si la respuesta está guardada en JSON.
    2. Si no, pregunta a la IA (responder_a_consulta) usando un thread.
    3. Guarda la respuesta nueva en el archivo.
    """
    msg = update.message.text.strip()
    processing_msg = await update.message.reply_text("🔄 Procesando...")

    try:
        respuestas_guardadas = cargar_respuestas()
        respuesta = respuestas_guardadas.get(msg.lower())

        if not respuesta:
            # Si no existe, usar la IA en un thread separado
            loop = asyncio.get_event_loop()
            respuesta = await loop.run_in_executor(executor, responder_a_consulta, msg)
            guardar_respuesta(msg, respuesta)

        # Edita el mensaje de "Procesando..." con la respuesta final
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=processing_msg.message_id,
            text=respuesta
        )
    except Exception as e:
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=processing_msg.message_id,
            text=f"❌ Error: {e}"
        )

# --- Registro de handlers ---
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CommandHandler("help", help_command))
tg_app.add_handler(CommandHandler("status", status))
tg_app.add_handler(CommandHandler("consultas", menu_consultas))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_mensaje))

# --- Rutas Flask ---
@app.route("/", methods=["GET"])
def index():
    """Ruta principal → confirma que el servidor está corriendo"""
    return "🤖 Bot Flask-Telegram corriendo"

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Ruta para recibir actualizaciones de Telegram vía webhook.
    Convierte el JSON recibido en un objeto Update y lo procesa con el bot.
    """
    try:
        update = Update.de_json(request.get_json(force=True), tg_app.bot)
        asyncio.run_coroutine_threadsafe(tg_app.process_update(update), bot_loop)
    except Exception as e:
        print(f"Error en webhook: {e}")
    return "ok", 200

# --- Función para correr el bot en un hilo separado ---
def run_bot():
    """Arranca el loop del bot y lo mantiene en ejecución"""
    asyncio.set_event_loop(bot_loop)
    bot_loop.run_until_complete(tg_app.initialize())
    bot_loop.run_until_complete(tg_app.start())
    bot_loop.run_forever()

# --- Main ---
if __name__ == "__main__":
    inicializar_bot()  # ✅ Inicializa embeddings / FAISS
    print("🌍 URL ngrok generada:", public_url)

    # Correr el bot en un thread aparte
    threading.Thread(target=run_bot, daemon=True).start()

    # Configurar webhook en Telegram
    requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true")
    r = requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}")
    print("Webhook set:", r.json())

    print("🚀 Servidor Flask corriendo con waitress...")

    # ✅ Usamos waitress en lugar de app.run()
    serve(app, host="0.0.0.0", port=5000)
