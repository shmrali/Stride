from pydantic import BaseModel, Field, HttpUrl


class FAQEntry(BaseModel):
    id: str
    category: str
    question: str
    answer: str
    link_text: str | None = None
    url: HttpUrl | None = None


class FAQDataset(BaseModel):
    schema_version: str
    dataset_name: str
    language: str
    updated_on: str
    total_questions: int = Field(ge=0)
    questions: list[FAQEntry]


class ChatResponse(BaseModel):
    final_response: str
    category: str
    confidence: str
    escalated: bool
    urgent: bool = False
    source_faq_id: str | None = None
    decision_basis: str
    writer_status: str = "not_used"


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2_000)
    context: list[str] = Field(default_factory=list, max_length=2)
