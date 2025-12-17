import os
from openai import OpenAI
from src.schemas import CountryMetadata

class ContentEnricher:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"
        
        # Simple pricing for gpt-4o-mini (approximate)
        # Input: $0.15 / 1M tokens, Output: $0.60 / 1M tokens
        self.input_cost_per_m = 0.15
        self.output_cost_per_m = 0.60

    def _calculate_cost(self, usage):
        if not usage:
            return 0.0
        input_cost = (usage.prompt_tokens / 1_000_000) * self.input_cost_per_m
        output_cost = (usage.completion_tokens / 1_000_000) * self.output_cost_per_m
        return input_cost + output_cost

    def extract_metadata(self, text: str):
        """
        Returns: (CountryMetadata object, dict_of_usage_stats)
        """
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": "Extract the following metadata from the country report. Be precise."},
                {"role": "user", "content": text[:15000]} 
            ],
            response_format=CountryMetadata,
        )
        
        # Capture Tracking Data
        usage = completion.usage
        stats = {
            "input_tokens": usage.prompt_tokens,
            "output_tokens": usage.completion_tokens,
            "cost": self._calculate_cost(usage)
        }
        
        return completion.choices[0].message.parsed, stats

    def generate_summary(self, text: str):
        """
        Returns: (summary_string, dict_of_usage_stats)
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Summarize the following text in one dense, keyword-rich sentence."},
                {"role": "user", "content": text[:10000]}
            ],
            max_tokens=250, 
        )
        
        usage = response.usage
        stats = {
            "input_tokens": usage.prompt_tokens,
            "output_tokens": usage.completion_tokens,
            "cost": self._calculate_cost(usage)
        }
        
        return response.choices[0].message.content.strip(), stats