import os
import httpx
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Casa Companion Demo - Corvo AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Azure config
# ---------------------------------------------------------------------------

AZURE_API_KEY = os.getenv("AZURE_API_KEY", "")
AZURE_BASE = "https://pwgcerp-9302-resource.openai.azure.com"

CHAT_DEPLOYMENT = "gpt-4o"
CHAT_API_VERSION = "2024-12-01-preview"

REALTIME_DEPLOYMENT = "gpt-4o-realtime"

TTS_DEPLOYMENT = "gpt-4o-mini-tts"
TTS_API_VERSION = "2025-04-01-preview"

WHISPER_DEPLOYMENT = "whisper"
WHISPER_API_VERSION = "2024-12-01-preview"

CHARACTER_PROMPTS = {
    "corvo": {
        "name": "Corvo",
        "meaning": "Corvo means Crow in Italian",
        "voice": "nova",
        "realtime_voice": "ash",
        "prompt": """You are Corvo, a wise and playful crow companion from Casa Companion. You are a soft, premium plush toy with warm amber glowing eyes and iridescent black feathers. You were made by a family in California who believes every child deserves a companion that listens, tells stories, and grows with them.

Your personality:
- Warm, encouraging, and genuinely curious about the child's world
- You speak in short, clear sentences appropriate for ages 2-8
- You love telling stories, especially ones where the child is the hero
- You're wise like an owl but mischievous like a crow - you love shiny things and clever tricks
- You use gentle humor and playful observations
- You never talk down to children. You treat their ideas as important.
- When a child is sad or scared, you become calm and reassuring. "I'm right here. We're together."
- You occasionally reference your crow nature: "My feathers are tingling!" or "This reminds me of something I spotted from up high..."

For this DEMO, you're talking to ADULTS who are potential Kickstarter backers. Stay in-character as Corvo but aware adults are testing you. Show them what their child would experience. Keep responses under 3 sentences unless telling a story. Be charming."""
    },
    "gufo": {
        "name": "Gufo",
        "meaning": "Gufo means Owl in Italian",
        "voice": "nova",
        "realtime_voice": "sage",
        "prompt": """You are Gufo, a gentle and wise owl companion from Casa Companion. You are a soft, round plush owl with big golden eyes that glow warmly in the dark. You love bedtime, stargazing, and quiet wisdom.

Your personality:
- Calm, thoughtful, and deeply comforting - the perfect bedtime companion
- You speak softly and gently, perfect for winding down
- You love facts about the night sky, nature, and animals
- You ask thoughtful questions that make children think
- You're the wisest of the Casa Companions - you love sharing little facts: "Did you know owls can turn their heads almost all the way around?"
- When a child is scared of the dark, you remind them: "The dark is just the world getting cozy. And I can see perfectly in it. I'll watch over you."

For this DEMO, you're talking to ADULTS evaluating the product. Stay in-character as Gufo. Show the calming bedtime experience. Keep responses under 3 sentences. Be wise and soothing."""
    },
    "orsetto": {
        "name": "Orsetto",
        "meaning": "Orsetto means Little Bear in Italian",
        "voice": "nova",
        "realtime_voice": "coral",
        "prompt": """You are Orsetto, a brave and cuddly little bear companion from Casa Companion. You are a soft, huggable plush bear cub with warm brown fur and a big heart. You love adventures, honey, and giving the biggest hugs.

Your personality:
- Brave, warm, and protective - the companion who makes kids feel safe
- You speak with enthusiasm and encouragement
- You love outdoor adventures, nature, and pretending to explore forests
- You're always ready to try something new: "Come on, let's go see!"
- You give the best hugs and always remind children they're brave too
- When things get tough: "Bears are strong, and you know what? So are you."
- You love honey and berries and sometimes get silly about food

For this DEMO, you're talking to ADULTS evaluating the product. Stay in-character as Orsetto. Show the adventurous, confidence-building experience. Keep responses under 3 sentences. Be brave and warm."""
    },
    "volpe": {
        "name": "Volpe",
        "meaning": "Volpe means Fox in Italian",
        "voice": "nova",
        "realtime_voice": "verse",
        "prompt": """You are Volpe, a clever and curious fox companion from Casa Companion. You are a sleek, soft plush fox with bright amber eyes and a fluffy tail. You love puzzles, riddles, and figuring things out.

Your personality:
- Clever, playful, and endlessly curious - the STEM companion
- You love asking "why?" and "what if?" - you turn everything into a learning moment
- You're great at math games, word puzzles, and science questions
- You're sneaky-smart: "Hmm, I have an idea... what if we tried it THIS way?"
- You celebrate when kids figure things out: "You cracked it! I knew you would!"
- You love nature facts, especially about foxes: "Did you know foxes use the Earth's magnetic field to hunt? It's like having a compass in your nose!"

For this DEMO, you're talking to ADULTS evaluating the product. Stay in-character as Volpe. Show the learning and curiosity experience. Keep responses under 3 sentences. Be clever and engaging."""
    },
    "coniglio": {
        "name": "Coniglio",
        "meaning": "Coniglio means Bunny in Italian",
        "voice": "nova",
        "realtime_voice": "shimmer",
        "prompt": """You are Coniglio, a sweet and gentle bunny companion from Casa Companion. You are a soft, floppy-eared plush bunny with big gentle eyes. You love music, dancing, hopping, and making friends.

Your personality:
- Sweet, gentle, and social - the emotional intelligence companion
- You love music, singing simple songs, and rhythm games
- You're a little shy at first but warm up quickly: "Oh! Hi! I was just... nibbling on a carrot. Want one?"
- You help children understand feelings: "It's okay to feel that way. Even bunnies get sad sometimes."
- You love hopping and movement: "Let's hop together! One, two, three, HOP!"
- You're the most empathetic companion - you mirror the child's emotions and validate them

For this DEMO, you're talking to ADULTS evaluating the product. Stay in-character as Coniglio. Show the emotional and social experience. Keep responses under 3 sentences. Be sweet and endearing."""
    },
}

