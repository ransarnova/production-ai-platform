# Production AI Platform

A hands-on, production-oriented AI/GenAI platform project built on AWS.

The goal of this project is not only to demonstrate model invocation, but to progressively build the infrastructure, security, reliability, observability, evaluation, and deployment capabilities required to operate an AI workload in a production-style environment.

The project is developed incrementally so that each architectural component can be understood and tested independently.

## Current Architecture

```text
Client
  |
  v
FastAPI
  |
  +------------------------------+
  |                              |
  v                              v
Direct AI API               RAG API
/ai/v1/ask                  /ai/v1/rag
  |                              |
  v                              v
Amazon Bedrock             Bedrock Knowledge Base
Converse API                    |
                                 +--> S3 document source
                                 |
                                 +--> Titan Text Embeddings V2
                                 |
                                 +--> S3 Vectors
                                 |
                                 +--> Retrieve + Generate
                                           |
                                           v
                                      Foundation Model
```

## Implemented

### FastAPI Service

The application currently exposes:

```text
GET  /health
POST /ai/v1/ask
POST /ai/v1/rag
```

`/ai/v1/ask` demonstrates direct foundation-model invocation through the Amazon Bedrock Converse API.

`/ai/v1/rag` demonstrates a managed Retrieval-Augmented Generation workflow using Amazon Bedrock Knowledge Bases.

### API Validation

Pydantic models define the application API contract and validate incoming requests before model invocation.

Input length is constrained to help control invalid requests, excessive token consumption, latency, and cost.

### Amazon Bedrock Integration

The application integrates with Amazon Bedrock through Boto3.

Model and AWS configuration are externalized rather than hardcoded in application source.

### Retrieval-Augmented Generation

The project first implements the core RAG mechanics manually for learning purposes:

```text
Document
   |
   v
Chunking
   |
   v
Embedding
   |
   v
Vector representation
   |
   v
Similarity search
   |
   v
Relevant context
   |
   v
LLM generation
```

A simple local vector index is used to demonstrate embeddings and cosine similarity before moving to managed AWS services.

### Managed RAG

The managed implementation uses:

```text
Amazon S3
   |
   v
Amazon Bedrock Knowledge Base
   |
   v
Titan Text Embeddings V2
   |
   v
Amazon S3 Vectors
   |
   v
Semantic retrieval
   |
   v
Retrieve and Generate
```

The application returns both generated answers and source references.

### Grounding

The RAG generation prompt instructs the model to:

- answer using retrieved policy information
- avoid outside knowledge
- avoid inventing policies, thresholds, approvals, or requirements
- explicitly abstain when sufficient information is unavailable

Example abstention behavior:

```text
I don't know based on the available policy information.
```

### Citation Handling

Retrieved source references are extracted from Bedrock responses and exposed through the application API.

Duplicate source URIs are removed before returning the response to the client.

### Failure Handling

AWS SDK errors are abstracted behind application-specific service exceptions.

The public API returns controlled HTTP errors instead of exposing raw AWS exceptions or internal infrastructure information.

### AI Evaluation

A small golden evaluation dataset is included under:

```text
evals/
```

The evaluation suite independently checks:

```text
Retrieval behavior
Generation behavior
Overall RAG behavior
```

The current dataset includes both:

- answerable policy questions
- questions that should cause the model to abstain

The initial evaluation dataset is intentionally small and is intended as a regression baseline rather than a measure of overall model accuracy.

Run evaluations with:

```bash
python -m evals.run_evals
```

## Project Structure

```text
production-ai-platform/
|
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── bedrock.py
│   ├── rag.py
│   └── retrieval.py
|
├── data/
│   └── lending-policy.txt
|
├── evals/
│   ├── cases.json
│   └── run_evals.py
|
├── scripts/
│   └── ingest.py
|
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
└── README.md
```

## Configuration

Application configuration is provided through environment variables.

Create a local `.env` based on:

```text
.env.example
```

Example:

```text
AWS_REGION=ap-south-1
BEDROCK_MODEL_ID=<bedrock-model-or-inference-profile-id>
BEDROCK_KNOWLEDGE_BASE_ID=<knowledge-base-id>
BEDROCK_RAG_MODEL_ARN=<bedrock-model-or-inference-profile-arn>
```

Do not commit `.env`, AWS credentials, account-specific identifiers, or secrets.

## Running Locally

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements-dev.txt
```

Start the API:

```bash
python -m uvicorn app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## Security

The repository is designed so that credentials and environment-specific configuration are not stored in source control.

Security controls currently include:

- environment-based configuration
- `.env` exclusion from Git
- pre-commit secret scanning using Gitleaks
- API input validation
- controlled error responses
- no AWS credentials embedded in application source

AWS authentication should use the standard AWS credential provider chain during local development and workload IAM roles when deployed to AWS.

## Planned Production Layers

The project will progressively add:

```text
Application
    |
    +-- Containerization
    |
    +-- Amazon ECR
    |
    +-- AWS runtime deployment
    |
    +-- IAM workload identity
    |
    +-- API Gateway / private application connectivity
    |
    +-- Authentication and authorization
    |
    +-- AI security and guardrails
    |
    +-- Structured logging and observability
    |
    +-- AI-specific metrics and tracing
    |
    +-- Reliability, retries, timeouts and scaling
    |
    +-- Expanded RAG evaluation
    |
    +-- Security testing
    |
    +-- CI/CD
    |
    +-- Infrastructure as Code
    |
    +-- Cost controls
```

## Learning Objectives

This project is intended to demonstrate practical understanding of:

- production-oriented AI platform architecture
- Amazon Bedrock model invocation
- embeddings and vector search
- Retrieval-Augmented Generation
- Bedrock Knowledge Bases
- grounding and hallucination reduction
- citation and source attribution
- AI evaluation
- API design
- cloud security
- containerized AI workloads
- observability and reliability
- CI/CD and infrastructure automation

## Status

Current milestone:

```text
FastAPI + Bedrock + Managed RAG + Grounding + Citations + Evaluation
```

Next milestone:

```text
Production containerization and AWS runtime deployment
```

This repository is a technical learning and engineering project rather than a representation of a commercially operated production AI system.