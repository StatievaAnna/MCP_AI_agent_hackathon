# from fastapi import FastAPI
# from pydantic import BaseModel
# from fastapi.middleware.cors import CORSMiddleware
# from typing import List
# from datetime import datetime

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class PHQ9Submission(BaseModel):
#     answers: List[int]


# @app.post("/survay")
# def receive_phq9(submission: PHQ9Submission):
#     score = sum(submission.answers)
#     print(f"Оценка PHQ-9: {score}")
#     return {"score": score, "severity": classify_score(score)}

# def classify_score(score: int) -> str:
#     if score <= 4:
#         return "Минимальная депрессия"
#     elif score <= 9:
#         return "Лёгкая депрессия"
#     elif score <= 14:
#         return "Умеренная депрессия"
#     elif score <= 19:
#         return "Умеренно тяжёлая депрессия"
#     else:
#         return "Тяжёлая депрессия"


# class SurveyData(BaseModel):
#     answers: List[int]

# class ChatMessage(BaseModel):
#     text: str
#     sender: str

# def save_chat_message(text: str, sender: str):
#     with open("chat_history.txt", "a", encoding='utf-8') as f:
#         f.write(f"{datetime.now()} - {sender}: {text}\n")

# @app.post("/survey")
# async def submit_survey(data: SurveyData):
#     return {"message": "Данные сохранены"}

# @app.post("/api/chat")
# async def handle_chat(message: ChatMessage):
#     save_chat_message(message.text, message.sender)

#     #базовый ответ эхо
#     bot_response = "Это автоматический ответ. Ваше сообщение: " + message.text
#     save_chat_message(bot_response, "bot")

#     return {"text": bot_response, "sender": "bot"}


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime
import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
from config import MODEL_API_KEY


load_dotenv()

app = FastAPI(
    title="Психологический чат-бот с AI",
    description="API для чат-бота с психологическим ассистентом"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# MODEL_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=MODEL_API_KEY) if MODEL_API_KEY else None

chat_histories: Dict[str, List[Dict]] = {}
system_message = {
    "role": "system",
    "content": (
        "Ты — вежливый, внимательный ассистент-психолог. "
        "Ты должен сам начать диалог и задавать вопросы по поводу самочувствия клиента. "
        "Твоя задача — мягко расспрашивать пользователя о его состоянии, симптомах, самочувствии и переживаниях. "
        "Не делай поспешных выводов. Сначала узнай все необходимые детали.\n\n"
        "Когда соберешь достаточно информации, ты можешь сделать предварительное предположение о диагнозе. "
        "При назначении диагноза и методов лечения, изучи доступные тебе источники. "
        "Если пользователь отвечает коротко или неясно — уточняй, переспрашивай, проявляй сочувствие."
    )
}


class PHQ9Submission(BaseModel):
    answers: List[int]

class ChatMessage(BaseModel):
    text: str
    sender: str
    chat_id: str


def classify_score(score: int) -> str:
    """Классификация результатов теста PHQ-9"""
    if score <= 4:
        return "Минимальная депрессия"
    elif score <= 9:
        return "Лёгкая депрессия"
    elif score <= 14:
        return "Умеренная депрессия"
    elif score <= 19:
        return "Умеренно тяжёлая депрессия"
    else:
        return "Тяжёлая депрессия"

def save_chat_history(chat_id: str, text: str, sender: str):
    if chat_id not in chat_histories:
        chat_histories[chat_id] = []

    entry = {
        "role": sender,
        "content": text,
        # "timestamp": datetime.now().isoformat()
    }
    chat_histories[chat_id].append(entry)

    # with open(f"chat_{chat_id}.log", "a", encoding='utf-8') as f:
    #     f.write(f"{entry['timestamp']} - {sender}: {text}\n")

def load_tools_from_openapi(openapi_url: str):
    try:
        response = requests.get(openapi_url)
        response.raise_for_status()
        openapi = response.json()

        tools = []
        name_to_path_map = {}
        paths = openapi.get("paths", {})

        for path, methods in paths.items():
            for method, operation in methods.items():
                if method.lower() != "get":
                    continue

                parameters = operation.get("parameters", [])
                properties = {}
                required = []

                for param in parameters:
                    if param.get("in") != "query":
                        continue

                    name = param["name"]
                    schema = param.get("schema", {})
                    param_type = schema.get("type", "string")

                    json_type = (
                        "string" if param_type not in {"integer", "number", "boolean"} else param_type
                    )

                    properties[name] = {
                        "type": json_type,
                        "description": param.get("description", "")
                    }

                    if param.get("required"):
                        required.append(name)

                operation_id = operation.get("operationId") or path.strip("/").replace("/", "_")
                description = operation.get("description", "")
                name_to_path_map[operation_id] = path

                tool = {
                    "type": "function",
                    "function": {
                        "name": operation_id,
                        "description": description,
                        "parameters": {
                            "type": "object",
                            "properties": properties,
                            "required": required
                        }
                    }
                }
                tools.append(tool)

        return tools, name_to_path_map
    except Exception as e:
        print(f"Ошибка загрузки инструментов: {e}")
        return [], {}

def call_mcp_function(name: str, args: dict, name_to_path_map: dict) -> dict:
    base_url = "http://localhost:8000"
    path = name_to_path_map.get(name)

    if not path:
        return {"error": f"Unknown function name: {name}"}

    url = f"{base_url}{path}"
    # print(f"Вызов функции '{name}' по адресу: {url} с параметрами: {args}")

    try:
        response = requests.get(url, params=args)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

def generate_ai_response(messages: list) -> str:
    if not client:
        return "Извините, сервис временно недоступен. Попробуйте позже."

    try:
        openapi_url = "http://localhost:8000/openapi.json"
        tools, name_to_path_map = load_tools_from_openapi(openapi_url)
        print(f'messages: {messages}')

        for i in range(10):
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.7
            )

            msg = response.choices[0].message

            if not msg.tool_calls:
                return msg.content

            tool_call = msg.tool_calls[0]
            args = json.loads(tool_call.function.arguments)
            func_name = tool_call.function.name

            mcp_result = call_mcp_function(func_name, args, name_to_path_map)
            # print("Результаты MCP:", mcp_result)

            messages.append(msg)
            messages.append({
                "role": "tool",
                "content": json.dumps(mcp_result),
                "tool_call_id": tool_call.id,
                "name": func_name
            })

        return msg.content if msg else "Не удалось получить ответ от модели"
    except Exception as e:
        print(f"Ошибка при генерации ответа: {str(e)}")
        return "Извините, произошла ошибка при обработке вашего запроса."

