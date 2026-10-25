# Corrective RAG (CRAG) Evaluation Platform

## Project Scope

Large Language Model applications that rely on standard Retrieval-Augmented Generation (RAG) often fail when the retrieval mechanism returns irrelevant, incomplete, or noisy documents. When fed irrelevant context, models are prone to hallucinating answers or failing to address the user request.

This platform implements a Corrective Retrieval-Augmented Generation (CRAG) workflow combined with an automated evaluation harness and distributed telemetry. The scope of this project includes:

1. Self-correcting retrieval graph built on LangGraph to grade document relevance before generating responses, automatically rewriting queries when retrieved context is inadequate.
2. Observability pipeline integrating OpenTelemetry and Arize Phoenix to trace query execution, graph state transitions, and model latencies.
3. Quality gates powered by DeepEval to evaluate faithfulness and contextual precision within automated CI/CD pipelines, preventing faulty pipelines from reaching production.
4. Production-ready API service built with FastAPI exposing structured inference endpoints.

## What the System Does

### 1. Corrective RAG Workflow

The core reasoning logic is defined as a directed graph in `app/graph.py` using LangGraph:

- Retrieval: Receives an incoming query and retrieves relevant context documents from the document store or vector database.
- Relevance Grading: Evaluates whether the retrieved context contains information relevant to the user query.
- Conditional Routing:
  - If documents are graded relevant, the graph routes directly to answer generation.
  - If documents are graded irrelevant or insufficient, the graph routes to query rewriting to refine search keywords and loops back to retrieval.
- Answer Generation: Synthesizes a factual response grounded strictly in the validated context.
- Hallucination Verification: Grades the generated answer against the source context before returning the payload to the caller.

### 2. Telemetry and Tracing

The platform uses `app/telemetry.py` to instrument LangChain and LangGraph calls using OpenInference and OpenTelemetry SDK. Traces are dispatched asynchronously via `BatchSpanProcessor` to an Arize Phoenix collector instance running locally or remotely on port 6006. This provides step-by-step inspection of:

- Retrieval document payloads
- Prompt templates and token counts
- LLM latency and token consumption
- Decision paths taken through graph edges

### 3. CI/CD Quality Gates

The `tests/test_rag_quality.py` test suite integrates DeepEval metrics into automated testing:

- Faithfulness: Validates whether the generation is free of factual contradictions against the retrieved context (threshold >= 0.85).
- Contextual Precision: Validates whether relevant context items are ranked higher than irrelevant ones (threshold >= 0.80).

GitHub Actions (`.github/workflows/ai-eval.yml`) executes these tests on every push and pull request against `main`. If metrics fall below required thresholds, deployment jobs are blocked.

## Project Structure

```
crag-eval-platform/
|-- .github/
|   \-- workflows/
|       \-- ai-eval.yml          # GitHub Actions evaluation gate workflow
|-- app/
|   |-- __init__.py
|   |-- graph.py                 # LangGraph CRAG state graph implementation
|   |-- main.py                  # FastAPI application and routing
|   \-- telemetry.py             # OpenTelemetry and Arize Phoenix instrumentation
|-- tests/
|   |-- __init__.py
|   \-- test_rag_quality.py      # DeepEval metric test cases
|-- .env.example                 # Example environment variables
|-- docker-compose.yml           # Arize Phoenix service definition
|-- requirements.txt             # Python dependencies
|-- launch_phoenix.py            # Local Phoenix launcher script
|-- run.py                       # Root launcher script
\-- README.md
```

## Setup and Installation

### Prerequisites

- Python 3.10 or 3.11
- Docker and Docker Compose (required for running the Arize Phoenix tracing service)
- OpenAI API Key

### Step 1: Create and Activate a Virtual Environment

On Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On Linux or macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Copy `.env.example` to create `.env`:

On Windows (PowerShell):
```powershell
Copy-Item .env.example .env
```

On Linux or macOS:
```bash
cp .env.example .env
```

Open `.env` and configure your API keys:
```env
OPENAI_API_KEY=your_openai_api_key_here
PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006/v1/traces
```

### Step 4: Start Arize Phoenix Tracing (Optional but Recommended)

You can run the Phoenix telemetry collector using either Docker or Python:

Option 1 (Using Docker Compose):
```bash
docker compose up -d
```

Option 2 (Using Python without Docker):
```bash
python launch_phoenix.py
```

Once running, access the Phoenix UI at:
```
http://localhost:6006
```

### Step 5: Run the FastAPI Server

You can run the server using any of the following commands:

Option 1 (Recommended launcher):
```bash
python run.py
```

Option 2 (Direct Python module):
```bash
python app/main.py
```

Option 3 (Direct Uvicorn CLI):
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The interactive API documentation (Swagger UI) is accessible at:
```
http://localhost:8000/docs
```

## API Reference

### Health Check

- Method: `GET`
- Path: `/health`
- Response:
```json
{
  "status": "healthy"
}
```

### Process Query

- Method: `POST`
- Path: `/api/v1/query`
- Headers: `Content-Type: application/json`
- Request Body:
```json
{
  "query": "How does Corrective RAG handle irrelevant documents?"
}
```

- Example Response:
```json
{
  "original_query": "How does Corrective RAG handle irrelevant documents?",
  "final_query_used": "How does Corrective RAG handle irrelevant documents?",
  "answer": "Corrective RAG mitigates hallucinations by evaluating the relevance of retrieved documents prior to generation and rewriting queries when the context is insufficient.",
  "documents_retrieved": 2,
  "hallucination_grade": "pass"
}
```

### Example Request Commands

Using curl:
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How does Corrective RAG mitigate hallucinations?"}'
```

Using PowerShell:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/query" -Method Post -ContentType "application/json" -Body '{"query": "How does Corrective RAG mitigate hallucinations?"}' | ConvertTo-Json
```

## Running Evaluations and Tests

To run the DeepEval quality gate test suite locally:

```bash
pytest tests/test_rag_quality.py -v
```

Note: DeepEval tests evaluate live model responses and require a valid `OPENAI_API_KEY` set in your `.env` or system environment. If no key is set, the test will be skipped automatically.

## Conclusion

Standard RAG architectures often suffer from silent retrieval failures and groundedness drift. By coupling LangGraph corrective routing with OpenTelemetry tracing and DeepEval regression testing, this platform establishes a verifiable, self-healing pipeline for production knowledge retrieval.
