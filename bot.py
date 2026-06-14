"""
Entrypoint del bot.

Arma la aplicación de Telegram, registra los handlers y arranca el polling.
Se ejecuta con:  python bot.py
"""

import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

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


class _HealthHandler(BaseHTTPRequestHandler):
    """Responde 200 OK para health checks (Render) y pings de UptimeRobot."""

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):
        pass  # silencia el log de cada request


def _start_health_server() -> None:
    """
    Mini servidor HTTP para hosts free tier (Render) que requieren un puerto
    abierto y matan el servicio si no hay tráfico. Escucha en PORT (lo inyecta
    Render); un monitor de UptimeRobot lo mantiene despierto.
    """
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(("0.0.0.0", port), _HealthHandler).serve_forever()


def main() -> None:
    # Falla temprano y claro si faltan credenciales.
    config.validate()

    # Health-server en un thread daemon (no bloquea el cierre del proceso).
    threading.Thread(target=_start_health_server, daemon=True).start()

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
    app.run_polling(allowed_updates=["message"], drop_pending_updates=True)


if __name__ == "__main__":
    main()
