from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Question to send to the AI model",
    )


class TokenUsage(BaseModel):
    input_tokens: int
    output_tokens: int


class AskResponse(BaseModel):
    answer: str
    model: str
    usage: TokenUsage


class Source(BaseModel):
    uri: str


class RagResponse(BaseModel):
    answer: str
    sources: list[Source]
    session_id: str | None = None
