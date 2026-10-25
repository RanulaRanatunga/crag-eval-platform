import os
from typing import TypedDict, List
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

load_dotenv()

class GraphState(TypedDict):
    query: str
    documents: List[str]
    generation: str
    relevance_grade: str
    hallucination_grade: str

def get_llm():
    return ChatOpenAI(model="gpt-4o", temperature=0)

def retrieve_node(state: GraphState):
    mock_docs = [
        "Document 1: Kubernetes auto-remediation requires proper RBAC.",
        "Document 2: LLM hallucinations can be mitigated using Corrective RAG."
    ]
    return {"documents": mock_docs}

def grade_documents_node(state: GraphState):
    grade = "yes"
    return {"relevance_grade": grade}

def rewrite_query_node(state: GraphState):
    better_query = state["query"] + " (optimized)"
    return {"query": better_query}

def generate_answer_node(state: GraphState):
    prompt = f"Answer the query based on context.\nQuery: {state['query']}\nContext: {state['documents']}"
    llm = get_llm()
    answer = llm.invoke(prompt).content
    return {"generation": answer}

def hallucination_check_node(state: GraphState):
    return {"hallucination_grade": "pass"}

def decide_to_generate(state: GraphState):
    if state.get("relevance_grade") == "yes":
        return "generate"
    return "rewrite"

workflow = StateGraph(GraphState)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("grade_documents", grade_documents_node)
workflow.add_node("rewrite_query", rewrite_query_node)
workflow.add_node("generate_answer", generate_answer_node)
workflow.add_node("hallucination_check", hallucination_check_node)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "generate": "generate_answer",
        "rewrite": "rewrite_query"
    }
)
workflow.add_edge("rewrite_query", "retrieve")
workflow.add_edge("generate_answer", "hallucination_check")
workflow.add_edge("hallucination_check", END)

crag_app = workflow.compile()

def run_crag_pipeline(query: str):
    if not os.getenv("OPENAI_API_KEY"):
        return {
            "query": query,
            "documents": [],
            "generation": "Error: OPENAI_API_KEY is not set.",
            "relevance_grade": "no",
            "hallucination_grade": "error"
        }
    inputs = {"query": query}
    return crag_app.invoke(inputs)