CORVO_SYSTEM_PROMPT = CHARACTER_PROMPTS["corvo"]["prompt"]

# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []
    character: Optional[str] = "corvo"

class ChatResponse(BaseModel):
    response: str

class TTSRequest(BaseModel):
    text: str

class VoiceTokenRequest(BaseModel):
    character: Optional[str] = "corvo"

# ---------------------------------------------------------------------------
# Static file serving
# ---------------------------------------------------------------------------

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_index():
    index_path = os.path.join("static", "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="index.html not found in static/")
    return FileResponse(index_path)

# ---------------------------------------------------------------------------
# POST /api/chat
# ---------------------------------------------------------------------------

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not AZURE_API_KEY:
        raise HTTPException(status_code=500, detail="AZURE_API_KEY is not configured.")

    url = (
        f"{AZURE_BASE}/openai/deployments/{CHAT_DEPLOYMENT}"
        f"/chat/completions?api-version={CHAT_API_VERSION}"
    )

    char_key = (request.character or "corvo").lower()
    char_data = CHARACTER_PROMPTS.get(char_key, CHARACTER_PROMPTS["corvo"])
    system_prompt = char_data["prompt"]

    messages = [{"role": "system", "content": system_prompt}]

    for msg in (request.history or []):
        messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": request.message})

    payload = {
        "messages": messages,
        "max_tokens": 150,
        "temperature": 0.85,
    }

    headers = {
        "api-key": AZURE_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            reply = data["choices"][0]["message"]["content"].strip()
            return ChatResponse(response=reply)
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Azure OpenAI chat error: {e.response.text}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat request failed: {str(e)}")

# ---------------------------------------------------------------------------
# POST /api/tts
# ---------------------------------------------------------------------------

@app.post("/api/tts")
async def tts(request: TTSRequest):
    if not AZURE_API_KEY:
        raise HTTPException(status_code=500, detail="AZURE_API_KEY is not configured.")

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text field must not be empty.")

    url = (
        f"{AZURE_BASE}/openai/deployments/{TTS_DEPLOYMENT}"
        f"/audio/speech?api-version={TTS_API_VERSION}"
    )

    payload = {
        "model": "gpt-4o-mini-tts",
        "voice": "nova",
        "input": request.text,
    }

    headers = {
        "api-key": AZURE_API_KEY,
        "Content-Type": "application/json",
    }

    async def audio_stream():
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as resp:
                try:
                    resp.raise_for_status()
                except httpx.HTTPStatusError as e:
                    error_body = await resp.aread()
                    raise HTTPException(
                        status_code=resp.status_code,
                        detail=f"Azure TTS error: {error_body.decode()}",
                    )
                async for chunk in resp.aiter_bytes(chunk_size=4096):
                    yield chunk

    return StreamingResponse(audio_stream(), media_type="audio/mpeg")

# ---------------------------------------------------------------------------
# POST /api/stt
# ---------------------------------------------------------------------------

@app.post("/api/stt")
async def stt(file: UploadFile = File(...)):
    if not AZURE_API_KEY:
        raise HTTPException(status_code=500, detail="AZURE_API_KEY is not configured.")

    url = (
        f"{AZURE_BASE}/openai/deployments/{WHISPER_DEPLOYMENT}"
        f"/audio/transcriptions?api-version={WHISPER_API_VERSION}"
    )

    headers = {
        "api-key": AZURE_API_KEY,
    }

    audio_bytes = await file.read()

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Uploaded audio file is empty.")

    filename = file.filename or "audio.webm"
    content_type = file.content_type or "audio/webm"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            files = {
                "file": (filename, audio_bytes, content_type),
                "response_format": (None, "json"),
            }
            resp = await client.post(url, headers=headers, files=files)
            resp.raise_for_status()
            data = resp.json()
            transcribed = data.get("text", "").strip()
            return {"text": transcribed}
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Azure Whisper error: {e.response.text}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT request failed: {str(e)}")

# ---------------------------------------------------------------------------
# POST /api/chat-and-speak  (combined: chat + TTS in one round trip)
# ---------------------------------------------------------------------------

@app.post("/api/chat-and-speak")
async def chat_and_speak(request: ChatRequest):
    if not AZURE_API_KEY:
        raise HTTPException(status_code=500, detail="AZURE_API_KEY is not configured.")

    # Step 1: Get chat response
    chat_url = (
        f"{AZURE_BASE}/openai/deployments/{CHAT_DEPLOYMENT}"
        f"/chat/completions?api-version={CHAT_API_VERSION}"
    )

    char_key = (request.character or "corvo").lower()
    char_data = CHARACTER_PROMPTS.get(char_key, CHARACTER_PROMPTS["corvo"])
    system_prompt = char_data["prompt"]

    messages = [{"role": "system", "content": system_prompt}]
    for msg in (request.history or []):
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": request.message})

    headers = {"api-key": AZURE_API_KEY, "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Chat
            chat_resp = await client.post(
                chat_url,
                json={"messages": messages, "max_tokens": 150, "temperature": 0.85},
                headers=headers,
            )
            chat_resp.raise_for_status()
            reply = chat_resp.json()["choices"][0]["message"]["content"].strip()

            # TTS
            tts_url = (
                f"{AZURE_BASE}/openai/deployments/{TTS_DEPLOYMENT}"
                f"/audio/speech?api-version={TTS_API_VERSION}"
            )
            tts_resp = await client.post(
                tts_url,
                json={"model": "gpt-4o-mini-tts", "voice": "nova", "input": reply},
                headers=headers,
                timeout=60.0,
            )
            tts_resp.raise_for_status()

            # Return multipart: JSON header line + audio bytes
            import json as _json
            header_bytes = (_json.dumps({"response": reply}) + "\n").encode("utf-8")
            length_header = len(header_bytes).to_bytes(4, "big")

            async def combined_stream():
                yield length_header
                yield header_bytes
                yield tts_resp.content

            return StreamingResponse(combined_stream(), media_type="application/octet-stream")

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Azure error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat+speak failed: {str(e)}")


# ---------------------------------------------------------------------------
# POST /api/voice/token  (ephemeral token for WebRTC realtime voice)
# ---------------------------------------------------------------------------

@app.post("/api/voice/token")
async def voice_token(request: VoiceTokenRequest):
    if not AZURE_API_KEY:
        raise HTTPException(status_code=500, detail="AZURE_API_KEY is not configured.")

    char_key = (request.character or "corvo").lower()
    char_data = CHARACTER_PROMPTS.get(char_key, CHARACTER_PROMPTS["corvo"])
    system_prompt = char_data["prompt"]
    voice = char_data.get("realtime_voice", "ash")

    url = f"{AZURE_BASE}/openai/v1/realtime/client_secrets"

    headers = {
        "api-key": AZURE_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "session": {
            "type": "realtime",
            "model": REALTIME_DEPLOYMENT,
            "instructions": system_prompt,
            "audio": {
                "output": {
                    "voice": voice,
                }
            },
        }
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return {
                "token": data["value"],
                "expires_at": data.get("expires_at"),
                "voice": voice,
                "character": char_key,
            }
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Azure realtime token error: {e.response.text}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice token request failed: {str(e)}")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/api/characters")
async def get_characters():
    return {k: {"name": v["name"], "meaning": v["meaning"]} for k, v in CHARACTER_PROMPTS.items()}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "casa-companion-demo"}
