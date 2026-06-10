"""
Entrypoint del bot.

Arma la aplicación de Telegram, registra los handlers y arranca el polling.
Se ejecuta con:  python bot.py
"""

import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

import config
import handlers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main() -> None:
    # Falla temprano y claro si faltan credenciales.
    config.validate()

    app = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("reset", handlers.reset))
    # Cualquier texto que no sea un comando va al LLM.
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.on_message)
    )
    app.add_error_handler(handlers.error_handler)

    logger.info(
        "🤖 Bot iniciado | modelo=%s | personalidad cargada | memoria=%d msgs",
        config.GROQ_MODEL,
        config.MAX_HISTORY,
    )
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
