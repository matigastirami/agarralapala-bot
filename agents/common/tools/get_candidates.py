from langchain_core.tools import tool

from common.database.repositories.candidates import CandidatesRepository


@tool('get_candidates')
def get_candidates():
    """
    Return a list of candidates of the DB that includes:
        * Tech stack as a comma separated string of techs
        * location that can be a country or a region, but in the first case it must prioritize regions, for example,
        if country is anything in latin america, it should opt for matching the whole latam region instead of just the country
        * role that can be anything like backend engineer, frontend, data, manager, VP, etc
    """
    candidates_repo = CandidatesRepository()
    candidates = candidates_repo.get_candidates()
    return [
        {
            "id": r.id,
            "telegram_chat_id": r.telegram_chat_id,
            "tech_stack": r.tech_stack,
            "location": r.location,
            "role": r.role,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            "deleted_at": r.deleted_at.isoformat() if r.deleted_at else None,
        }
        for r in candidates
    ]