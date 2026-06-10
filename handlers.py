"""
Handlers de Telegram (python-telegram-bot v21, async).

Define qué hace el bot ante:
  - /start  -> bienvenida + inicializa memoria del usuario
  - /reset  -> borra el historial del usuario
  - texto   -> conversa con el LLM usando el contexto reciente
  - errores -> responde algo amigable y loguea el error real
"""

import logging

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

import config
import groq_client
import memory

logger = logging.getLogger(__name__)

# La personalidad se resuelve una sola vez al cargar el módulo.
SYSTEM_PROMPT = config.load_system_prompt()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start: mensaje de bienvenida y reinicio del contexto del usuario."""
    user_id = update.effective_user.id
    memory.reset(user_id)

    bienvenida = (
        f"¡Hola! Soy *{config.BOT_NAME}*. 🤖\n\n"
        "Hablame en lenguaje natural, como en una conversación normal — "
        "no necesitás menús ni comandos.\n\n"
        "Comandos disponibles:\n"
        "• /reset — borrar la conversación y empezar de cero\n\n"
        "¿En qué te puedo ayudar?"
    )
    await update.message.reply_text(bienvenida, parse_mode="Markdown")


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/reset: limpia el historial del usuario."""
    memory.reset(update.effective_user.id)
    await update.message.reply_text(
        "Listo, borré nuestra conversación. Empezamos de cero. ✨"
    )


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mensaje de texto normal: arma contexto, consulta al LLM y responde."""
    user_id = update.effective_user.id
    user_text = update.message.text

    # Muestra "escribiendo..." mientras genera la respuesta.
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING
    )

    memory.add(user_id, "user", user_text)
    history = memory.get(user_id)

    # Si Groq falla, dejamos que el error suba al error_handler global.
    answer = groq_client.chat(SYSTEM_PROMPT, history)

    memory.add(user_id, "assistant", answer)
    await update.message.reply_text(answer)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Captura cualquier excepción y responde amigablemente al usuario."""
    logger.error("Excepción en handler:", exc_info=context.error)

    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(config.FRIENDLY_ERROR)
