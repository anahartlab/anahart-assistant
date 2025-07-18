from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import httpx

app = FastAPI()

# Разрешаем CORS для GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://anahartlab.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем папку со статикой
app.mount("/static", StaticFiles(directory="static"), name="static")

# Отдача assistant.html по пути /assistant
@app.get("/assistant", response_class=HTMLResponse)
async def serve_assistant():
    with open("static/assistant.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)


# Редирект с корня на /assistant
@app.get("/")
async def root():
    return RedirectResponse(url="/assistant")

@app.post("/assistant")
async def assistant_post():
    return {"status": "OK"}

# Загружаем products.json один раз при старте
with open(os.path.join("static", "products.json"), "r", encoding="utf-8") as f:
    products = json.load(f)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

async def ask_openrouter(message: str):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "openai/gpt-4o",
        "messages": [{"role": "user", "content": message}],
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

def find_products(query: str):
    query_lower = query.lower()
    results = []
    for product in products:
        if (query_lower in product.get("name", "").lower()
            or query_lower in product.get("title", "").lower()
            or query_lower in product.get("description", "").lower()):
            results.append(product)
    return results[:5]

@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message", "")
    found = find_products(user_message)

    if found:
        reply = "Вот что я нашёл:\n"
        for p in found:
            reply += f"- {p['title']} (в наличии: {p.get('stock', 'нет данных')})\n"
            if "link" in p:
                reply += f"  Подробнее: {p['link']}\n"
        return {"reply": reply}

    # Если ничего не найдено, подключаем OpenRouter GPT
    gpt_reply = await ask_openrouter(user_message)
    return {"reply": gpt_reply}