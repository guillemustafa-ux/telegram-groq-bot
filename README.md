# 🤖 Telegram Groq Bot

Bot de Telegram conversacional con **lenguaje natural** (sin menús), impulsado por la
[Groq API](https://groq.com/) como LLM. Mantiene contexto de la conversación, soporta
múltiples usuarios a la vez y su **personalidad es totalmente configurable sin tocar
código** — solo cambiás una variable de entorno o un archivo de texto.

Pensado para usarse como base reutilizable: el mismo bot sirve para un asistente cripto,
un bot de atención al cliente de una empresa, o un asistente genérico.

---

## ✨ Funcionalidades

- 💬 **Conversación natural** — el usuario escribe libremente, sin comandos ni menús.
- 🧠 **Memoria de contexto** — recuerda los últimos N mensajes (configurable, default 10).
- 🎭 **Personalidad configurable** — cambiás el *system prompt* sin tocar el código.
- 👥 **Multiusuario** — cada usuario tiene su propio contexto separado por `user_id`.
- `/start` — mensaje de bienvenida.
- `/reset` — borra el historial y empieza de cero.
- 🛡️ **Manejo de errores** — si algo falla, el usuario ve un mensaje amigable (no crashea).

---

## 🧩 Stack

- **Python 3.12+**
- [`python-telegram-bot`](https://docs.python-telegram-bot.org/) v21 (async)
- [`groq`](https://pypi.org/project/groq/) — SDK oficial de Groq
- `python-dotenv` — configuración por variables de entorno

---

## 📁 Estructura

```
telegram-groq-bot/
├── bot.py              # Entrypoint: arma la app y arranca el polling
├── config.py           # Carga y valida variables de entorno + system prompt
├── groq_client.py      # Wrapper de la Groq API
├── memory.py           # Memoria de conversación por usuario
├── handlers.py         # /start, /reset, mensajes y manejo de errores
├── prompts/            # Personalidades listas (.txt)
│   ├── generic.txt     #   asistente genérico (default)
│   ├── crypto.txt      #   asistente cripto
│   └── business.txt    #   atención al cliente
├── requirements.txt
├── .env.example
├── Procfile            # Railway
└── runtime.txt         # Railway (pin de Python)
```

---

## 🚀 Instalación y uso local

### 1. Conseguir las credenciales

- **Token de Telegram**: hablale a [@BotFather](https://t.me/BotFather), mandá `/newbot`,
  seguí los pasos y copiá el token que te da.
- **API key de Groq**: entrá a [console.groq.com/keys](https://console.groq.com/keys),
  creá una key (empieza con `gsk_`). El tier gratuito alcanza de sobra para empezar.

### 2. Instalar

```bash
# Clonar y entrar a la carpeta
git clone <tu-repo> telegram-groq-bot
cd telegram-groq-bot

# (Recomendado) entorno virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Dependencias
pip install -r requirements.txt
```

### 3. Configurar

```bash
# Copiá el ejemplo y completá tus valores
cp .env.example .env      # Windows: copy .env.example .env
```

Editá `.env` y poné al menos `TELEGRAM_TOKEN` y `GROQ_API_KEY`.

### 4. Correr

```bash
python bot.py
```

Si todo está bien vas a ver `🤖 Bot iniciado ...` en la consola. Andá a Telegram,
buscá tu bot y mandale `/start`.

---

## 🎭 Personalizar la personalidad (sin tocar código)

Esta es la parte clave para reutilizar el bot con distintos clientes. Hay dos formas,
elegí una:

**Opción A — apuntar a un archivo de prompt** (recomendado)

En `.env`:
```env
SYSTEM_PROMPT_FILE=prompts/crypto.txt
```
Ya vienen tres listos: `generic.txt`, `crypto.txt`, `business.txt`. Podés crear el tuyo:
copiá uno, editalo y apuntá la variable a él.

**Opción B — escribir el prompt directo en la variable**

En `.env` (tiene prioridad sobre el archivo):
```env
SYSTEM_PROMPT=Sos un asistente que solo responde sobre recetas de cocina italiana.
```

Para el caso **atención al cliente**, abrí `prompts/business.txt` y completá los datos
de la empresa (nombre, rubro, horarios, productos, formas de pago). El bot responderá
usando solo esa información.

### Otros ajustes (en `.env`)

| Variable | Default | Para qué |
|---|---|---|
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Modelo de Groq (ver abajo) |
| `TEMPERATURE` | `0.7` | Creatividad de las respuestas (0–1) |
| `MAX_TOKENS` | `600` | Largo máximo de cada respuesta |
| `MAX_HISTORY` | `10` | Mensajes recientes que recuerda por usuario |
| `BOT_NAME` | `Asistente` | Nombre que usa en el `/start` |

---

## 🧠 Modelos de Groq

> ⚠️ Modelos viejos como `llama3-8b-8192` y `mixtral-8x7b` están **deprecados** en Groq.

Vigentes (poné el id en `GROQ_MODEL`):

- `llama-3.3-70b-versatile` — mejor calidad **(default)**
- `llama-3.1-8b-instant` — más rápido y barato, ideal para alto volumen

Lista actualizada: [console.groq.com/docs/models](https://console.groq.com/docs/models).

---

## ☁️ Deploy en Railway

1. Subí el repo a GitHub (el `.gitignore` ya excluye `.env`, así que tus keys no se suben).
2. En [Railway](https://railway.app/): **New Project → Deploy from GitHub repo** y elegí
   este repo.
3. En **Variables**, cargá las mismas que tenés en `.env`
   (`TELEGRAM_TOKEN`, `GROQ_API_KEY`, y las opcionales que quieras).
4. Railway detecta el `Procfile` (`worker: python bot.py`) y levanta el bot.
   Como usa *polling*, no necesitás exponer ningún puerto ni configurar webhooks.

El bot queda corriendo 24/7. Para cambiar la personalidad en producción, basta con
editar la variable `SYSTEM_PROMPT_FILE` / `SYSTEM_PROMPT` en Railway y reiniciar.

---

## 💾 Persistencia (opcional)

La memoria vive en RAM (`memory.py`), así que se reinicia si el proceso se cae. Para la
mayoría de los casos alcanza. Si un cliente necesita que el bot recuerde entre reinicios,
reemplazá la implementación de `memory.py` por SQLite o Redis manteniendo la misma API
(`add`, `get`, `reset`) — el resto del bot no cambia.

---

## 📄 Licencia

MIT — usalo, modificalo y adaptalo libremente.
