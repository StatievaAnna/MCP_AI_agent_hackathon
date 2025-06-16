from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PHQ9Submission(BaseModel):
    session_id: int
    answers: Dict[str, str] 

@app.post("/survay")
def receive_phq9(submission: PHQ9Submission): 
    return {
        "message": "Ответы успешно получены",
        "session_id": submission.session_id,
        "total_questions": len(submission.answers)
    }

