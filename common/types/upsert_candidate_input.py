from typing import Optional

from pydantic import BaseModel, Field


class UpsertCandidateInput(BaseModel):
    role: Optional[str] = Field(description='The candidate role', default=None)
    tech_stack: Optional[str] = Field(description='The tech stack, normally a list of strings comma separated', default=None)
    location: Optional[str] = Field(description='The candidate geo location', default=None)
    telegram_chat_id: Optional[int] = Field(description='The chat ID telegram provides', default=None)
    language: str = Field(description="Candidate language", default="en")