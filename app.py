from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    json_data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Ты — ассистент ANAHART. Отвечай вежливо и по делу."},
            {"role": "user", "content": message}
        ]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(OPENROUTER_URL, headers=headers, json=json_data)
        response.raise_for_status()
        data = response.json()

    reply = data["choices"][0]["message"]["content"]
    return {"reply": reply}
