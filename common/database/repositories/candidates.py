from common.database.database import db_session
from common.database.models.candidate import Candidate
from common.types.upsert_candidate_input import UpsertCandidateInput


class CandidatesRepository:
    def __init__(self):
        self.session = db_session()

    def get_candidates(self):
        return self.session.query(Candidate).all()

    def update(self, id: int, data: UpsertCandidateInput):
        candidate = self.session.query(Candidate).filter_by(telegram_chat_id=id).first()
        if candidate:
            candidate.role = data.role if data.role else candidate.role
            candidate.location = data.location if data.location else candidate.location
            candidate.tech_stack = data.tech_stack if data.tech_stack else candidate.tech_stack
            candidate.language = data.language if data.language else candidate.language
        self.session.commit()

    def create(self, data: UpsertCandidateInput):
        new_candidate = Candidate()
        new_candidate.location = data.location or None
        new_candidate.tech_stack = data.tech_stack or None
        new_candidate.role = data.role or None
        new_candidate.telegram_chat_id = data.telegram_chat_id or None
        new_candidate.language = data.language or 'en'
        self.session.add(new_candidate)
        self.session.commit()

    def get_by_id(self, id: int):
        return self.session.query(Candidate).filter_by(telegram_chat_id=id).first()
    
    def get_candidate_by_id(self, candidate_id: int):
        """Get candidate by internal ID (not telegram_chat_id)"""
        return self.session.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    def get_candidates_with_telegram(self):
        """Get all candidates that have a telegram_chat_id"""
        return self.session.query(Candidate).filter(
            Candidate.telegram_chat_id.isnot(None)
        ).all()