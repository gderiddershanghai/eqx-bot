import os
import yaml
from openai import OpenAI
from typing import List, Dict, Iterator
from src.tracing import get_tracer

tracer = get_tracer("generation")

class LLMGenerator:
    def __init__(self, model="gpt-4o", prompt_name="analyst"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.prompt_name = prompt_name
        self.system_prompt = self._load_prompt(prompt_name)

    def _load_prompt(self, prompt_name: str) -> str:
        """Loads prompt from YAML file."""
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, "prompts", f"{prompt_name}.yaml")
        
        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
                return f"{data['instructions']}\n\nROLE: {data['role']}"
        except FileNotFoundError:
            return "You are an economic assistant. Answer based on context."

    def generate(self, query: str, context_chunks: List[Dict], intent=None) -> Iterator[str]:
        # The span remains open until the generator finishes yielding
        with tracer.start_as_current_span("llm_generate") as span:
            
            # --- 1. BUILD CONTEXT ---
            context_str = ""
            for i, chunk in enumerate(context_chunks):
                country = chunk.get('country', 'Unknown')
                text = chunk.get('text', '')
                context_str += f"[Source {i+1}: {country}]\n{text}\n\n"

            # --- 2. PREPARE MESSAGES ---
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Context Data:\n{context_str}\n\nUser Question: {query}"}
            ]

            # --- 3. API CALL (STREAMING) ---
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
                stream=True, 
                stream_options={"include_usage": True} 
            )
            
            # --- 4. YIELD CHUNKS ---
            for chunk in stream:
                # 4a. Yield Content
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                
                # 4b. Log Token Usage (Available in the last chunk)
                if chunk.usage:
                    span.set_attribute("gen.tokens.input", chunk.usage.prompt_tokens)
                    span.set_attribute("gen.tokens.output", chunk.usage.completion_tokens)