from django.test import TestCase, Client
from unittest.mock import patch


class ClaudeAPITest(TestCase):

    def setUp(self):
        self.client = Client()

    @patch("webapp.services.claude_service.ClaudeService.ask")
    def test_claude_api_success(self, mock_ask):
        mock_ask.return_value = "Hello from mock"

        response = self.client.post(
            "/api/claude/",
            data={"prompt": "hi"},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("response", response.json())
        self.assertEqual(
            response.json()["response"],
            "Hello from mock"
        )

    def test_claude_api_only_post(self):
        response = self.client.get("/api/claude/")

        self.assertEqual(response.status_code, 200)
