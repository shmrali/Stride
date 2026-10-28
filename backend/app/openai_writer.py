import os
from typing import Protocol

from dotenv import load_dotenv
from openai import OpenAI


class ResponseWriter(Protocol):
    def draft(self, answer: str) -> str: ...


class OpenAIResponseWriter:
    """Uses OpenAI only after deterministic policy and FAQ checks have passed."""

    def __init__(self, client: OpenAI | None = None, model: str | None = None):
        load_dotenv()
        self.client = client or OpenAI()
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5.5")

    def draft(self, answer: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            instructions=(
                "You write short, warm, non-judgmental replies for Stride, a fitness gym. "
                "Use only the facts in the approved FAQ answer below. "
                "Do not add prices, timings, health claims, medical guidance, or promises. "
                "Do not diagnose, treat, prescribe, or interpret health information."
            ),
            input=f"Approved FAQ answer:\n{answer}",
        )
        drafted = response.output_text.strip()
        if not drafted:
            raise RuntimeError("OpenAI returned an empty response.")
        return drafted
