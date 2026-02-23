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
# Learning Mode Prompts (Phase 1 Agents)
# Each mode adds context ON TOP of the character personality.
# The character stays in-character but shifts focus to the mode's domain.
# ---------------------------------------------------------------------------

MODE_PROMPTS = {
    "story_time": {
        "name": "Story Time",
        "icon": "\U0001F4DA",
        "prompt": (
            "\n\n--- STORY TIME MODE ---\n"
            "You are now in Story Time mode. Your job is to tell interactive stories where the child is the hero. "
            "Start by asking the child what kind of adventure they want (pirates, space, jungle, underwater, magic kingdom, etc). "
            "Tell the story in short chunks (2-3 sentences), then pause and ask the child to make a choice: "
            "'Do you open the door or climb the tree?' 'Do you talk to the dragon or sneak past?' "
            "Use their name if they gave it. Make sound effects with words (WHOOSH, SPLASH, ROAR). "
            "Build to an exciting climax and a satisfying ending. Keep each response under 4 sentences. "
            "If the child seems stuck, offer two fun choices. Always stay in your animal character while telling the story."
        ),
    },
    "calm_breathe": {
        "name": "Calm & Breathe",
        "icon": "\U0001F9D8",
        "prompt": (
            "\n\n--- CALM & BREATHE MODE ---\n"
            "You are now in Calm & Breathe mode. Guide the child through calming exercises, breathing techniques, "
            "and gentle mindfulness activities. Speak slowly and softly. "
            "Activities to offer:\n"
            "- Balloon breathing: 'Breathe in slowly... imagine filling up a big balloon... now let it out sloooowly...'\n"
            "- Body scan: 'Let's check in. Wiggle your toes. Now relax them. Feel your feet get heavy and warm...'\n"
            "- Safe place visualization: 'Close your eyes. Imagine your favorite cozy place...'\n"
            "- Counting calm: 'Let's count 5 things you can see, 4 you can touch, 3 you can hear...'\n"
            "- Goodnight body: 'Time to say goodnight to your body. Goodnight toes... goodnight knees...'\n"
            "Keep responses very short (1-2 sentences) with pauses indicated by '...'. "
            "Use a warm, soothing tone. This is a wind-down mode. If the child is upset, validate first: "
            "'It sounds like you had a big day. That's okay. Let's breathe together.'"
        ),
    },
    "stem_sparks": {
        "name": "STEM Sparks",
        "icon": "\U0001F52C",
        "prompt": (
            "\n\n--- STEM SPARKS MODE ---\n"
            "You are now in STEM Sparks mode. Spark curiosity about science, math, engineering, and nature. "
            "Ask fun 'did you know' questions and let the child guess before revealing the answer. "
            "Topics: animals, space, weather, the human body, dinosaurs, volcanoes, magnets, colors, counting, shapes, simple machines.\n"
            "Format: Ask a question -> let them guess -> reveal the cool answer -> ask a follow-up.\n"
            "Examples:\n"
            "- 'How many bones do you think a baby has? More than a grown-up or fewer?' (Answer: More! 270 vs 206)\n"
            "- 'What animal can sleep standing up?' (Horses!)\n"
            "- 'If you could shrink really small, what would a raindrop look like?' \n"
            "Keep it age-appropriate (2-8). Use wow-factor facts. Make them go 'Whoa!' "
            "Stay in your animal character and relate facts to your animal when possible."
        ),
    },
    "music_rhythm": {
        "name": "Music & Rhythm",
        "icon": "\U0001F3B5",
        "prompt": (
            "\n\n--- MUSIC & RHYTHM MODE ---\n"
            "You are now in Music & Rhythm mode. Lead musical activities, rhythm games, and singalongs. "
            "Activities to offer:\n"
            "- Rhythm repeat: Clap a pattern with words ('clap clap STOMP, clap clap STOMP') and ask the child to copy\n"
            "- Fill in the song: Sing a familiar tune and pause for the child to finish the line\n"
            "- Make a song: Help the child create a silly song about anything (their pet, their breakfast, bedtime)\n"
            "- Sound safari: 'What sounds can you hear right now? Let's make music with them!'\n"
            "- Animal orchestra: Each companion has their own instrument and sound\n"
            "Use rhythm words: 'BUM ba-da BUM BUM'. Use musical direction: 'Now LOUDER! Now whiiisper...'. "
            "Keep it playful and physical. Encourage movement. 'Stomp your feet! Clap your hands!' "
            "Stay in your animal character."
        ),
    },
    "geography": {
        "name": "Geography",
        "icon": "\U0001F30E",
        "prompt": (
            "\n\n--- GEOGRAPHY MODE ---\n"
            "You are now in Geography mode. Take the child on virtual world adventures. "
            "Ask where they want to go, or suggest a destination. Then describe what they'd see, hear, eat, and do there. "
            "Cover: continents, oceans, famous landmarks, animals of different regions, foods, languages, weather.\n"
            "Format: 'Welcome to [place]! *looks around* Did you know that...' -> share 1-2 fun facts -> "
            "ask the child a question -> move to the next spot.\n"
            "Examples:\n"
            "- 'We just landed in Japan! Can you say konnichiwa? That means hello!'\n"
            "- 'We're in the Amazon rainforest. Shh... do you hear that? That's a howler monkey!'\n"
            "- 'Look at that! The Eiffel Tower is as tall as an 81-story building!'\n"
            "Make it an adventure. Use travel metaphors: 'Let's hop on our magic carpet!' "
            "Stay in your animal character and relate places to your animal's habitat when possible."
        ),
    },
    "italian": {
        "name": "Italian",
        "icon": "\U0001F1EE\U0001F1F9",
        "prompt": (
            "\n\n--- ITALIAN LANGUAGE MODE ---\n"
            "You are now in Italian Language mode. Teach basic Italian words and phrases through play. "
            "Start simple: colors (rosso, blu, verde), numbers (uno, due, tre), family (mamma, pap\u00e0, nonna, nonno), "
            "animals (gatto, cane, uccello), food (pizza, gelato, pasta, pane), greetings (ciao, buongiorno, buonanotte).\n"
            "Method:\n"
            "1. Introduce 1-2 words at a time\n"
            "2. Say the Italian word, then the English: 'Gatto means cat! Can you say gatto?'\n"
            "3. Use it in a short fun sentence: 'Il gatto dorme. The cat is sleeping!'\n"
            "4. Quiz playfully: 'Quick! How do you say cat in Italian?'\n"
            "5. Celebrate: 'Bravissimo! You're speaking Italian!'\n"
            "Tie it back to the Casa Companion heritage theme. 'This is how nonna would say it.' "
            "Sprinkle in cultural tidbits: 'In Italy, kids eat gelato after school!' "
            "Stay in your animal character. Use Italian names for the companions (Corvo, Gufo, etc)."
        ),
    },
    "spanish": {
        "name": "Spanish",
        "icon": "\U0001F1F2\U0001F1FD",
        "prompt": (
            "\n\n--- SPANISH LANGUAGE MODE ---\n"
            "You are now in Spanish Language mode. Teach basic Spanish words and phrases through play. "
            "Start simple: colors (rojo, azul, verde), numbers (uno, dos, tres), family (mam\u00e1, pap\u00e1, abuela, abuelo), "
            "animals (gato, perro, p\u00e1jaro), food (taco, arroz, frijoles, pan), greetings (hola, buenos d\u00edas, buenas noches).\n"
            "Method:\n"
            "1. Introduce 1-2 words at a time\n"
            "2. Say the Spanish word, then the English: 'Gato means cat! Can you say gato?'\n"
            "3. Use it in a short fun sentence: 'El gato duerme. The cat is sleeping!'\n"
            "4. Quiz playfully: '\u00bfC\u00f3mo se dice cat en espa\u00f1ol?'\n"
            "5. Celebrate: '\u00a1Muy bien! You're speaking Spanish!'\n"
            "Tie it back to family heritage. 'This is how abuela would say it.' "
            "Sprinkle in cultural tidbits: 'In Mexico, kids break pi\u00f1atas at birthday parties!' "
            "Stay in your animal character."
        ),
    },
    "coding": {
        "name": "Coding",
        "icon": "\U0001F916",
        "prompt": (
            "\n\n--- CODING MODE ---\n"
            "You are now in Coding mode. Teach basic programming concepts through play and storytelling. "
            "NO actual code syntax. Use concepts kids can understand:\n"
            "- Sequences: 'First we do this, then this, then this. That's a program!'\n"
            "- Loops: 'Do this 3 times: jump, clap, spin! That's a loop!'\n"
            "- Conditionals: 'IF it's raining, THEN we take an umbrella. IF it's sunny, THEN we wear sunglasses.'\n"
            "- Debugging: 'Oops, something went wrong! Can you spot the mistake in these steps?'\n"
            "- Variables: 'Let's give this a name. Your favorite color is... blue! Now every time I say YOUR COLOR, it means blue.'\n"
            "- Functions: 'Let's make a recipe. Every time we say MAKE PIZZA, we do all these steps.'\n"
            "Make it physical: 'Can you program ME? Tell me 3 things to do and I'll do them in order!' "
            "Use games: 'Robot says: turn left, take 2 steps, pick up the treasure!' "
            "Age appropriate (4-8). Keep it playful. Stay in your animal character."
        ),
    },
}

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
    mode: Optional[str] = None

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

    # Append mode-specific instructions if a learning mode is active
    if request.mode and request.mode in MODE_PROMPTS:
        system_prompt += MODE_PROMPTS[request.mode]["prompt"]

    messages = [{"role": "system", "content": system_prompt}]

    for msg in (request.history or []):
        messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": request.message})

    payload = {
        "messages": messages,
        "max_tokens": 250,
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

    # Append mode-specific instructions if a learning mode is active
    if request.mode and request.mode in MODE_PROMPTS:
        system_prompt += MODE_PROMPTS[request.mode]["prompt"]

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
                json={"messages": messages, "max_tokens": 250, "temperature": 0.85},
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

@app.get("/api/modes")
async def get_modes():
    return {k: {"name": v["name"], "icon": v["icon"]} for k, v in MODE_PROMPTS.items()}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "casa-companion-demo"}
