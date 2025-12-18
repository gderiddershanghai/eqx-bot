import weaviate
import os
import weaviate.classes as wvc
from dotenv import load_dotenv

load_dotenv()

class VectorRetriever:
    def __init__(self):
        self.client = weaviate.connect_to_local(
            headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")}
        )
        self.collection_name = "EQxReport"

    def search(self, query: str, limit: int = 5, country_filter: str = None):
        collection = self.client.collections.get(self.collection_name)

        filters = None
        if country_filter:
            ####### what if the document has china in the countries mentioned??
            filters = wvc.query.Filter.by_property("country").equal(country_filter)

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
                "text": obj.properties["text"],
                "country": obj.properties.get("country"),
                "income_group": obj.properties.get("income_group"),
                "themes": obj.properties.get("themes", []),
                "score": obj.metadata.score,
            })
        
        return results

    def close(self):
        self.client.close()