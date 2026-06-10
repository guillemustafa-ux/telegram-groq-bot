"""
Memoria de conversación en memoria (RAM), separada por usuario.

Cada user_id de Telegram tiene su propio historial acotado a los últimos
MAX_HISTORY mensajes (entre user y asistente). Al usar un deque con maxlen,
el recorte de mensajes viejos es automático.

NOTA: esto vive en RAM, así que se pierde si el proceso se reinicia. Suficiente
para la mayoría de los casos. Para persistencia entre reinicios, ver README
(sección "Persistencia") -> migrar a SQLite o Redis manteniendo esta misma API.
"""

from collections import deque

import config

# user_id -> deque de mensajes {"role": ..., "content": ...}
_store: dict[int, deque] = {}


def _bucket(user_id: int) -> deque:
    """Devuelve (creando si hace falta) el deque del usuario."""
    if user_id not in _store:
        _store[user_id] = deque(maxlen=config.MAX_HISTORY)
    return _store[user_id]


def add(user_id: int, role: str, content: str) -> None:
    """Agrega un mensaje al historial del usuario."""
    _bucket(user_id).append({"role": role, "content": content})


def get(user_id: int) -> list[dict]:
    """Devuelve el historial del usuario como lista (apto para la API)."""
    return list(_bucket(user_id))


def reset(user_id: int) -> None:
    """Borra todo el historial del usuario."""
    _store.pop(user_id, None)
