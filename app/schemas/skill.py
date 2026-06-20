from pydantic import BaseModel


class SkillExtractRequest(BaseModel):
    raw_text: str
