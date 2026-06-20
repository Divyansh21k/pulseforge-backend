"""
Skill extraction utility (PS1 section 4.1 / 6.1).

Primary path: Gemini-based NLP extraction, normalizing free text into a
small consistent skill vocabulary.

Fallback path: if the Gemini API key is missing, the API call fails, or
the response can't be parsed as JSON (rate limits, network issues, key
not configured during a live demo), we fall back to a deterministic
keyword-matching extractor against the same vocabulary. This guarantees
/api/skills/extract never 500s during judging -- a live demo failing on
a flaky external API call is a worse outcome than a slightly less
sophisticated fallback.
"""
import json
import logging

import google.generativeai as genai

from app.core.config import settings

logger = logging.getLogger(__name__)

_model = None
if settings.gemini_api_key:
    try:
        genai.configure(api_key=settings.gemini_api_key)
        _model = genai.GenerativeModel("gemini-2.5-flash")
    except Exception:  # pragma: no cover - defensive against bad SDK/config state
        logger.exception("Failed to initialize Gemini model; will use fallback extraction.")
        _model = None

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

# Keyword -> normalized tag map used by the offline fallback extractor.
# Deliberately simple substring matching; good enough to demonstrate the
# feature end-to-end without a live API call.
_FALLBACK_KEYWORDS = {
    "backend": ["backend", "back-end", "server side", "api development", "django", "flask", "fastapi"],
    "frontend": ["frontend", "front-end", "html", "css", "ui development"],
    "mobile": ["mobile", "android", "ios", "flutter", "react native", "kotlin", "swift"],
    "machine-learning": ["machine learning", "ml", "deep learning", "neural network", "pytorch", "tensorflow"],
    "data-science": ["data science", "data analysis", "pandas", "numpy", "data analytics"],
    "devops": ["devops", "ci/cd", "jenkins", "terraform", "ansible"],
    "cloud": ["aws", "azure", "gcp", "cloud", "google cloud"],
    "ui-ux": ["ui/ux", "ui-ux", "figma", "design", "user experience", "ux"],
    "blockchain": ["blockchain", "solidity", "web3", "smart contract", "ethereum"],
    "cybersecurity": ["cybersecurity", "security", "penetration testing", "infosec"],
    "python": ["python"],
    "javascript": ["javascript", "js", "typescript"],
    "java": ["java "],
    "react": ["react"],
    "nodejs": ["node.js", "nodejs", "node "],
    "sql": ["sql", "postgres", "mysql", "database"],
}


def _fallback_extract(raw_text: str) -> list[str]:
    text_lower = f" {raw_text.lower()} "  # pad so word-boundary substrings like ' java ' always match
    found = []
    for tag, keywords in _FALLBACK_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            found.append(tag)
    return found


def extract_skills(raw_text: str) -> list[str]:
    if not raw_text or not raw_text.strip():
        return []

    if _model is None:
        return _fallback_extract(raw_text)

    try:
        prompt = SKILL_EXTRACTION_PROMPT.format(raw_text=raw_text)
        response = _model.generate_content(
            prompt,
            request_options={"timeout": 8},  # hard cap so a slow/unreachable API never hangs a request
        )
        text = (response.text or "").strip()

        if text.startswith("`"):
            text = text.strip("`")
            text = text.replace("json", "", 1).strip()

        skills = json.loads(text)
        if isinstance(skills, list):
            parsed = [str(s).strip().lower() for s in skills if s]
            if parsed:
                return parsed
        # Parsed to something unusable (empty list / non-list) -> fall back.
        return _fallback_extract(raw_text)
    except Exception:
        logger.warning("Gemini skill extraction failed; using fallback extractor.", exc_info=True)
        return _fallback_extract(raw_text)
TEAM_RATIONALE_PROMPT = """You are an assistant explaining hackathon team compositions to organizers.
Given the skill categories a team covers and the categories it's missing, write ONE concise sentence
(max 25 words) describing the team's strength and its main gap. Be specific and natural, not generic.

Categories covered: {covered}
Categories missing: {gaps}

Output ONLY the sentence, no preamble."""


def generate_team_rationale(covered: list[str], gaps: list[str]) -> str:
    try:
        prompt = TEAM_RATIONALE_PROMPT.format(
            covered=", ".join(covered) if covered else "none",
            gaps=", ".join(gaps) if gaps else "none",
        )
        response = _model.generate_content(prompt)
        text = response.text.strip()
        return text if text else "Team formed based on available skill complementarity."
    except Exception:
        return "Team formed based on available skill complementarity."
