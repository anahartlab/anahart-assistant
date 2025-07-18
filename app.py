import json
import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

OPENROUTER_API_KEY = "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"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Загружаем товары из products.json
with open("products.json", "r", encoding="utf-8") as f:
    products = json.load(f)

def find_products(query: str):
    query_lower = query.lower()
    results = []
    for p in products:
        if (query_lower in p["name"].lower()
            or query_lower in p["title"].lower()
            or query_lower in p["description"].lower()):
            results.append(p)
    return results[:5]

@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message", "")

    found = find_products(user_message)
    if found:
        reply = "Вот что я нашёл:\n"
        for p in found:
            reply += f'– {p["title"]} ({p["stock"]})\n👉 <a href="{p["link"]}" target="_blank">Смотреть</a>\n\n'
    else:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        body = {
            "model": "openrouter/openchat",
            "messages": [
                {"role": "system", "content": "Ты ассистент ANAHART. Отвечай вежливо и по делу."},
                {"role": "user", "content": user_message}
            ]
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=body
            )
            response.raise_for_status()
            data = response.json()
            reply = data["choices"][0]["message"]["content"]

    return {"reply": reply}
