from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PHQ9Submission(BaseModel):
    answers: List[int]




@app.post("/survay")
def receive_phq9(submission: PHQ9Submission):
    score = sum(submission.answers)
    print(f"Оценка PHQ-9: {score}")
    return {"score": score, "severity": classify_score(score)}

def classify_score(score: int) -> str:
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


class SurveyData(BaseModel):
    answers: List[int]

class ChatMessage(BaseModel):
    text: str
    sender: str

def save_chat_message(text: str, sender: str):
    with open("chat_history.txt", "a", encoding='utf-8') as f:
        f.write(f"{datetime.now()} - {sender}: {text}\n")

@app.post("/survey")
async def submit_survey(data: SurveyData):
    return {"message": "Данные сохранены"}

@app.post("/api/chat")
async def handle_chat(message: ChatMessage):
    save_chat_message(message.text, message.sender)

    #базовый ответ эхо
    bot_response = "Это автоматический ответ. Ваше сообщение: " + message.text
    save_chat_message(bot_response, "bot")

    return {"text": bot_response, "sender": "bot"}
