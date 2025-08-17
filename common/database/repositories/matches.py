from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import List, Optional
from sqlalchemy import or_, and_
import logging

from common.database.database import db_session
from common.database.models.match import Match
from common.database.models.job_posting import JobPosting


class MatchesRepository:
    def __init__(self):
        self.session = db_session()

    def save_matches(self, matches_list: list[dict]):
        """
        Upsert matches - update if exists (by candidate_id + job_posting_id), insert if new
        """
        print(f'Upserting {len(matches_list)} matches')
        
        successful_upserts = 0
        failed_upserts = 0
        
        for match_data in matches_list:
            try:
                # Check if match already exists by candidate_id + job_posting_id
                existing_match = self.session.query(Match).filter(
                    Match.candidate_id == match_data['candidate_id'],
                    Match.job_posting_id == match_data['job_posting_id']
                ).first()
                
                if existing_match:
                    # Update existing match
                    print(f"Updating existing match for candidate {match_data['candidate_id']} and job {match_data['job_posting_id']}")
                    for key, value in match_data.items():
                        if hasattr(existing_match, key) and key != 'created_at':  # Don't update created_at
                            setattr(existing_match, key, value)
                else:
                    # Insert new match
                    print(f"Inserting new match for candidate {match_data['candidate_id']} and job {match_data['job_posting_id']}")
                    match_obj = Match(**match_data)
                    self.session.add(match_obj)
                
                # Commit each match individually to avoid transaction conflicts
                self.session.commit()
                successful_upserts += 1
                
            except Exception as e:
                print(f"Error processing match for candidate {match_data.get('candidate_id', 'Unknown')} and job {match_data.get('job_posting_id', 'Unknown')}: {e}")
                self.session.rollback()
                failed_upserts += 1
                continue

        print(f"Successfully upserted {successful_upserts} matches, {failed_upserts} failed")
        
        if failed_upserts > 0:
            raise Exception(f"Failed to upsert {failed_upserts} matches")
        
        self.session.close()
    
    def upsert_match(self, match_data: dict):
        """
        Upsert a single match
        """
        try:
            existing_match = self.session.query(Match).filter(
                Match.candidate_id == match_data['candidate_id'],
                Match.job_posting_id == match_data['job_posting_id']
            ).first()
            
            if existing_match:
                # Update existing match
                for key, value in match_data.items():
                    if hasattr(existing_match, key) and key != 'created_at':  # Don't update created_at
                        setattr(existing_match, key, value)
                print(f"Updated match for candidate {match_data['candidate_id']} and job {match_data['job_posting_id']}")
            else:
                # Insert new match
                match_obj = Match(**match_data)
                self.session.add(match_obj)
                print(f"Inserted new match for candidate {match_data['candidate_id']} and job {match_data['job_posting_id']}")
            
            self.session.commit()
            return existing_match or match_obj
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_matches_since(self, since_date: datetime) -> List[Match]:
        """Get matches created since a specific date"""
        return self.session.query(Match).filter(
            Match.created_at >= since_date
        ).all()
    
    def get_unnotified_matches_since(self, since_date: datetime) -> List[Match]:
        """Get matches created since a specific date that haven't been notified yet"""
        return self.session.query(Match).filter(
            Match.created_at >= since_date,
            Match.notified_at.is_(None)
        ).all()
    
    def get_matches_by_candidate(self, candidate_id: int) -> List[Match]:
        """Get all matches for a specific candidate"""
        return self.session.query(Match).filter(
            Match.candidate_id == candidate_id
        ).order_by(Match.created_at.desc()).all()
    
    def get_matches_by_candidate_with_filter(self, candidate_id: int, query: Optional[str] = None) -> List[Match]:
        """
        Get matches for a specific candidate with optional filtering
        
        Args:
            candidate_id: The candidate ID to filter by
            query: Optional search query to filter job postings by title, company, description, etc.
        
        Returns:
            List of matches that match the criteria
        """
        try:
            if not query or query.strip() == "":
                # No filter, return all matches for the candidate
                return self.session.query(Match).filter(
                    Match.candidate_id == candidate_id
                ).order_by(Match.created_at.desc()).all()
            
            # Clean and prepare the search query
            search_term = f"%{query.strip().lower()}%"
            
            # Use explicit join with ON clause to avoid ambiguity
            # Join Match with JobPosting on job_posting_id
            filtered_query = self.session.query(Match).join(
                JobPosting, Match.job_posting_id == JobPosting.id
            ).filter(
                Match.candidate_id == candidate_id,
                or_(
                    JobPosting.job_title.ilike(search_term),
                    JobPosting.company_name.ilike(search_term),
                    JobPosting.quick_description.ilike(search_term),
                    JobPosting.detailed_description.ilike(search_term),
                    JobPosting.requirements.ilike(search_term),
                    JobPosting.tech_stack.ilike(search_term),
                    JobPosting.industry.ilike(search_term),
                    JobPosting.company_type.ilike(search_term)
                )
            ).order_by(Match.created_at.desc())
            
            return filtered_query.all()
            
        except Exception as e:
            logging.error(f"Error filtering matches for candidate {candidate_id} with query '{query}': {e}")
            self.session.rollback()
            # Return empty list on error to prevent crashes
            return []
    
    def get_match_by_candidate_and_job(self, candidate_id: int, job_posting_id: int):
        """Get a specific match by candidate_id and job_posting_id"""
        try:
            return self.session.query(Match).filter(
                Match.candidate_id == candidate_id,
                Match.job_posting_id == job_posting_id
            ).first()
        except Exception as e:
            self.session.rollback()
            raise e
        # Don't close session here - let the caller manage it

    def exists_by_candidate_and_job(self, candidate_id: int, job_posting_id: int) -> bool:
        """Check if a match exists by candidate_id and job_posting_id"""
        try:
            return self.session.query(Match).filter(
                Match.candidate_id == candidate_id,
                Match.job_posting_id == job_posting_id
            ).first() is not None
        except Exception as e:
            self.session.rollback()
            raise e
        # Don't close session here - let the caller manage it

    def mark_matches_as_notified(self, match_ids: List[int]):
        """Mark specific matches as notified by setting notified_at timestamp"""
        try:
            self.session.query(Match).filter(
                Match.id.in_(match_ids)
            ).update({
                Match.notified_at: datetime.now()
            }, synchronize_session=False)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def close_session(self):
        """Close the session - call this when done with the repository"""
        if self.session:
            self.session.close()