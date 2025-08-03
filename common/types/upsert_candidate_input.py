from typing import Optional

from pydantic import BaseModel, Field


class UpsertCandidateInput(BaseModel):
    role: Optional[str] = Field(description='The candidate role')
    tech_stack: Optional[str] = Field(description='The tech stack, normally a list of strings comma separated')
    location: Optional[str] = Field(description='The candidate geo location')
    telegram_chat_id: Optional[str] = Field(description='The chat ID telegram provides')