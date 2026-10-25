import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest
from dotenv import load_dotenv
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric, ContextualPrecisionMetric
from app.graph import run_crag_pipeline

load_dotenv()

pytestmark = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY is required to run DeepEval tests."
)

def test_rag_hallucination_and_precision():
    input_query = "How does Corrective RAG handle irrelevant documents?"
    graph_result = run_crag_pipeline(input_query)
    
    actual_output = graph_result.get("generation", "")
    retrieved_context = graph_result.get("documents", [])

    test_case = LLMTestCase(
        input=input_query,
        actual_output=actual_output,
        retrieval_context=retrieved_context
    )
    
    faithfulness_metric = FaithfulnessMetric(threshold=0.85)
    context_precision_metric = ContextualPrecisionMetric(threshold=0.80)

    assert_test(test_case, [faithfulness_metric, context_precision_metric])
