import os
from typing import Optional

import google.generativeai as genai

DEFAULT_GEMINI_MODEL = "gemini-2.5-pro"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)

DEFAULT_GENERATION_CONFIG: dict[str, float | int] = {
    "temperature": 0.75,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 384,
}


def _merge_generation_config(
    overrides: Optional[dict[str, float | int]] = None,
) -> dict[str, float | int]:
    config = DEFAULT_GENERATION_CONFIG.copy()
    if overrides:
        for key, value in overrides.items():
            if value is not None:
                config[key] = value
    return config


def _extract_text_from_candidate(candidate) -> str:
    content = getattr(candidate, "content", None)
    if not content:
        return ""


def _build_fallback_question(
    role: str,
    company: str,
    round_type: str,
    difficulty: str,
    previous_questions: Optional[list] = None,
) -> str:
    normalized_round = (round_type or "").strip().lower()
    normalized_diff = (difficulty or "").strip().lower()
    company_label = company.strip() if company else "the company"
    role_label = role.strip() if role else "this role"

    templates: dict[str, list[str]] = {
        "coding": [
            "How would you design a scalable solution to handle real-time data processing for {company_label}?",
            "Describe your approach to debugging a complex performance issue in production systems.",
        ],
        "behavioral": [
            "Tell me about a time you convinced stakeholders to pursue a different strategy at {company_label}.",
            "Describe a challenging situation with a teammate and how you resolved it.",
        ],
        "warm up": [
            "What excites you most about joining {company_label} as a {role_label}?",
            "How do you stay current with industry trends relevant to this opportunity?",
        ],
        "role related": [
            "Walk me through how you would prioritize competing projects as a {role_label} at {company_label}.",
            "How would you measure success for the {role_label} role within the first 90 days?",
        ],
    }

    bank = templates.get(normalized_round) or templates.get("role related")
    previous = set(previous_questions or [])
    for template in bank:
        formatted = template.format(company_label=company_label, role_label=role_label)
        if formatted not in previous:
            return formatted if formatted.endswith("?") else f"{formatted}?"

    generic = (
        f"What would be your strategy for succeeding as a {role_label} at {company_label} "
        f"during a {round_type or 'practice'} round?"
    ).strip()
    return generic if generic.endswith("?") else f"{generic}?"
    parts = getattr(content, "parts", None) or []
    snippets: list[str] = []
    for part in parts:
        text = getattr(part, "text", None)
        if text:
            snippets.append(text.strip())
    return "\n".join(filter(None, snippets)).strip()


def _extract_text_from_response(response) -> str:
    if not response:
        return ""
    try:
        quick_text = getattr(response, "text", None)
        if quick_text:
            text_value = quick_text.strip()
            if text_value:
                return text_value
    except ValueError:
        # Gemini raises when no valid Part exists—fall back to manual parsing.
        pass

    candidates = getattr(response, "candidates", None) or []
    for candidate in candidates:
        candidate_text = _extract_text_from_candidate(candidate)
        if candidate_text:
            return candidate_text
    return ""


def validate_google_api_key(
    api_key: str,
    generation_config: Optional[dict[str, float | int]] = None,
) -> None:
    """Raise if the provided API key fails a lightweight validation call."""
    if not api_key or not api_key.strip():
        raise ValueError("GOOGLE_API_KEY missing. Provide it via .env before generating questions.")

    try:
        genai.configure(api_key=api_key)
        effective_config = _merge_generation_config(generation_config)

        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            generation_config=effective_config,
        )
        model.count_tokens("ping")
    except Exception as exc:
        raise RuntimeError(f"GOOGLE_API_KEY validation failed: {exc}") from exc


def generate_question(
    role: str,
    company: str,
    round_type: str,
    difficulty: str,
    previous_questions: Optional[list] = None,
    api_key: str | None = None,
    generation_config: Optional[dict[str, float | int]] = None,
) -> str:

    if not api_key:
        raise ValueError("GOOGLE_API_KEY missing. Provide it via .env before generating questions.")

    # Generate using Gemini
    try:
        genai.configure(api_key=api_key)
        effective_config = _merge_generation_config(generation_config)
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            generation_config=effective_config,
        )
        prior_list = "\n".join(f"- {q}" for q in (previous_questions or [])) or "None"
        prompt = f"""
You are acting as an expert interview coach. Craft one concise and challenging interview question.
Role: {role}
Company: {company or 'N/A'}
Round: {round_type}
Difficulty: {difficulty}
Previously asked questions:
{prior_list}

Return only the question text.
"""
        response = model.generate_content(prompt)
        question = _extract_text_from_response(response)
        if question:
            if not question.endswith("?"):
                question += "?"
            return question
        finish_reasons = ", ".join(
            filter(
                None,
                [
                    str(getattr(candidate, "finish_reason", ""))
                    for candidate in getattr(response, "candidates", [])
                ],
            )
        )
        if "2" in finish_reasons or "SAFETY" in finish_reasons.upper():
            return _build_fallback_question(
                role=role,
                company=company,
                round_type=round_type,
                difficulty=difficulty,
                previous_questions=previous_questions,
            )
        raise RuntimeError(
            "Gemini returned an empty response"
            + (f" (finish reasons: {finish_reasons})" if finish_reasons else "")
        )
    except Exception as exc:
        raise RuntimeError(f"Gemini question generation failed: {exc}") from exc
