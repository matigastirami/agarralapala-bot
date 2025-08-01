from common.database.database import db_session
from common.database.models.candidate import Candidate


class CandidatesRepository:
    def __init__(self):
        self.session = db_session()

    def get_candidates(self):
        return self.session.query(Candidate).all()