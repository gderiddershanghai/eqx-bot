import os
from openai import OpenAI
from src.schemas import QueryIntent

class IntentRouter:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    ####################################################
    # DEFINITIONS OF COMPLEXITY NEED TO CHANGE
    ####################################################
    def analyze_query(self, query: str) -> QueryIntent:
        system_prompt = """
        You are the Query Router for the EQx Economic Report Bot.
        
        Your Goal: Analyze the user's question and extract structured intent, filters, and requirements.
        
        Definitions for Complexity:
        - Low: Simple fact retrieval (e.g., "What is China's rank?").
        - Medium: Single-country analysis or simple comparison (e.g., "How is Japan's healthcare?").
        - High: Multi-step reasoning, synthesis across many countries, or complex scenarios.
        
        Definitions for SQL Lookup:
        - Set True if the user asks for specific rankings ("Top 10"), raw statistics, or sorting.
        - Set False for qualitative questions ("Why is growth slow?").
        
        Definitions for Charts:
        - Set True if the user asks for trends ("over time"), comparisons ("vs"), or distributions.
        """
        
        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini", # 4.1 nano?
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            response_format=QueryIntent
        )
        
        return completion.choices[0].message.parsed