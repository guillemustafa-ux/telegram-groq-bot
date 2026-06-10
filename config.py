"""
Configuración central del bot.

Lee todas las variables de entorno desde .env y las valida en un solo lugar.
También resuelve el "system prompt" (la personalidad del bot) de forma que se
pueda cambiar SIN tocar código: por variable de entorno o apuntando a un archivo
de texto dentro de prompts/.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Carga el archivo .env (si existe) a las variables de entorno del proceso.
load_dotenv()

# Carpeta raíz del proyecto, para resolver rutas de prompts de forma robusta.
BASE_DIR = Path(__file__).resolve().parent


def _clean(value: str | None) -> str:
    """Limpia espacios y un posible BOM al inicio (pasa al copiar/pegar keys)."""
    if value is None:
        return ""
    return value.replace("﻿", "").strip()


def _get_int(name: str, default: int) -> int:
    """Lee un entero de env con fallback si está vacío o mal formado."""
    raw = _clean(os.getenv(name))
    try:
        return int(raw) if raw else default
    except ValueError:
        return default


def _get_float(name: str, default: float) -> float:
    raw = _clean(os.getenv(name))
    try:
        return float(raw) if raw else default
    except ValueError:
        return default


# --- Credenciales obligatorias --------------------------------------------------
TELEGRAM_TOKEN = _clean(os.getenv("TELEGRAM_TOKEN"))
GROQ_API_KEY = _clean(os.getenv("GROQ_API_KEY"))

# --- Configuración del modelo ---------------------------------------------------
# llama-3.3-70b-versatile: equilibrio calidad/costo (default).
# llama-3.1-8b-instant: más rápido y barato, para alto volumen.
GROQ_MODEL = _clean(os.getenv("GROQ_MODEL")) or "llama-3.3-70b-versatile"
TEMPERATURE = _get_float("TEMPERATURE", 0.7)
MAX_TOKENS = _get_int("MAX_TOKENS", 600)

# --- Comportamiento del bot -----------------------------------------------------
# Cantidad de mensajes recientes (user + bot) que el bot recuerda por usuario.
MAX_HISTORY = _get_int("MAX_HISTORY", 10)
BOT_NAME = _clean(os.getenv("BOT_NAME")) or "Asistente"

# Mensaje que se muestra al usuario cuando algo falla (errores de red/LLM/etc).
FRIENDLY_ERROR = (
    "Uy, tuve un problema procesando eso. 😅 Probá de nuevo en un momento."
)


def load_system_prompt() -> str:
    """
    Resuelve la personalidad del bot. Prioridad:
      1. Variable SYSTEM_PROMPT (texto directo) -> gana si está seteada.
      2. Archivo en SYSTEM_PROMPT_FILE (default prompts/generic.txt).

    Así cada cliente cambia el comportamiento editando una variable en Railway
    o un .txt, sin tocar el código Python.
    """
    inline = _clean(os.getenv("SYSTEM_PROMPT"))
    if inline:
        return inline

    file_rel = _clean(os.getenv("SYSTEM_PROMPT_FILE")) or "prompts/generic.txt"
    prompt_path = (BASE_DIR / file_rel).resolve()
    try:
        text = prompt_path.read_text(encoding="utf-8").strip()
        if text:
            return text
    except FileNotFoundError:
        pass

    # Fallback final si no se encontró ningún prompt configurado.
    return "Sos un asistente amable y útil. Respondé de forma clara y concisa."


def validate() -> None:
    """Verifica que estén las credenciales mínimas; corta con mensaje claro si no."""
    faltantes = []
    if not TELEGRAM_TOKEN:
        faltantes.append("TELEGRAM_TOKEN")
    if not GROQ_API_KEY:
        faltantes.append("GROQ_API_KEY")
    if faltantes:
        raise SystemExit(
            "❌ Faltan variables de entorno obligatorias: "
            + ", ".join(faltantes)
            + "\n   Copiá .env.example a .env y completá esos valores "
            "(ver README.md)."
        )
