from fastapi import FastAPI, HTTPException

from app.bedrock import BedrockServiceError, ask_model
from app.models import AskRequest, AskResponse


app = FastAPI(
    title="Production AI Platform",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/ai/v1/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    try:
        return ask_model(request.question)
    except BedrockServiceError:
        raise HTTPException(
            status_code=503, detail="AI service temporarily unavailable")
