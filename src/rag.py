import time
from typing import Iterator, Union
from src.retrieval import VectorRetriever
from src.generation import LLMGenerator
from src.router import IntentRouter
from src.tracing import get_tracer

tracer = get_tracer("orchestrator")

class RAGOrchestrator:
    def __init__(self):
        self.retriever = VectorRetriever()
        self.generator = LLMGenerator()
        self.router = IntentRouter()

    def process_query(self, query: str) -> Iterator[str]:
        # Note: This function is now a GENERATOR
        with tracer.start_as_current_span("rag_process") as span:
            
            # 1. ROUTING
            intent = self.router.analyze_query(query)
            
            # Guardrails
            if intent.category == "malicious":
                yield "I cannot fulfill that request."
                return
            if intent.category == "off_topic":
                yield "I can only answer questions about the EQx Economic Report."
                return

            # 2. RETRIEVAL
            results = []
            if intent.target_countries:
                for country in intent.target_countries:
                    # We fetch specific chunks for each identified country
                    results.extend(self.retriever.search(query, limit=3, country_filter=country))
            else:
                # Fallback to general search if no specific country is named
                results = self.retriever.search(query, limit=5)

            if not results:
                yield "I couldn't find any relevant information."
                return

            # 3. GENERATION (Yields the stream from LLMGenerator)
            yield from self.generator.generate(query, results, intent=intent)

    def close(self):
        """Cleanup resources (like the Weaviate client)."""
        if self.retriever:
            self.retriever.close()