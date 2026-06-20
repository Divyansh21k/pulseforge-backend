import json

import google.generativeai as genai

from app.core.config import settings

genai.configure(api_key=settings.gemini_api_key)

_model = genai.GenerativeModel("gemini-2.5-flash")

SKILL_EXTRACTION_PROMPT = """You are a skill normalization engine for a hackathon platform.
Given free-text input describing a person's skills, return ONLY a JSON array of
normalized, lowercase, hyphenated skill tags (e.g. "machine-learning", "backend", "react").
Use a small consistent vocabulary (backend, frontend, mobile, machine-learning,
data-science, devops, cloud, ui-ux, blockchain, cybersecurity, python, javascript,
java, react, nodejs, sql, etc. -- infer the closest matching tags, don't invent overly
specific ones). Do not include any explanation, markdown, or extra text -- output ONLY
the JSON array.

Input: {raw_text}
Output:"""


def extract_skills(raw_text: str) -> list[str]:
    if not raw_text or not raw_text.strip():
        return []

    prompt = SKILL_EXTRACTION_PROMPT.format(raw_text=raw_text)
    response = _model.generate_content(prompt)
    text = response.text.strip()

    if text.startswith("`"):
        text = text.strip("")
        text = text.replace("json", "", 1).strip()

    try:
        skills = json.loads(text)
        if isinstance(skills, list):
            return [str(s).strip().lower() for s in skills if s]
    except json.JSONDecodeError:
        pass

    return []
