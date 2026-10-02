import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import settings
from app.models import RagResponse, Source

import json


bedrock_agent_runtime = boto3.client(
    "bedrock-agent-runtime",
    region_name=settings.aws_region,
)


class RagServiceError(Exception):
    """Raised when the managed RAG request fails."""


def ask_knowledge_base(question: str) -> RagResponse:
    try:
        response = bedrock_agent_runtime.retrieve_and_generate(
            input={
                "text": question,
            },
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": settings.bedrock_knowledge_base_id,
                    "modelArn": settings.bedrock_model_id,

                    "retrievalConfiguration": {
                        "vectorSearchConfiguration": {
                            "numberOfResults": 3,
                        }
                    },

                    "generationConfiguration": {
                        "promptTemplate": {
                            "textPromptTemplate": """
                            You are an enterprise policy assistant.

                            Use only the information contained in the search results
                            to answer the user's question.

                            Do not use outside knowledge.

                            If the search results do not contain enough information
                            to answer the question, respond exactly:

                            I don't know based on the available policy information.

                            Do not invent policies, thresholds, requirements, or approvals.

                            Search results:
                            $search_results$

                            $output_format_instructions$
                            """
                        }
                    },
                },
            },
        )
        print(
            json.dumps(
                response,
                indent=2,
                default=str,
            )
        )

    except (ClientError, BotoCoreError) as exc:
        print(f"Bedrock RAG error: {exc}")
        raise RagServiceError(
            "Knowledge Base request failed"
        ) from exc

    source_uris = set()

    for citation in response.get("citations", []):
        for reference in citation.get("retrievedReferences", []):
            location = reference.get("location", {})
            s3_location = location.get("s3Location", {})

            uri = s3_location.get("uri")

            if uri:
                source_uris.add(uri)

    sources = [
        Source(uri=uri)
        for uri in sorted(source_uris)
    ]

    return RagResponse(
        answer=response["output"]["text"],
        sources=sources,
        session_id=response.get("sessionId"),
    )


def retrieve_context(question: str) -> list[str]:
    try:
        response = bedrock_agent_runtime.retrieve(
            knowledgeBaseId=settings.bedrock_knowledge_base_id,
            retrievalQuery={
                "text": question,
            },
            retrievalConfiguration={
                "vectorSearchConfiguration": {
                    "numberOfResults": 3,
                }
            },
        )

    except (ClientError, BotoCoreError) as exc:
        raise RagServiceError(
            "Knowledge Base retrieval failed"
        ) from exc

    return [
        result["content"]["text"]
        for result in response.get("retrievalResults", [])
    ]
