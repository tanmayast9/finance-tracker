import os
import requests

class GeminiClient:
    """Minimal wrapper to call Gemini-like API if GEMINI_API_KEY is present."""
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.base_url = os.getenv('GEMINI_API_URL', 'https://api.gemini.example')

    def available(self):
        return bool(self.api_key)

    def classify_expense(self, description, amount):
        """Example call: send description and amount to LLM for categorization.
        Returns dict {"category": "Food", "confidence": 0.92} or None if not configured.
        """
        if not self.available():
            return None

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'prompt': f"Classify this transaction: '{description}' amount {amount}",
            'max_tokens': 60
        }

        try:
            resp = requests.post(f"{self.base_url}/v1/classify", json=payload, headers=headers, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None
