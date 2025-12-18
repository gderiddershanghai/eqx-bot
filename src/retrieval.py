import weaviate
import os
import weaviate.classes as wvc
from dotenv import load_dotenv
from src.tracing import get_tracer

load_dotenv()
tracer = get_tracer("retrieval")

class VectorRetriever:
    def __init__(self):
        self.client = weaviate.connect_to_local(
            headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")}
        )
        self.collection_name = "EQxReport"

    def search(self, query: str, limit: int = 5, country_filter: str = None):
        with tracer.start_as_current_span("weaviate_search") as span:
            span.set_attribute("search.query", query)
            span.set_attribute("search.limit", limit)
            
            collection = self.client.collections.get(self.collection_name)

            filters = None
            if country_filter:
                span.set_attribute("search.filter.country", country_filter)
                # Filter logic: Match if 'country' is the target 
                # OR if 'other_countries_mentioned' contains the target
                filters = wvc.query.Filter.any_of([
                    wvc.query.Filter.by_property("country").equal(country_filter),
                    wvc.query.Filter.by_property("other_countries_mentioned").contains_any([country_filter])
                ])

            # Hybrid Search
            response = collection.query.hybrid(
                query=query,
                limit=limit,
                filters=filters,
                alpha=0.5,
                return_metadata=wvc.query.MetadataQuery(score=True)
            )

            results = []
            for obj in response.objects:
                results.append({
                    "text": obj.properties.get("text"),
                    "country": obj.properties.get("country"),
                    "mentioned": obj.properties.get("other_countries_mentioned", []),
                    "income_group": obj.properties.get("income_group"),
                    "themes": obj.properties.get("themes", []),
                    "score": obj.metadata.score,
                })
            
            span.set_attribute("search.results_count", len(results))
            return results

    def close(self):
        self.client.close()