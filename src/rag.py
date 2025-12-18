import time
from src.retrieval import VectorRetriever
from src.generation import LLMGenerator
from src.telemetry import telemetry
from src.router import IntentRouter 

class RAGOrchestrator:
    def __init__(self):
        self.retriever = VectorRetriever()
        self.generator = LLMGenerator() # Default model
        self.router = IntentRouter()

    def process_query(self, query: str):
        print(f"\n  >  Orchestrator: Received '{query}'")
        t0 = time.time()

        # 1. ROUTING
        intent = self.router.analyze_query(query)
        print(f"  >  Router Analysis:")
        print(f"     - Intent: {intent.category}")
        print(f"     - Complexity: {intent.complexity}")
        print(f"     - Chart Needed: {intent.chart_needed}")
        print(f"     - SQL Lookup: {intent.requires_sql_lookup}")
        
        # Future Logic: Swap model based on complexity?
        # if intent.complexity == "high":
        #     self.generator = LLMGenerator(model="o1-preview") 

        # 2. RETRIEVAL (Using the extracted filters)
        results = []
        
        # A. Apply Country Filters
        if intent.target_countries:
            for country in intent.target_countries:
                print(f"     - Fetching chunks for: {country}")
                # Note: We pass the country_filter to the search method
                country_results = self.retriever.search(query, limit=3, country_filter=country)
                results.extend(country_results)
        
        # B. Apply Metadata Filters (Region / Income)
        # (You would update retrieval.py search() to accept these new args like 'region_filter')
        elif intent.filters.income_group or intent.filters.region:
             # Placeholder for future logic:
             # results = self.retriever.search(..., filters=intent.filters)
             print(f"     - Filtering by {intent.filters}")
             results = self.retriever.search(query, limit=5) # Fallback for now

        else:
            # General Search
            results = self.retriever.search(query, limit=5)

        # Log Retrieval
        telemetry.log_event(
            event_type="retrieval",
            query=query,
            start_time=t0,
            metadata={
                "complexity": intent.complexity,
                "chart_needed": intent.chart_needed,
                "filters": intent.target_countries
            }
        )

        if not results:
            return "I couldn't find any relevant data."

        # 3. GENERATION
        # We pass the 'chart_needed' flag to the generator so it knows to output data in a specific format if needed
        answer = self.generator.generate(query, results)
        
        if intent.chart_needed:
            answer += "\n\n[System Note: A chart was requested. In the future, I will render a plot here based on the data.]"

        print(f"  >  Finished in {(time.time() - t0):.2f}s")
        return answer

    def close(self):
        self.retriever.close()