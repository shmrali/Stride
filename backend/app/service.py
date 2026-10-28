import logging
import re

from .openai_writer import ResponseWriter
from .schemas import ChatResponse, FAQDataset
from .tools import CATEGORY_CONTEXTS, Classification, classify_message, retrieve_faq


PLACEHOLDER_PATTERN = re.compile(r"\[[^\]]+\]")
logger = logging.getLogger(__name__)

PLACEHOLDER_GUIDANCE = {
    "Membership plans and pricing": "Exact membership and offer details are being confirmed. The Stride team can help you compare the current options.",
    "Joining and onboarding": "A few joining details are being confirmed. The Stride team can tell you exactly what to bring and how to get started.",
    "Trainers and personalised coaching": "Specific trainer and coaching details are being confirmed. The Stride team can help match you with the right support.",
    "Injury or post-surgery fitness support": "The Stride team can confirm the available recovery-support options after you have clearance from your doctor or physiotherapist.",
    "Lifestyle-health fitness support": "The Stride team can explain the available fitness-support options while working within your qualified clinician's guidance.",
    "Diet and fitness assessments": "The Stride team can confirm the current assessment and nutrition-support details for you.",
    "Classes, facilities, and gym hours": "Current class, facility and timing details are being confirmed. The Stride team can share the latest information.",
}

FOLLOW_UP_QUESTIONS = {
    "membership_enquiry": "Would you like help with plans, pricing, payment options, or joining Stride?",
    "joining_onboarding": "Are you looking to join online, visit the gym first, or understand what happens on your first day?",
    "trainer_coaching": "Would you like to know about personal training, beginner guidance, or support for a specific fitness goal?",
    "recovery_support": "Could you share whether you are returning after an injury or surgery? Please make sure you have guidance from your doctor or physiotherapist first.",
    "lifestyle_health": "Would you like to know how Stride personalises fitness support around your goals and your clinician’s guidance?",
    "assessment_diet": "Would you like to know about fitness assessments, personalised diet support, or how plans are reviewed?",
    "facilities_classes": "Would you like to know about classes, facilities, gym hours, or visiting Stride?",
    "unclear": "Are you looking for memberships, trainers, classes, fitness assessments, or safe support for getting started?",
}


