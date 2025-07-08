import openai

class CategorizationService:
    def __init__(self, api_key: str):
        self.api_key = api_key
    def categorize(self, text: str):
        # Placeholder for AI categorization
        return {"category": "General", "summary": text[:100]}
