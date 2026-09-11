import ollama


class OllamaChatClient:
    """Generic, reusable client for talking to a local Ollama chat model.

    Knows nothing about projects, tasks, or prompts - only how to send
    a message and get a response back from the model.
    """

    def __init__(self, model_name="llama3.2"):
        self.model_name = model_name
        self.history = []


    def send(self, prompt):
        # Reject empty/blank prompts before doing anything
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        # Add the user's message to the running history
        user_message = {"role": "user", "content": prompt.strip()}
        self.history.append(user_message)

        try:
            # Call the model with the full conversation so far
            response = ollama.chat(model=self.model_name, messages=self.history)

            # Handle both dict-style and object-style responses
            try:
                content = response["message"]["content"]
            except (TypeError, KeyError):
                content = getattr(response, "message", None)
                content = getattr(content, "content", None)

            # Reject missing/blank/non-string replies
            if not isinstance(content, str) or not content.strip():
                raise RuntimeError("unusable response")

        except Exception:
            # Roll back the user message so history stays consistent
            self.history.remove(user_message)
            raise RuntimeError("AI service request failed.")

        # Only store the reply once we know it's valid
        assistant_message = {"role": "assistant", "content": content}
        self.history.append(assistant_message)

        return content


    def reset(self):
        # Clear conversation history
        self.history=[]

    def message_count(self):
        #Number of messages stored so far
        return len(self.history)

    def get_transcript(self):
        # Return a copy so users can't change internal history directly
        return [message.copy() for message in self.history]