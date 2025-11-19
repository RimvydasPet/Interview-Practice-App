import os
from typing import Optional

import google.generativeai as genai

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)

def generate_question(role: str, company: str, round_type: str, difficulty: str,
                     previous_questions: Optional[list] = None, api_key: str | None = None) -> str:
  
    if not api_key:
        raise ValueError("GOOGLE_API_KEY missing. Provide it via .env before generating questions.")

    # Generate using Gemini
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name=GEMINI_MODEL)
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
        question = response.text.strip() if response and response.text else ""
        if question:
            if not question.endswith("?"):
                question += "?"
            return question
        raise RuntimeError("Gemini returned an empty response")
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Gemini question generation failed: {exc}") from exc
