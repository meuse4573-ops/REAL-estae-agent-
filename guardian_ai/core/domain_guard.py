"""
Domain Guard — Real Estate Restriction Middleware

Runs BEFORE any LLM call to ensure requests fall within real estate scope.
Refuses non-real-estate requests at the gate, never wastes LLM resources on out-of-scope tasks.
"""

from typing import Literal

ALLOWED_KEYWORDS = [
    "contract", "deal", "closing", "inspection", "lender", "buyer", "seller",
    "title", "escrow", "contingency", "addendum", "FAR/BAR", "MLS",
    "appraisal", "earnest money", "disclosure", "E&O", "broker", "agent",
    "TC", "transaction coordinator", "purchase agreement", "title insurance",
    "deed", "mortgage", "pre-approval", "loan commitment", "homestead",
    "property tax", "closing costs", "escrow officer", "title company",
    "listing agreement", "buyer's agent", "seller's agent", "dual agent",
    "commission", "representation", "financing contingency", "inspection contingency",
    "appraisal contingency", "real estate", "transaction", "property",
    "lease", "rental", "landlord", "tenant", "deposit", "lease agreement",
    "commercial property", "residential property", "investment property",
    "flip", "wholesale", "wholesaling", "REI", "real estate investing",
    "FREC", "Chapter 475", "Florida real estate", "REALTOR", "listing",
    "showings", "open house", "mortgage rate", "interest rate", "HUD",
    "settlement statement", "CD", "closing disclosure", "GFE", "good faith estimate",
    "due diligence", "option fee", "option period", " HOA", "HOA fees",
    "community association", "rent roll", "cap rate", "cash flow", "NOI",
    "commercial lease", "triple net", "NNN", "gross lease", "assignment",
    "wholesaler", "lead generation", "marketing", "driving for dollars",
]

UNCLEAR_PHRASES = [
    "how do i", "what is the", "can you", "i need to", "help me",
    "please", "can i", "should i", "would you", "could you",
]

REFUSAL_TEMPLATE = (
    "I'm your Real Estate Deal Co-Pilot, specialized in transaction management. "
    "I can't help with {request}, but I'm here to protect your deals, predict problems, "
    "and keep your transactions on track."
)

UNCLEAR_TEMPLATE = (
    "I'm your Real Estate Deal Co-Pilot, specialized in Florida real estate transactions. "
    "How does this relate to your real estate transaction?"
)


def _normalize(text: str) -> str:
    return text.lower()


def _has_real_estate_keyword(text: str) -> bool:
    normalized = _normalize(text)
    for keyword in ALLOWED_KEYWORDS:
        if keyword.lower() in normalized:
            return True
    return False


def _is_real_estate_context(text: str) -> bool:
    normalized = _normalize(text)
    real_estate_signals = [
        "my deal", "my transaction", "my closing", "my property",
        "my contract", "my offer", "my client", "my buyer", "my seller",
        "real estate", "florida", "far/bar", "frec",
    ]
    for signal in real_estate_signals:
        if signal in normalized:
            return True
    return False


def _is_declared_competence(text: str) -> bool:
    normalized = _normalize(text)
    for phrase in UNCLEAR_PHRASES:
        if phrase in normalized:
            return _is_real_estate_context(text)
    return False


def check_domain(request_text: str) -> Literal["ALLOW", "REFUSE", "UNCLEAR"]:
    if not request_text or not request_text.strip():
        return "REFUSE"

    has_keyword = _has_real_estate_keyword(request_text)
    has_context = _is_real_estate_context(request_text)
    is_declared = _is_declared_competence(request_text)

    if has_keyword or has_context:
        return "ALLOW"

    if is_declared:
        return "UNCLEAR"

    return "REFUSE"


def get_response(request_text: str) -> str:
    decision = check_domain(request_text)

    if decision == "ALLOW":
        return "ALLOW"

    elif decision == "REFUSE":
        return REFUSAL_TEMPLATE.format(request=request_text)

    else:
        return UNCLEAR_TEMPLATE


def get_response_with_llm(request_text: str, llm_func=None):
    """
    Full middleware flow: check domain, return early if refused/uncertain,
    otherwise call LLM.
    """
    decision = check_domain(request_text)

    if decision == "ALLOW":
        if llm_func is None:
            return "ALLOW"
        return llm_func(request_text)

    elif decision == "REFUSE":
        return REFUSAL_TEMPLATE.format(request=request_text)

    else:
        return UNCLEAR_TEMPLATE


if __name__ == "__main__":
    print("=== Domain Guard Tests ===\n")

    print("--- REAL ESTATE REQUESTS (Should Pass) ---")
    real_estate_requests = [
        "Review my FAR/BAR contract for the Orlando property closing next week",
        "What is the deadline for the inspection contingency on my deal?",
        "Help me understand the earnest money requirements for Florida transactions",
    ]
    for req in real_estate_requests:
        result = check_domain(req)
        print(f"[{result}] {req}\n")

    print("\n--- NON-REAL-ESTATE REQUESTS (Should Be Refused) ---")
    non_real_estate_requests = [
        "Write me a Python function to sort a list",
        "What's 15% of 847?",
        "Write a poem about springtime in the mountains",
    ]
    for req in non_real_estate_requests:
        result = check_domain(req)
        response = get_response(req)
        print(f"[{result}] {req}")
        print(f"   Response: {response}\n")