class StrideChatService:
    """A four-stage, FAQ-grounded chatbot service for Stride."""

    def __init__(self, dataset: FAQDataset, writer: ResponseWriter | None = None):
        self.dataset = dataset
        self.writer = writer

    @staticmethod
    def _has_unresolved_details(text: str) -> bool:
        return bool(PLACEHOLDER_PATTERN.search(text))

    @staticmethod
    def _verified_part_of_answer(answer: str) -> str:
        """Keep complete sentences, while removing every sentence that exposes a placeholder."""
        sentences = re.split(r"(?<=[.!?])\s+", answer)
        verified = [sentence.strip() for sentence in sentences if sentence.strip() and not PLACEHOLDER_PATTERN.search(sentence)]
        return " ".join(verified)

    def _incomplete_faq_response(self, category: str, answer: str) -> str:
        verified = self._verified_part_of_answer(answer)
        guidance = PLACEHOLDER_GUIDANCE.get(
            category,
            "Some Stride details are still being confirmed. The Stride team can share the current information.",
        )
        return f"{verified}\n\n{guidance}" if verified else guidance

    @staticmethod
    def _friendly_no_match_response(classification_tag: str) -> str:
        question = FOLLOW_UP_QUESTIONS.get(classification_tag, FOLLOW_UP_QUESTIONS["unclear"])
        return f"I’d be happy to help you find the right information. {question}"

    def _safety_response(self, classification: Classification) -> ChatResponse | None:
        if classification.tag == "greeting":
            return ChatResponse(
                final_response=(
                    "Hi! Welcome to Stride 👋 I’m here to help you explore memberships, trainers, classes and a safe way to get started. "
                    "What would you like to know?"
                ),
                category=classification.tag,
                confidence="high",
                escalated=False,
                decision_basis="friendly_greeting",
            )
        if classification.tag == "thanks":
            return ChatResponse(
                final_response="You’re very welcome! If there’s anything else you’d like to know about Stride, I’m here to help.",
                category=classification.tag,
                confidence="high",
                escalated=False,
                decision_basis="friendly_acknowledgement",
            )
        if classification.tag == "goodbye":
            return ChatResponse(
                final_response="Take care, and whenever you’re ready, Stride will be here to help with your next step.",
                category=classification.tag,
                confidence="high",
                escalated=False,
                decision_basis="friendly_goodbye",
            )
        if classification.tag == "medical_or_urgent":
            if classification.urgent:
                return ChatResponse(
                    final_response=(
                        "Please stop exercising and seek urgent medical care now. "
                        "I cannot assess symptoms such as chest pain, severe breathing difficulty, fainting or severe dizziness."
                    ),
                    category=classification.tag,
                    confidence="high",
                    escalated=True,
                    urgent=True,
                    decision_basis="urgent_medical_safety",
                )
            return ChatResponse(
                final_response=(
                    "I can share general information about Stride, but I cannot assess this medically or decide whether exercise is safe for you. "
                    "Please speak with your doctor or physiotherapist before starting or changing exercise."
                ),
                category=classification.tag,
                confidence="high",
                escalated=True,
                decision_basis="medical_safety_boundary",
            )
        if classification.tag == "prompt_injection":
            return ChatResponse(
                final_response="I can help with Stride memberships, facilities, trainers and general programme information.",
                category=classification.tag,
                confidence="high",
                escalated=False,
                decision_basis="safe_redirect",
            )
        if classification.tag == "complaint_or_human_help":
            return ChatResponse(
                final_response="I’m sorry this needs personal attention. Please contact the Stride team so they can help you directly.",
                category=classification.tag,
                confidence="high",
                escalated=True,
                decision_basis="human_support",
            )
        return None

    def process_message(self, message: str, context: list[str] | None = None) -> ChatResponse:
        classification = classify_message(message)
        safety_response = self._safety_response(classification)
        if safety_response:
            return safety_response

        allowed_categories = CATEGORY_CONTEXTS.get(classification.tag)
        # For a vague follow-up, reuse only the previous user question to narrow the FAQ area.
        # Context arrives from the browser and is never stored by the backend.
        retrieval_message = message
        if classification.tag == "unclear" and context:
            previous_question = context[-1]
            previous_classification = classify_message(previous_question)
            allowed_categories = CATEGORY_CONTEXTS.get(previous_classification.tag)
            if allowed_categories:
                retrieval_message = f"{previous_question}\n{message}"

        match = retrieve_faq(
            self.dataset,
            retrieval_message,
            allowed_categories=allowed_categories,
        )
        if not match.entry:
            return ChatResponse(
                final_response=self._friendly_no_match_response(classification.tag),
                category=classification.tag,
                confidence="low",
                escalated=False,
                decision_basis="no_confident_match",
            )

        if self._has_unresolved_details(match.entry.answer):
            return ChatResponse(
                final_response=self._incomplete_faq_response(match.entry.category, match.entry.answer),
                category=match.entry.category,
                confidence="medium",
                escalated=False,
                source_faq_id=match.entry.id,
                decision_basis="unresolved_faq_detail",
            )

        response_text = match.entry.answer
        writer_status = "not_used"
        if self.writer:
            try:
                response_text = self.writer.draft(match.entry.answer)
                writer_status = "used"
                logger.info("OpenAI writer used for FAQ %s", match.entry.id)
            except Exception as exc:
                # The approved FAQ answer remains the safe fallback if the API is unavailable.
                logger.warning("OpenAI writer fallback: %s", type(exc).__name__)
                response_text = match.entry.answer
                writer_status = "fallback"

        confidence = "high" if match.score >= 0.7 else "medium"
        return ChatResponse(
            final_response=response_text,
            category=match.entry.category,
            confidence=confidence,
            escalated=False,
            source_faq_id=match.entry.id,
            decision_basis="faq_match",
            writer_status=writer_status,
        )
