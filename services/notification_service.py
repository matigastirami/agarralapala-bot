import logging
from typing import List
import asyncio

from common.database.models.match import Match
from common.database.models.job_posting import JobPosting
from common.database.repositories.job_posting import JobPostingsRepository


class NotificationService:
    def __init__(self):
        self.job_postings_repo = JobPostingsRepository()

    def send_matches_notification(self, telegram_chat_id: int, matches: List[Match], language: str = 'en'):
        """
        Send matches notification to a candidate via Telegram
        """
        try:
            # Format the message
            message = self._format_matches_message(matches, language)
            
            # Return the formatted message - the calling code will handle sending
            logging.info(f"Formatted matches notification for {telegram_chat_id}")
            return message
            
        except Exception as e:
            logging.error(f"Failed to format matches notification for {telegram_chat_id}: {e}")
            raise

    def _format_matches_message(self, matches: List[Match], language: str) -> str:
        """
        Format matches into a readable message
        """
        if language == 'es':
            header = "🎯 *Nuevas Oportunidades de Trabajo Encontradas!*\n\n"
            no_matches = "No se encontraron nuevas oportunidades de trabajo para ti en este momento."
        else:
            header = "🎯 *New Job Opportunities Found!*\n\n"
            no_matches = "No new job opportunities found for you at this time."

        if not matches:
            return header + no_matches

        message_parts = [header]
        
        for i, match in enumerate(matches[:5], 1):  # Limit to 5 matches
            # Get job posting details
            job_posting = self.job_postings_repo.get_by_id(match.job_posting_id)
            if not job_posting:
                continue
                
            match_score = int(match.match_score * 100)
            
            if language == 'es':
                message_parts.append(
                    f"*{i}. {job_posting.job_title}*\n"
                    f"🏢 {job_posting.company_name}\n"
                    f"📍 {getattr(job_posting, 'location', 'Remote') or 'Remote'}\n"
                    f"⭐ Match Score: {match_score}%\n"
                    f"🔗 {job_posting.job_link}\n"
                )
            else:
                message_parts.append(
                    f"*{i}. {job_posting.job_title}*\n"
                    f"🏢 {job_posting.company_name}\n"
                    f"📍 {getattr(job_posting, 'location', 'Remote') or 'Remote'}\n"
                    f"⭐ Match Score: {match_score}%\n"
                    f"🔗 {job_posting.job_link}\n"
                )
        
        if len(matches) > 5:
            if language == 'es':
                message_parts.append(f"\n... y {len(matches) - 5} oportunidades más!")
            else:
                message_parts.append(f"\n... and {len(matches) - 5} more opportunities!")
        
        return "\n".join(message_parts)

    def format_matches_for_display(self, matches: List[Match], language: str) -> str:
        """
        Format matches for display (used by the /matches command)
        """
        return self._format_matches_message(matches, language)
