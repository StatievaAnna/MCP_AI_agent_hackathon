from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PHQ9Submission(BaseModel):
    answers: list[int]

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
