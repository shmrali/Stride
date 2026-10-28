import re
import unicodedata
from dataclasses import dataclass

from .schemas import FAQDataset, FAQEntry


URGENT_PATTERNS = (
    r"\bchest pain\b", r"\b(can(?:not|'t)|unable to) breathe\b", r"\bdifficulty breathing\b",
    r"\bfaint(?:ed|ing)?\b", r"\bunconscious\b", r"\bsevere dizziness\b",
    r"\bsevere pain\b", r"\bbleed(?:ing)?\b", r"\bheart attack\b",
)
MEDICAL_PATTERNS = (
    r"\bdiagnos", r"\btreatment\b", r"\bmedicin(?:e|es)\b", r"\bdosage\b",
    r"\binterpret .* (?:report|test|result)", r"\bshould i exercise\b",
    r"\bis it safe .* exercise\b", r"\bdoctor(?:'s)? clearance\b",
)
RECOVERY_PATTERNS = (r"\binjur", r"\bsurger", r"\boperation\b", r"\bphysiotherap", r"\brecovery\b", r"\bknee problem\b", r"\bshoulder problem\b")
LIFESTYLE_PATTERNS = (r"\bdiabetes?\b", r"\bcholesterol\b", r"\bblood pressure\b", r"\bhypertension\b", r"\bweight management\b", r"\bweight loss\b", r"\blose weight\b")
COMPLAINT_PATTERNS = (r"\bcomplaint\b", r"\brefund\b", r"\bcharged\b", r"\bpoor service\b", r"\bdissatisfied\b")
HUMAN_PATTERNS = (r"\bspeak to (?:a |someone|the )", r"\bhuman\b", r"\bcall me\b", r"\bcontact staff\b")
INJECTION_PATTERNS = (r"ignore (?:all |your )?(?:previous )?instructions", r"system prompt", r"reveal .*instructions", r"act as (?:a )?doctor", r"pretend .* doctor")
GREETING_PATTERNS = (r"^\s*(?:hi|hello|hey|good morning|good afternoon|good evening)[!,. ]*$",)
THANKS_PATTERNS = (r"^\s*(?:thanks|thank you|thx)[!,. ]*$",)
GOODBYE_PATTERNS = (r"^\s*(?:bye|goodbye|see you|talk to you later)[!,. ]*$",)
MEMBERSHIP_PATTERNS = (r"\bmember", r"\bplan", r"\bpric", r"\bcost\b", r"\btrial\b", r"\bpayment", r"\bjoin\b", r"\benrol", r"\bsign up\b", r"\bdiscount", r"\bfreeze")
JOINING_PATTERNS = (r"\bhow (?:do|can) i join\b", r"\bsign up\b", r"\benrol(?:l)?\b", r"\bfirst day\b", r"\borientation\b", r"\bwhat (?:do|should) i bring\b", r"\bdocuments?\b")
TRAINER_PATTERNS = (r"\btrainer", r"\bpersonal training", r"\bcoach", r"\bmuscle gain\b", r"\bstrength training\b", r"\bmobility\b")
ASSESSMENT_PATTERNS = (r"\bassessment", r"\bdiet", r"\btest result", r"\bnutrition")
FACILITY_PATTERNS = (r"\bhours?\b", r"\bopening", r"\bweekends?\b", r"\bsundays?\b", r"\bholidays?\b", r"\bclass", r"\bfacilit", r"\bparking", r"\blockers?\b", r"\bchanging room", r"\blocation")

STOP_WORDS = {"a", "an", "and", "are", "at", "can", "do", "does", "for", "from", "help", "how", "i", "in", "is", "it", "me", "my", "of", "on", "or", "our", "please", "tell", "the", "this", "to", "we", "what", "when", "where", "with", "you", "your", "stride", "gym"}
ALIASES = {
    "price": {"cost", "pricing", "fee"}, "cost": {"price", "pricing", "fee"},
    "join": {"enrol", "membership", "member", "signup"}, "signup": {"join", "enrol", "membership"},
    "trainer": {"coach", "training"}, "coach": {"trainer", "training"},
    "train": {"exercise", "exercising", "workout"}, "training": {"exercise", "workout"},
    "exercise": {"train", "training", "workout"}, "exercising": {"exercise", "train", "workout"},
    "injury": {"recovery", "physiotherapy", "knee", "shoulder"},
    "surgery": {"recovery", "postoperative", "operation"}, "operation": {"surgery", "recovery"},
    "knee": {"injury", "recovery"}, "shoulder": {"injury", "recovery"},
    "diet": {"nutrition", "meal"}, "hours": {"opening", "timings"}, "opening": {"hours", "timings"},
    "locker": {"lockers", "changing"}, "lockers": {"locker", "changing"},
    "weight": {"management", "loss"}, "loss": {"weight", "management"},
    "diabetes": {"bloodsugar", "lifestyle"}, "cholesterol": {"heart", "lifestyle"},
}

