from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import List

from common.database.database import db_session
from common.database.models.match import Match


class MatchesRepository:
    def __init__(self):
        self.session = db_session()

    def save_matches(self, matches_list: list[dict]):
        print('called with', matches_list)
        for match in matches_list:
            match_obj = Match(**match)
            self.session.add(match_obj)

        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
        finally:
            self.session.close()
    
    def get_matches_since(self, since_date: datetime) -> List[Match]:
        """Get matches created since a specific date"""
        return self.session.query(Match).filter(
            Match.created_at >= since_date
        ).all()