def start_new_chat(chat_id: str, score: int = None) -> str:
    if chat_id not in chat_histories:
        chat_histories[chat_id] = [system_message]

    if score is not None:
        severity = classify_score(score)
        welcome_msg = (
            f"Привет! По результатам теста у вас {severity.lower()}. "
            "Давайте обсудим ваше состояние подробнее. Как вы себя чувствуете?"
        )
    else:
        welcome_msg = "Привет! Я ваш психологический ассистент. Расскажите, что вас беспокоит?"

    chat_histories[chat_id].append({
        "role": "assistant",
        "content": welcome_msg
    })
    save_chat_history(chat_id, welcome_msg, "assistant")

    return welcome_msg

# API endpoints
@app.post("/survey")
async def handle_survey(submission: PHQ9Submission):
    if len(submission.answers) != 9:
        raise HTTPException(status_code=400, detail="Должно быть 9 ответов")

    score = sum(submission.answers)
    chat_id = str(datetime.now().timestamp())

    welcome_msg = start_new_chat(chat_id, score)

    return {
        "score": score,
        "severity": classify_score(score),
        "chat_id": chat_id,
        "message": welcome_msg
    }

@app.post("/api/chat")
async def handle_chat(message: ChatMessage):
    if message.chat_id not in chat_histories:
        start_new_chat(message.chat_id)

    if message.text.lower() in {"выход", "exit", "quit"}:
        bot_response = "Спасибо за беседу! Если будут вопросы - обращайтесь."
    else:
        # chat_histories[message.chat_id].append({
        #     "role": "user",
        #     "content": message.text
        # })
        save_chat_history(message.chat_id, message.text, "user")

        bot_response = generate_ai_response(chat_histories[message.chat_id])
        # chat_histories[message.chat_id].append({
        #     "role": "assistant",
        #     "content": bot_response
        # })
        save_chat_history(message.chat_id, bot_response, "assistant")

    return {
        "text": bot_response,
        "sender": "bot",
        "chat_id": message.chat_id
    }

@app.get("/chat_history/{chat_id}")
async def get_chat_history(chat_id: str):
    if chat_id not in chat_histories:
        raise HTTPException(status_code=404, detail="Чат не найден")
    return chat_histories[chat_id]

@app.get("/")
async def root():
    return {
        "message": "Психологический чат-бот API",
        "status": "работает",
        "ai_available": bool(client),
        "endpoints": {
            "POST /survey": "Отправить результаты опроса PHQ-9",
            "POST /api/chat": "Отправить сообщение в чат",
            "GET /chat_history/{chat_id}": "Получить историю чата"
        }
    }
