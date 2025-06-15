import os

import openai
import json
import requests
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI
from config import MODEL_API_KEY

import requests

histori = {} 

def load_tools_from_openapi(openapi_url: str):
    response = requests.get(openapi_url)
    openapi = response.json()

    tools = []
    name_to_path_map = {}
    paths = openapi.get("paths", {})

    for path, methods in paths.items():
        for method, operation in methods.items():
            if method.lower() != "get":
                continue  # Обрабатываем только GET-запросы

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

            operation_id = operation.get("operationId")
            if not operation_id:
                # если нет operationId, создаём его на основе пути
                operation_id = path.strip("/").replace("/", "_")

            description = operation.get("description", "")

            # Добавляем в карту соответствий
            name_to_path_map[operation_id] = path

            # Создаём инструмент в формате OpenAI function
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

openapi_url = "http://localhost:8000/openapi.json"
tools, name_to_path_map = load_tools_from_openapi(openapi_url)

# def call_mcp_function(name, args):
#     base_url = "http://localhost:8000/api"
#     if name == "fda_drug_info":
#         print("Вызов fda_drug_info")
#         return requests.get(f"{base_url}/fda", params=args).json()
#     elif name == "pubmed_search":
#         print("Вызов pubmed_search")
#         return requests.get(f"{base_url}/pubmed", params=args).json()
#     elif name == "clinical_trials_search":
#         print("Вызов clinical_trials_search")
#         print(args)
#         return requests.get(f"{base_url}/clinical_trials", params=args).json()
#     return {"error": "Неизвестная функция"}

def call_mcp_function(name, args, name_to_path_map):
    base_url = "http://localhost:8000"

    # Получаем путь из карты
    path = name_to_path_map.get(name)
    if not path:
        return {"error": f"Unknown function name: {name}"}

    url = f"{base_url}{path}"

    print(f"Вызов функции '{name}' по адресу: {url} с параметрами: {args}")

    try:
        response = requests.get(url, params=args)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}


def ask_mcp_assisted_model(messages):
    for i in range(10):
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        msg = response.choices[0].message

        if not msg.tool_calls:
            break

        tool_call = msg.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        func_name = tool_call.function.name

        # Обращение к серверу
        mcp_result = call_mcp_function(func_name, args, name_to_path_map)
        print("Результаты поиска:", mcp_result)

        # Добавляем сообщения: от assistant (инструкция к вызову) и от tool (результат)
        messages.append(msg)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": func_name,
            "content": json.dumps(mcp_result)
        })
    
    messages.append(msg)
    return msg.content

def chat_loop():
    print("💬 Добро пожаловать! Введите 'выход' для завершения диалога.")
    history = [system_message]

    # all_history = {
    #     "id1": history1,
    #     "id2": history2,  
    # }

    while True:
        user_input = input("\n👤 Вы: ")
        if user_input.lower() in {"выход", "exit", "quit"}:
            print("🔚 Диалог завершён.")
            break

        # Добавляем вопрос пользователя в историю
        history.append({"role": "user", "content": user_input})

        # Получаем ответ от модели с учётом всей истории
        reply = ask_mcp_assisted_model(history)

        # Добавляем ответ модели в историю
        history.append({"role": "assistant", "content": reply})

        print("\n🤖 Ассистент:", reply)

histori = {}          

def start_chat(id):
    histori[id] = []
    histori[id].append(system_message)
    # анализ результатов прохождения теста...
    reply = 'Привет! Как ты чувствуешь себя?' # тут будет первое сообщение на основании анализа резов теста
    assistant_message = {"role": "assistant", "content": reply}
    histori[id].append(assistant_message)
    return reply
      
def get_answer(id, user_input):

    if user_input.lower() in {"выход", "exit", "quit"}:
        return("🔚 Диалог завершён пользователем. Спасибо, что поделился со мной своими мыслями и чувствами! Надеюсь, я смог тебе помочь.")   

    # Добавляем вопрос пользователя в историю
    histori[id].append({"role": "user", "content": user_input})

    # Получаем ответ от модели с учётом всей истории
    reply = ask_mcp_assisted_model(histori[id])

    # Добавляем ответ модели в историю
    histori[id].append({"role": "assistant", "content": reply})

    return reply


# 🔁 Точка входа
if __name__ == "__main__":

    client = OpenAI(api_key=MODEL_API_KEY)  # 🔒 Вставь свой API ключ

    system_message = {
        "role": "system",
        "content": (
            "Ты — вежливый, внимательный ассистент-психолог. "
            "Ты должен сам начать диалог и задавать вопросы по поводу самочувствия клиента"
            "Твоя задача — мягко расспрашивать пользователя о его состоянии, симптомах, самочувствии и переживаниях. "
            "Не делай поспешных выводов. Сначала узнай все необходимые детали.\n\n"
            "Когда соберешь достаточно информации, ты можешь сделать предварительное предположение о диагнозе "
            "При назначении диагноза и методов лечения, извучи доступные тебе источники: например, ты можешь исследовать статьи и получать информацию по определенной теме здоровья, получать информацию о различных лекарственных препаратов, важно вбивать название на английском языке"
            "Ты можешь обратиться к серверу несколько раз, если не удалось получить нужную информацию"
            "и обратиться к внешнему медицинскому сервису MCP (через встроенные инструменты), чтобы уточнить диагноз "
            "и получить рекомендации по лечению. "
            "Только после этого сообщи пользователю результаты и рекомендации.\n\n"
            "Если пользователь отвечает коротко или неясно — уточняй, переспрашивай, проявляй сочувствие."
        )
    }
    
    start_message = start_chat("123")
    print(start_message)
    user_input = "У меня тревожность и бессоница 2 недели"
    print(user_input)
    print(get_answer("123", user_input))
    start_message = start_chat("124")
    print(start_message)
    user_input = "У меня тревожность и бессоница 3 месяца. А еще меня мучает жена"
    print(user_input)
    print(get_answer("124", user_input))
    
    # question = "Расскажи об исследованиях на тему diabetes"
    # answer = ask_mcp_assisted_model(question)
    # print("\nОтвет модели:\n", answer)
    # chat_loop()
