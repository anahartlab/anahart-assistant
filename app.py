from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

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

# Пример API-эндпоинта
@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message", "")
    # Здесь можно добавить настоящую обработку
    return {"reply": f"Ты сказал: {user_message}"}