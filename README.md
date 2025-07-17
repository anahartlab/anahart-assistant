# ANAHART Assistant

Ассистент для сайта ANAHART. Отвечает на запросы клиентов, ищет товары по описанию, названию, размеру и наличию.

## Запуск на Render

1. Залейте этот проект на GitHub
2. Зайдите на https://render.com, нажмите "New + → Web Service"
3. Укажите:
   - Build command: `pip install -r requirements.txt`
   - Start command: `python server.py`
4. Добавьте переменную окружения:
   - `OPENAI_API_KEY` — ваш ключ OpenAI
