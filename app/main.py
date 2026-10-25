import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from app.graph import run_crag_pipeline
from app.telemetry import setup_telemetry

load_dotenv()
setup_telemetry()

app = FastAPI(title="Corrective RAG (CRAG) Gateway")

class QueryRequest(BaseModel):
    query: str

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/query")
async def process_query(request: QueryRequest):
    result = run_crag_pipeline(request.query)
    return {
        "original_query": request.query,
        "final_query_used": result.get("query"),
        "answer": result.get("generation"),
        "documents_retrieved": len(result.get("documents", [])),
        "hallucination_grade": result.get("hallucination_grade")
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
