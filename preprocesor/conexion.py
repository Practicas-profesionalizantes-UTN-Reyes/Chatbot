import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from principal import responder_a_consulta, inicializar_bot

# Token de BotFather (¡RECUERDA CAMBIAR ESTO!)
TOKEN = "7640980967:AAH2dSSczf-a6_3DSGNMZoDfOkABEou7onc"

# Respuesta al comando /start
async def start(update, context):
    welcome_text = """
¡Hola! 🤖 Soy tu asistente virtual.

Puedes preguntarme sobre cualquier tema relacionado con los documentos que tengo disponibles.

Ejemplos de preguntas:
• ¿Cómo obtengo la constancia de alumno regular?
• ¿Cuáles son los requisitos para...?
• ¿Dónde puedo encontrar información sobre...?

¡Estoy aquí para ayudarte! 💫
    """
    await update.message.reply_text(welcome_text)

# Respuesta al comando /help
async def help_command(update, context):
    help_text = """
📋 **Comandos disponibles:**
/start - Iniciar el bot
/help - Mostrar esta ayuda
/status - Estado del sistema

💡 **Cómo usar:**
Simplemente escribe tu pregunta y te responderé basándome en la información disponible.

⚠️ **Nota:** Solo puedo responder con información de los documentos que tengo cargados.
    """
    await update.message.reply_text(help_text)

# Respuesta al comando /status
async def status(update, context):
    status_text = """
✅ **Estado del sistema:**
• Bot: Funcionando correctamente
• Base de conocimientos: Cargada y actualizada
• Listo para responder consultas

📊 **Estadísticas:**
• Embeddings generados: Sí
• FAISS index: Activo
    """
    await update.message.reply_text(status_text)

# Manejar mensajes de texto
async def responder_mensaje(update, context):
    user_message = update.message.text
    
    # Mostrar que estamos procesando
    processing_msg = await update.message.reply_text("🔄 Procesando tu consulta...")
    
    try:
        # Obtener respuesta
        respuesta = responder_a_consulta(user_message)
        
        # Editar el mensaje de procesamiento con la respuesta final
        await context.bot.edit_message_text(
            chat_id=update.message.chat_id,
            message_id=processing_msg.message_id,
            text=respuesta
        )
        
    except Exception as e:
        error_msg = f"❌ Lo siento, ocurrió un error procesando tu consulta:\n\n{str(e)}"
        await context.bot.edit_message_text(
            chat_id=update.message.chat_id,
            message_id=processing_msg.message_id,
            text=error_msg
        )

# Manejar errores
async def error_handler(update, context):
    print(f"Error: {context.error}")
    if update and update.message:
        await update.message.reply_text("❌ Ocurrió un error inesperado. Por favor, intenta nuevamente.")

def main():
    # Inicializar el sistema
    inicializar_bot()
    
    # Conectamos con la API de Telegram
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_mensaje))
    
    # Manejo de errores
    app.add_error_handler(error_handler)

    # Arranca el bot
    print("🤖 Bot corriendo... Presiona Ctrl+C para detener")
    app.run_polling()

if __name__ == "__main__":
    main()