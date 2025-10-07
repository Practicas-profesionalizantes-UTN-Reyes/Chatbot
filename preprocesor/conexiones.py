# ===================== IMPORTS =====================
# Librerías estándar y externas que usa el proyecto
import os
import json
import asyncio
import threading
import concurrent.futures
from pathlib import Path
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from pyngrok import ngrok
import requests
from waitress import serve
from principal import responder_a_consulta   # función IA para responder consultas

# ===================== ARCHIVOS =====================
# Archivos de preguntas/respuestas (JSON)
RESPUESTAS_FILE = "preguntas_respuestas.json"
RESPUESTAS_PATHS = [Path("./data/output/respuestas.json")]

# ===================== FUNCIONES PARA JSON =====================
def cargar_respuestas() -> dict:
    """
    Carga el archivo JSON de preguntas/respuestas desde la primera ruta disponible.
    Si no existe o es inválido, devuelve {}.
    """
    for p in RESPUESTAS_PATHS:
        try:
            if p.exists():
                with p.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    print(f"✅ Cargadas {len(data)} preguntas desde: {p}")
                    return data
        except json.JSONDecodeError:
            print(f"⚠️ JSON inválido en: {p}")
    print("⚠️ No se encontró ningún archivo de preguntas.")
    return {}

def guardar_respuesta(pregunta, respuesta):
    """
    Guarda una nueva pregunta/respuesta en el archivo JSON principal.
    """
    data = cargar_respuestas()
    data[pregunta] = respuesta
    with open(RESPUESTAS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ===================== CATEGORÍAS =====================
# Categorías predefinidas de preguntas
# Solo se mostrarán si tienen preguntas en el JSON cargado
CATEGORIAS_DEF = {
    "🧾 Legajo y Libreta": [
        "Cómo obtener el legajo definitivo",
        "Cómo tramitar la libreta",
        "Dónde retirar la documentación para iniciar el trámite de la libreta",
    ],
    "📚 Inscripciones y Materias": [
        "Cómo me inscribo a las materias",
        "Cómo me inscribo a un final",
        "Cómo me inscribo a una carrera",
    ],
    "🚍 Boleto estudiantil": [
        "Quiénes pueden solicitar el boleto estudiantil",
        "Cómo lo renuevo si ya tengo el boleto estudiantil",
        "Cómo lo solicito por primera vez, al boleto estudiantil",
        "Dónde hacer el reclamo, si tengo problemas con el boleto estudiantil",
        "Qué hacer si pierdo o me roban la SUBE",
    ],
    "🎓 Becas (Manuel Belgrano / Progresar)": [
        "Quiénes pueden aplicar a las Becas Manuel Belgrano",
        "Cuáles son los requisitos, para las Becas Manuel Belgrano",
        "Cómo hacer los reclamos para las Becas Manuel Belgrano",
        "Dónde completar el formulario de Becas PROGRESAR",
        "A qué becas puedo aplicar",
    ],
    "📄 Certificados y Constancias": [
        "Dónde solicitar el Certificado de Alumno Regular",
        "Dónde solicitar el Certificado Académico/Analítico",
        "Dónde solicitar constancia de título en trámite",
    ],
    "🗓️ Calendario y Fechas": [
        "Dónde miro las fechas de finales",
        "Dónde miro la fecha de receso",
        "Dónde encuentro el calendario académico",
        "Cuándo arranca el ciclo lectivo",
    ],
    "🗺️ Ubicaciones en la Facultad": [
        "Dónde están ubicadas las aulas",
        "Dónde queda las secretarias",
        "Dónde queda los departamentos de cada carrera",
        "Dónde está la fotocopiadora",
        "Dónde está la doctora",
    ],
    "📑 Planes de estudio y Carreras": [
        "Dónde me fijo los planes de estudio de mi carrera",
    ],
    "🖥️ Sistemas y Accesos": [
        "Cómo acceder al Sysacad",
        "Cómo acceder al Campus Virtual",
        "Cómo tramitar el correo institucional para obtener al paquete office 365",
    ],
    "ℹ️ General": [
        "Qué significa ser Alumno Regular de la carrera",
        "A qué cursos extracurriculares puedo aplicar",
    ],
}

def filtrar_categorias_por_json(respuestas: dict) -> dict:
    """
    Filtra las categorías, dejando solo aquellas preguntas
    que existan realmente en el JSON cargado.
    """
    filtradas = {}
    keys = set(respuestas.keys())
    for cat, preguntas in CATEGORIAS_DEF.items():
        presentes = [p for p in preguntas if p in keys]
        if presentes:
            filtradas[cat] = presentes
    return filtradas

# ===================== MENÚS TELEGRAM =====================
def kb_categorias(categorias: dict) -> ReplyKeyboardMarkup:
    """
    Construye el teclado de categorías (2 botones por fila).
    """
    botones = []
    fila = []
    for cat in categorias.keys():
        fila.append(KeyboardButton(cat))
        if len(fila) == 2:
            botones.append(fila)
            fila = []
    if fila:
        botones.append(fila)
    return ReplyKeyboardMarkup(botones, resize_keyboard=True)

def kb_preguntas(preguntas: list) -> ReplyKeyboardMarkup:
    """
    Construye el teclado de preguntas dentro de una categoría.
    - Si la pregunta es larga: va sola en una fila.
    - Si es corta: se muestran de a 2.
    - Agrega botones de navegación (⬅️ Volver, 🏠 Inicio).
    """
    botones = []
    fila = []
    for q in preguntas:
        if len(q) > 28:
            if fila:
                botones.append(fila)
                fila = []
            botones.append([KeyboardButton(q)])
        else:
            fila.append(KeyboardButton(q))
            if len(fila) == 2:
                botones.append(fila)
                fila = []
    if fila:
        botones.append(fila)
    botones.append([KeyboardButton("⬅️ Volver"), KeyboardButton("🏠 Inicio")])
    return ReplyKeyboardMarkup(botones, resize_keyboard=True)

# ===================== NGROK (URL pública) =====================
# Se abre un túnel con ngrok para recibir mensajes de Telegram
tunnel = ngrok.connect(addr=5000, proto="http", bind_tls=True)
public_url = tunnel.public_url
WEBHOOK_URL = f"{public_url}/webhook"
print("🌍 Webhook público:", WEBHOOK_URL)

# ===================== CONFIGURACIÓN BOT =====================
TOKEN = "7640980967:AAH2dSSczf-a6_3DSGNMZoDfOkABEou7onc"  # Token del bot

# Inicializamos Flask y el Bot
app = Flask(__name__)
tg_app = Application.builder().token(TOKEN).build()

# Loop y ThreadPool
bot_loop = asyncio.new_event_loop()
executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

# ===================== HANDLERS DEL BOT =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /start → Muestra menú de categorías inicial.
    """
    respuestas = cargar_respuestas()
    categorias = filtrar_categorias_por_json(respuestas)
    context.user_data.clear()
    context.user_data["categorias"] = categorias

    if not categorias:
        await update.message.reply_text(
            "No encontré preguntas para armar el menú.\n"
            "Verificá que exista alguno de estos archivos:\n"
            "• ./data/output/respuestas.json\n"
            "• ./preguntas_respuestas.json"
        )
        return

    await update.message.reply_text(
        "¡Hola! Soy tu asistente virtual 🤖\nElegí un tema:",
        reply_markup=kb_categorias(categorias)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help → Muestra lista de comandos disponibles."""
    await update.message.reply_text("Comandos: /start /help /status /consultas")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /status → Verifica que el bot está funcionando."""
    await update.message.reply_text("✅ Bot en funcionamiento")

async def menu_consultas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /consultas → Muestra menú principal de categorías nuevamente.
    """
    respuestas = cargar_respuestas()
    categorias = filtrar_categorias_por_json(respuestas)
    context.user_data["categorias"] = categorias
    context.user_data.pop("tema_actual", None)

    if not categorias:
        await update.message.reply_text(
            "No encontré preguntas para armar el menú.\n"
            "Verificá que exista alguno de estos archivos:\n"
            "• ./data/output/respuestas.json\n"
            "• ./preguntas_respuestas.json"
        )
        return

    await update.message.reply_text(
        "📚 Preguntas frecuentes por tema:",
        reply_markup=kb_categorias(categorias)
    )

def es_categoria(texto: str, categorias: dict) -> bool:
    """Verifica si el texto coincide con una categoría."""
    return texto in categorias

async def responder_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler principal para mensajes de texto:
    - Navegación entre categorías/preguntas.
    - Si el mensaje es una pregunta conocida: responde desde el JSON.
    - Si no está: consulta a la IA, responde y guarda en el JSON.
    """
    msg = (update.message.text or "").strip()
    respuestas = cargar_respuestas()
    categorias = context.user_data.get("categorias") or filtrar_categorias_por_json(respuestas)

    # Navegación
    if msg == "🏠 Inicio":
        context.user_data.clear()
        context.user_data["categorias"] = filtrar_categorias_por_json(respuestas)
        await update.message.reply_text("Elegí un tema:", reply_markup=kb_categorias(context.user_data["categorias"]))
        return

    if msg == "⬅️ Volver":
        context.user_data.pop("tema_actual", None)
        context.user_data["categorias"] = filtrar_categorias_por_json(respuestas)
        await update.message.reply_text("Volvés al menú por temas:", reply_markup=kb_categorias(context.user_data["categorias"]))
        return

    # Si es categoría → mostrar submenú
    if es_categoria(msg, categorias):
        context.user_data["tema_actual"] = msg
        preguntas = categorias[msg]
        await update.message.reply_text(f"Temas: {msg}\nElegí una pregunta:", reply_markup=kb_preguntas(preguntas))
        return

    # Si es pregunta → mostrar respuesta
    tema_actual = context.user_data.get("tema_actual")
    if tema_actual:
        preguntas = categorias.get(tema_actual, [])
        if msg in preguntas:
            respuesta = respuestas.get(msg, "No encontré la respuesta en el catálogo.")
            await update.message.reply_text(respuesta, reply_markup=kb_preguntas(preguntas))
            return
        else:
            await update.message.reply_text("Elegí una opción del menú o tocá ⬅️ Volver.", reply_markup=kb_preguntas(preguntas))
            return

    # Si no coincide con nada → consulta IA
    processing_msg = await update.message.reply_text("🔄 Procesando...")
    try:
        loop = asyncio.get_event_loop()
        respuesta = await loop.run_in_executor(executor, responder_a_consulta, msg)
        guardar_respuesta(msg, respuesta)
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

# ===================== REGISTRO DE HANDLERS =====================
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CommandHandler("help", help_command))
tg_app.add_handler(CommandHandler("status", status))
tg_app.add_handler(CommandHandler("consultas", menu_consultas))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_mensaje))

# ===================== FLASK ROUTES =====================
@app.route("/", methods=["GET"])
def index():
    """Ruta principal → simple mensaje de verificación."""
    return "🤖 Bot Flask-Telegram corriendo"

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Ruta para recibir mensajes de Telegram via Webhook.
    Convierte el JSON en un objeto Update y lo procesa con el bot.
    """
    try:
        update = Update.de_json(request.get_json(force=True), tg_app.bot)
        asyncio.run_coroutine_threadsafe(tg_app.process_update(update), bot_loop)
    except Exception as e:
        print(f"Error en webhook: {e}")
    return "ok", 200

# ===================== BOT LOOP =====================
def run_bot():
    """
    Arranca el loop del bot en un hilo separado.
    Mantiene al bot corriendo de forma asíncrona.
    """
    asyncio.set_event_loop(bot_loop)
    bot_loop.run_until_complete(tg_app.initialize())
    bot_loop.run_until_complete(tg_app.start())
    bot_loop.run_forever()

# ===================== MAIN =====================
if __name__ == "__main__":
    print("🌍 URL ngrok generada:", public_url)

    # Lanzar bot en un hilo
    threading.Thread(target=run_bot, daemon=True).start()

    # Configurar webhook en Telegram
    requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true")
    r = requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}")
    print("Webhook set:", r.json())

    # Correr Flask con waitress
    print("🚀 Servidor Flask corriendo con waitress...")
    serve(app, host="0.0.0.0", port=5000)
