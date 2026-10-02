import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import settings
from app.models import AskResponse, TokenUsage

from app.retrieval import retrieve_context


bedrock_client = boto3.client(
    "bedrock-runtime",
    region_name=settings.aws_region,
)


class BedrockServiceError(Exception):
    """raised whhen the bedrock service call fails."""


def ask_model(question: str) -> AskResponse:

    context = retrieve_context(question)

    grounded_prompt = f"""
    Answer the question using only the provided context.

    If the answer is not contained in the context, say:
    "I don't know based on the provided information."

    Context:
    {context}

    Question:
    {question}
    """

    try:
        response = bedrock_client.converse(
            modelId=settings.bedrock_model_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "text": grounded_prompt,
                        }
                    ],
                }
            ],
            inferenceConfig={
                "maxTokens": 500,
                "temperature": 0.2,
            },
        )
    except (ClientError, BotoCoreError) as exc:
        raise BedrockServiceError("bedrock request failed") from exc

    answer = response["output"]["message"]["content"][0]["text"]

    usage = response["usage"]

    return AskResponse(
        answer=answer,
        model=settings.bedrock_model_id,
        usage=TokenUsage(
            input_tokens=usage["inputTokens"],
            output_tokens=usage["outputTokens"],
        ),
    )
