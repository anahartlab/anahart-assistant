import httpx
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")

    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "openrouter/openchat",
        "messages": [
            {"role": "system", "content": "Ты — ассистент ANAHART. Отвечай вежливо и по делу."},
            {"role": "user", "content": message}
        ]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post("https://openrouter.ai/v1/chat/completions", headers=headers, json=body)
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]

    return {"reply": reply}
