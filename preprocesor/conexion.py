import os
import asyncio
import threading
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from pyngrok import ngrok
import requests

from principal import responder_a_consulta, inicializar_bot

# --- Abre túnel con ngrok ---
tunnel = ngrok.connect(addr=5000, proto="http", bind_tls=True)
public_url = tunnel.public_url   # <- aquí la URL en string
WEBHOOK_URL = f"{public_url}/webhook"
print("🌍 Webhook público:", WEBHOOK_URL)


# --- Configuración ---
TOKEN = "7640980967:AAH2dSSczf-a6_3DSGNMZoDfOkABEou7onc"

# --- Inicializar Flask ---
app = Flask(__name__)

# --- Inicializar Bot ---
tg_app = Application.builder().token(TOKEN).build()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy tu asistente virtual 🤖 \nSi quieres saber consultas pon /consultas y apaeceran las mas utilizadas")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Comandos: /start /help /status /consultas")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot en funcionamiento")

# --- Menú de consultas frecuentes ---
async def menu_consultas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("📅 ¿Cuál es la fecha de los finales?")],
        [KeyboardButton("📍 ¿Como inscribirse a nuevas materias?")],
        [KeyboardButton("💵 ¿Cómo puedo solicitar una constancia de alumno regular?")],
        [KeyboardButton("ℹ️ ¿Cómo puedo presentar una solicitud para una revisión de examen o nota en una materia?")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Elegí una consulta:", reply_markup=reply_markup)

# --- IA responde mensajes ---

async def responder_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    processing_msg = await update.message.reply_text("🔄 Procesando...")

    try:
        # Ejecutar la función bloqueante en un thread aparte
        respuesta = await asyncio.to_thread(responder_a_consulta, msg)

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


# Registrar handlers
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CommandHandler("help", help_command))
tg_app.add_handler(CommandHandler("status", status))
tg_app.add_handler(CommandHandler("consultas", menu_consultas))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_mensaje))

# --- Rutas Flask ---
@app.route("/", methods=["GET"])
def index():
    return "🤖 Bot Flask-Telegram corriendo"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), tg_app.bot)
        asyncio.run_coroutine_threadsafe(tg_app.process_update(update), loop)
    except Exception as e:
        print(f"Error en webhook: {e}")
    return "ok", 200

# --- Función para correr el bot en un thread ---
def run_bot():
    loop.run_until_complete(tg_app.initialize())
    loop.run_until_complete(tg_app.start())
    loop.run_forever()

# --- Main ---
if __name__ == "__main__":
    inicializar_bot()  # FAISS/embeddings
    print("🌍 URL ngrok generada:", public_url)

    # Arrancar el bot en un thread aparte
    threading.Thread(target=run_bot, daemon=True).start()

    # Establecer webhook en Telegram
    requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true")
    r = requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}")
    print("Webhook set:", r.json())

    print("🚀 Servidor Flask corriendo...")

    # ⚡ Evita el crash de colorama/click en Windows
    app.run(host="0.0.0.0", port=5000, use_reloader=False)

