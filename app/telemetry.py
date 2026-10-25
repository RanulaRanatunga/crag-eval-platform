import os
import urllib.request
from dotenv import load_dotenv
from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

load_dotenv()

def is_phoenix_reachable(endpoint: str) -> bool:
    try:
        base_url = endpoint.split("/v1/traces")[0]
        req = urllib.request.Request(base_url, method="GET")
        with urllib.request.urlopen(req, timeout=0.5):
            return True
    except Exception:
        return False

def setup_telemetry():
    endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006/v1/traces")
    enable_telemetry = os.getenv("ENABLE_TELEMETRY", "auto").lower()

    if enable_telemetry == "false":
        return

    tracer_provider = TracerProvider()

    if enable_telemetry == "true" or is_phoenix_reachable(endpoint):
        tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
        trace.set_tracer_provider(tracer_provider)
        LangChainInstrumentor().instrument()
        print(f"Telemetry configured. Sending traces to {endpoint}")
    else:
        trace.set_tracer_provider(tracer_provider)
        print("Phoenix collector not detected at localhost:6006. Running server without remote tracing.")
