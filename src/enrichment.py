import os
from openai import OpenAI
from src.schemas import CountryMetadata

class ContentEnricher:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.debug = os.getenv("DEBUG", "False").lower() == "true"

    def extract_metadata(self, text):
        """
        Extracts structured metadata using GPT-4o-mini.
        """
        if self.debug:
            print("  > [DEBUG] Generating dummy metadata...")
            # --- UPDATED DUMMY DATA ---
            dummy = CountryMetadata(
                country="Debug_istan",
                iso_code="DBG",
                region="Localhost",
                income_group="High Income",  
                eqx_rank=99,
                other_countries_mentioned=["Utopia", "Atlantis"], # <--- New field
                themes=["debug", "test"],
                trend_direction="flat"
            )
            return dummy, {"cost": 0.0}

        # Real API Call (No changes needed to logic, just the prompt will now fill the new model)
        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract structured metadata from the following text."},
                {"role": "user", "content": text[:4000]} # Send first 4k chars context
            ],
            response_format=CountryMetadata,
        )

        usage = completion.usage
        cost = (usage.prompt_tokens * 0.15 / 1e6) + (usage.completion_tokens * 0.60 / 1e6)
        
        return completion.choices[0].message.parsed, {"cost": cost}

    def generate_summary(self, text):
        if self.debug:
            return "This is a debug summary.", {"cost": 0.0}
            
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Summarize this country report in 3 sentences, focusing on key strengths and weaknesses."},
                {"role": "user", "content": text[:10000]} 
            ]
        )
        usage = completion.usage
        cost = (usage.prompt_tokens * 0.15 / 1e6) + (usage.completion_tokens * 0.60 / 1e6)
        
        return completion.choices[0].message.content, {"cost": cost}