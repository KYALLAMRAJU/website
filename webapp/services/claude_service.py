import anthropic
from django.conf import settings


class ClaudeService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def ask(self, prompt: str):
        response = self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=700,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
