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
async def assistant_post(request: Request):
    data = await request.json()
    user_message = data.get("message", "")

    # Получаем ключевые слова через ИИ
    keywords = await extract_keywords(user_message)
    if not keywords:
        keywords = user_message.split()

    # Ищем по ключевым словам
    query = " ".join(keywords)
    found = find_products(query)

    if found:
        reply = "Вот что я нашёл:\n"
        for p in found:
            reply += f"- {p['title']} (в наличии: {p.get('stock', 'нет данных')})\n"
            if "link" in p:
                reply += f"  Подробнее: {p['link']}\n"
        return {"reply": reply}

    # Если ничего не найдено — шаблон
    fallback_message = (
        "🤖 В связи с большой загрузкой ИИ время ответа может быть увеличено.\n\n"
        "Вы можете самостоятельно посмотреть товары здесь:\n"
        "🌀 <a href=\"https://anahartlab.github.io/wear.html\" target=\"_blank\">Одежда</a>\n"
        "🌈 <a href=\"https://anahartlab.github.io/tapestries/instock.html\" target=\"_blank\">Полотна</a>\n"
        "📩 <a href=\"https://t.me/anahart\" target=\"_blank\">Написать в Telegram</a>"
    )
    return {"reply": fallback_message}

# Загружаем products.json один раз при старте
with open(os.path.join("static", "products.json"), "r", encoding="utf-8") as f:
    products = json.load(f)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# Извлечение ключевых слов из сообщения пользователя через OpenRouter
async def extract_keywords(message: str) -> list[str]:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    prompt = (
        "Извлеки ключевые слова из следующего запроса пользователя для поиска по базе данных товаров.\n"
        "Ответ верни как список слов, без лишнего текста. Пример: ['футболка', 'будда']\n\n"
        f"Запрос: {message}"
    )
    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [{"role": "user", "content": prompt}],
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        response.raise_for_status()
        json_data = response.json()
        content = json_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        try:
            keywords = eval(content.strip())
            return keywords if isinstance(keywords, list) else []
        except:
            return []

import re

def normalize(text):
    return re.sub(r"[^\w\s]", "", text.lower())

def find_products(query: str):
    query_words = normalize(query).split()
    results = []

    for product in products:
        searchable = " ".join([
            normalize(product.get("name", "")),
            normalize(product.get("title", "")),
            normalize(product.get("description", ""))
        ])
        if all(word in searchable for word in query_words):
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

    # Если ничего не найдено
    fallback_message = (
        "🤖 В связи с большой загрузкой ИИ время ответа может быть увеличено.\n\n"
        "Вы можете самостоятельно посмотреть товары здесь:\n"
        "🌀 Одежда: https://anahartlab.github.io/wear.html\n"
        "🌈 Полотна: https://anahartlab.github.io/tapestries/instock.html\n"
        "📩 Или написать художнику напрямую в Telegram: https://t.me/anahart"
    )
    return {"reply": fallback_message}