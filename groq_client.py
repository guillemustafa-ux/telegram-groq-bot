"""
Wrapper de la Groq API usando el SDK oficial.

Aísla toda la lógica de hablar con el LLM en un solo módulo, de modo que el resto
del bot no sepa los detalles de la API. Devuelve texto plano o lanza GroqError,
que el handler de Telegram convierte en un mensaje amigable.
"""

import logging

from groq import Groq

import config

logger = logging.getLogger(__name__)

# Cliente único reutilizado en todas las llamadas.
_client = Groq(api_key=config.GROQ_API_KEY)


class GroqError(Exception):
    """Error al consultar la Groq API (red, auth, rate limit, etc.)."""


def chat(system_prompt: str, history: list[dict]) -> str:
    """
    Genera una respuesta del LLM.

    Args:
        system_prompt: la personalidad/instrucciones del bot.
        history: lista de mensajes [{"role": "user"|"assistant", "content": ...}]
                 con el contexto reciente de la conversación.

    Returns:
        El texto de la respuesta del asistente.

    Raises:
        GroqError: si la API falla o devuelve algo inesperado.
    """
    messages = [{"role": "system", "content": system_prompt}, *history]

    try:
        completion = _client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=messages,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS,
        )
    except Exception as exc:  # el SDK puede lanzar varios tipos de error
        logger.error("Error llamando a Groq: %s", exc)
        raise GroqError(str(exc)) from exc

    try:
        return completion.choices[0].message.content.strip()
    except (AttributeError, IndexError) as exc:
        logger.error("Respuesta inesperada de Groq: %s", completion)
        raise GroqError("Respuesta vacía o malformada del modelo") from exc
