import json
from pathlib import Path

from pydantic import ValidationError

from .schemas import FAQDataset


DATASET_PATH = Path(__file__).parent / "data" / "gym_chatbot_faq.json"


def load_faq_dataset(path: Path = DATASET_PATH) -> FAQDataset:
    """Load the local, reviewed FAQ knowledge base."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        dataset = FAQDataset.model_validate(raw)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        raise RuntimeError("The Stride FAQ dataset is missing or invalid.") from exc

    if dataset.total_questions != len(dataset.questions):
        raise RuntimeError("The Stride FAQ dataset question count does not match its metadata.")
    return dataset
