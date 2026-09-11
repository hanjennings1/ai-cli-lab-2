'''
monkeypatch, a built-in pytest fixture that lets you 
temporarily replace a function (like the real ollama.chat) 
with a fake one, just for the duration of one test
'''


import pytest

from services import ai_client as ai_client_module
from services.ai_client import OllamaChatClient


class TestOllamaChatClient:
    def test_client_initializes_with_defaults(self):
        client = OllamaChatClient()
        assert client.model_name == "llama3.2"
        assert client.history == []

    def test_client_accepts_custom_model_name(self):
        client = OllamaChatClient(model_name="custom-model")
        assert client.model_name == "custom-model"

    def test_send_rejects_blank_prompt(self):
        client = OllamaChatClient()
        with pytest.raises(ValueError):
            client.send("   ")

    def test_send_returns_ai_response(self, monkeypatch):
        client = OllamaChatClient()

        def fake_chat(model, messages):
            return {"message": {"role": "assistant", "content": "Fake AI reply"}}

        monkeypatch.setattr(ai_client_module.ollama, "chat", fake_chat)

        result = client.send("Summarize this project")

        assert result == "Fake AI reply"
        assert client.history == [
            {"role": "user", "content": "Summarize this project"},
            {"role": "assistant", "content": "Fake AI reply"},
        ]

    def test_send_raises_and_rolls_back_history_on_failure(self, monkeypatch):
        client = OllamaChatClient()

        def fake_chat(model, messages):
            raise ConnectionError("service unreachable")

        monkeypatch.setattr(ai_client_module.ollama, "chat", fake_chat)

        with pytest.raises(RuntimeError):
            client.send("This will fail")

        # History should be empty - the failed user message was rolled back
        assert client.history == []

    def test_send_rejects_blank_response_content(self, monkeypatch):
        client = OllamaChatClient()

        def fake_chat(model, messages):
            return {"message": {"role": "assistant", "content": "   "}}

        monkeypatch.setattr(ai_client_module.ollama, "chat", fake_chat)

        with pytest.raises(RuntimeError):
            client.send("Prompt that gets a blank reply")

        assert client.history == []

    def test_reset_clears_history(self):
        client = OllamaChatClient()
        client.history = [{"role": "user", "content": "Old message"}]

        client.reset()

        assert client.history == []

    def test_message_count(self):
        client = OllamaChatClient()
        client.history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello"},
        ]

        assert client.message_count() == 2

    def test_get_transcript_returns_copy(self):
        client = OllamaChatClient()
        client.history = [{"role": "user", "content": "Original"}]

        transcript = client.get_transcript()

        assert transcript == client.history
        assert transcript is not client.history  # different list object

        transcript[0]["content"] = "Changed"
        assert client.history[0]["content"] == "Original"  # internal history untouched