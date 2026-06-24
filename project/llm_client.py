import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class GroqLLM:
    def __init__(self):
        # Groq uses the exact same interface as OpenAI!
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables. Please check your .env file.")

        # By changing the base_url, we redirect the OpenAI library to use Groq's servers which are 100% FREE
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        # Using Llama 3.1 - completely free and excellent reasoning
        self.model = "llama-3.1-8b-instant"

    def generate(self, system_prompt, user_prompt, temperature=0.7):
        import time
        time.sleep(2) # Adding a tiny sleep to respect Groq's free tier rate limits
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=2048,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error from LLM request: {str(e)}"
