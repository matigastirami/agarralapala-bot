from sqlalchemy import Column, Integer, String, DateTime, Nullable, func

from common.database.models import Base

class Candidate(Base):
    __tablename__ = 'candidates'

    id = Column(Integer, primary_key=True, index=True)
    telegram_chat_id = Column(Integer, unique=True, nullable=True)
    tech_stack = Column(String(length=255), nullable=True)
    location = Column(String(length=64), nullable=True)
    role = Column(String(length=64), nullable=True)
    language = Column(String(length=2), nullable=False, default='en')

    created_at = Column(DateTime, nullable=False, server_default=func.now()) # Add default value here
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)