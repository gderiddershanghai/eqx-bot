import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.openai import OpenAIInstrumentor

def init_tracing():
    # 1. Setup Provider
    provider = TracerProvider(resource=Resource.create({"service.name": "eqx-bot"}))
    
    # 2. Exporter A: Print to Terminal (Standard Output)
    console_exporter = ConsoleSpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(console_exporter))

    # 3. Exporter B: Write to File
    log_file = open("tracing_logs.txt", "a")
    file_exporter = ConsoleSpanExporter(out=log_file)
    provider.add_span_processor(SimpleSpanProcessor(file_exporter))
    
    # 4. Register
    trace.set_tracer_provider(provider)
    
    # 5. Auto-instrument OpenAI
    OpenAIInstrumentor().instrument()
    
    print("🔭 Tracing active: Logs streaming to Terminal AND 'tracing_logs.txt'")

def get_tracer(name):
    return trace.get_tracer(name)