import sys
import types


# Fake out the ollama module if it's not actually installed/importable,
# so tests can run in any environment without needing Ollama running

try:
    import ollama  # noqa: F401
except ModuleNotFoundError:
    fake_ollama = types.ModuleType("ollama")

    def unconfigured_chat(*args, **kwargs):
        raise RuntimeError("ollama.chat was called before being mocked by the tests.")

    fake_ollama.chat = unconfigured_chat
    sys.modules["ollama"] = fake_ollama