# Agent 2 only searches the knowledge-base areas approved by Agent 1.
# This prevents a recovery question containing the word "join" from returning a general joining FAQ.
CATEGORY_CONTEXTS = {
    "membership_enquiry": {"Membership plans and pricing", "Joining and onboarding"},
    "joining_onboarding": {"Joining and onboarding"},
    "trainer_coaching": {"Trainers and personalised coaching"},
    "recovery_support": {"Injury or post-surgery fitness support"},
    "lifestyle_health": {"Lifestyle-health fitness support"},
    "assessment_diet": {"Diet and fitness assessments"},
    "facilities_classes": {"Classes, facilities, and gym hours"},
}


def _matches(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


@dataclass(frozen=True)
class Classification:
    tag: str
    urgent: bool = False


def classify_message(message: str) -> Classification:
    """Classify a message, always placing medical safety ahead of FAQ retrieval."""
    if _matches(message, URGENT_PATTERNS):
        return Classification("medical_or_urgent", urgent=True)
    if _matches(message, MEDICAL_PATTERNS):
        return Classification("medical_or_urgent")
    if _matches(message, INJECTION_PATTERNS):
        return Classification("prompt_injection")
    if _matches(message, GREETING_PATTERNS):
        return Classification("greeting")
    if _matches(message, THANKS_PATTERNS):
        return Classification("thanks")
    if _matches(message, GOODBYE_PATTERNS):
        return Classification("goodbye")
    if _matches(message, COMPLAINT_PATTERNS) or _matches(message, HUMAN_PATTERNS):
        return Classification("complaint_or_human_help")
    if _matches(message, RECOVERY_PATTERNS):
        return Classification("recovery_support")
    if _matches(message, LIFESTYLE_PATTERNS):
        return Classification("lifestyle_health")
    if _matches(message, JOINING_PATTERNS):
        return Classification("joining_onboarding")
    if _matches(message, MEMBERSHIP_PATTERNS):
        return Classification("membership_enquiry")
    if _matches(message, TRAINER_PATTERNS):
        return Classification("trainer_coaching")
    if _matches(message, ASSESSMENT_PATTERNS):
        return Classification("assessment_diet")
    if _matches(message, FACILITY_PATTERNS):
        return Classification("facilities_classes")
    return Classification("unclear")


def _tokens(text: str) -> set[str]:
    normalized = unicodedata.normalize("NFKD", text).casefold()
    normalized = normalized.replace("sign up", "signup").replace("work out", "workout")
    tokens = {token for token in re.findall(r"[a-z0-9]+", normalized) if len(token) > 1 and token not in STOP_WORDS}
    expanded = set(tokens)
    # Handles straightforward wording variations such as "locker" / "lockers".
    for token in tokens:
        if token.endswith("ies") and len(token) > 4:
            expanded.add(token[:-3] + "y")
        elif token.endswith("s") and len(token) > 3 and not token.endswith("ss"):
            expanded.add(token[:-1])
    for token in tokens:
        expanded.update(ALIASES.get(token, set()))
    return expanded


@dataclass(frozen=True)
class Match:
    entry: FAQEntry | None
    score: float


def retrieve_faq(dataset: FAQDataset, message: str, allowed_categories: set[str] | None = None) -> Match:
    """Return one grounded FAQ match, or no match rather than guessing."""
    candidates = [
        entry for entry in dataset.questions
        if allowed_categories is None or entry.category in allowed_categories
    ]
    normalized = " ".join(re.findall(r"[a-z0-9]+", message.casefold()))
    for entry in candidates:
        question = " ".join(re.findall(r"[a-z0-9]+", entry.question.casefold()))
        if normalized == question:
            return Match(entry, 1.0)

    message_tokens = _tokens(message)
    best_entry: FAQEntry | None = None
    best_score = 0.0
    for entry in candidates:
        question_tokens = _tokens(entry.question)
        answer_tokens = _tokens(entry.answer)
        primary_overlap = len(message_tokens & question_tokens)
        answer_overlap = len(message_tokens & answer_tokens)
        if not primary_overlap and not answer_overlap:
            continue
        score = 0.75 * primary_overlap / max(len(message_tokens), 1) + 0.25 * primary_overlap / max(len(question_tokens), 1)
        if score > best_score:
            best_entry, best_score = entry, score
    return Match(best_entry if best_score >= 0.36 else None, round(min(best_score, 1.0), 3))
