from common.database.repositories.candidates import CandidatesRepository
from common.types.upsert_candidate_input import UpsertCandidateInput


class CandidatesService:
    def __init__(self):
        self.candidates_repo = CandidatesRepository()

    def get_candidates(self):
        return self.candidates_repo.get_candidates()

    def upsert(self, id: int, data: UpsertCandidateInput):
        candidate = self.candidates_repo.get_by_id(id)
        if candidate:
            self.candidates_repo.update(id, data)
        else:
            data.telegram_chat_id = id
            self.candidates_repo.create(data)

    def get_by_id(self, id: int):
        return self.candidates_repo.get_by_id(id)