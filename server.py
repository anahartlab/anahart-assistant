from flask import Flask, request, jsonify
import json
import os
import openai

app = Flask(__name__)
openai.api_key = os.environ.get("OPENROUTER_API_KEY")

# Загружаем товары
with open("products.json", "r", encoding="utf-8") as f:
    products = json.load(f)

def find_products(query):
    query_lower = query.lower()
    results = []
    for p in products:
        if (query_lower in p["name"].lower()
            or query_lower in p["title"].lower()
            or query_lower in p["description"].lower()):
            results.append(p)
    return results[:5]

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    found = find_products(user_message)
    if found:
        reply = "Вот что я нашёл:
"
        for p in found:
            reply += f'– {p["title"]} ({p["stock"]})
👉 <a href="{p["link"]}" target="_blank">Смотреть</a>

'
    else:
        # fallback to GPT
        gpt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты ассистент ANAHART. Отвечай вежливо и по существу."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = gpt_response.choices[0].message["content"]

    return jsonify({"reply": reply})
