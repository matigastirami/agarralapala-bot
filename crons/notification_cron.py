from crons.cron_manager import CronJob
from common.database.repositories.matches import MatchesRepository
from common.database.repositories.candidates import CandidatesRepository
from common.database.repositories.job_posting import JobPostingsRepository
from bot.telegram_bot import TelegramBot
import logging
from datetime import datetime, timedelta
import asyncio

class NotificationCron(CronJob):
    def __init__(self):
        self.matches_repo = MatchesRepository()
        self.candidates_repo = CandidatesRepository()
        self.job_postings_repo = JobPostingsRepository()
        self.telegram_bot = TelegramBot()

    @property
    def name(self) -> str:
        return "notification_cron"

    @property
    def interval_hours(self) -> int:
        return 6  # Run every 6 hours

    def run(self):
        logging.info("Starting notification process")
        try:
            # Get matches from the last 24 hours
            yesterday = datetime.now() - timedelta(days=1)
            recent_matches = self.matches_repo.get_matches_since(yesterday)
            
            # Group matches by candidate
            candidate_matches = {}
            for match in recent_matches:
                candidate_id = match.candidate_id
                if candidate_id not in candidate_matches:
                    candidate_matches[candidate_id] = []
                candidate_matches[candidate_id].append(match)
            
            # Send notifications to each candidate
            for candidate_id, matches in candidate_matches.items():
                self._send_candidate_notification(candidate_id, matches)
                
            logging.info(f"Sent notifications to {len(candidate_matches)} candidates")
            
        except Exception as e:
            logging.error(f"Notification process failed: {str(e)}")

    def _send_candidate_notification(self, candidate_id: int, matches: list):
        """Send notification to a specific candidate about their matches"""
        try:
            # Get candidate info
            candidate = self.candidates_repo.get_candidate_by_id(candidate_id)
            if not candidate:
                logging.warning(f"Candidate {candidate_id} not found")
                return
            
            # Format notification message
            message = self._format_match_notification(matches)
            
            # Send via Telegram using asyncio
            asyncio.run(self.telegram_bot.send_message(
                chat_id=candidate.telegram_chat_id,
                message=message
            ))
            
        except Exception as e:
            logging.error(f"Error sending notification to candidate {candidate_id}: {str(e)}")

    def _format_match_notification(self, matches: list) -> str:
        """Format the notification message for matches"""
        if len(matches) == 1:
            match = matches[0]
            # Get job posting details
            job_posting = self.job_postings_repo.get_job_postings_by_ids([match.job_posting_id])[0]
            
            return f"""
🎯 You have a new job match!

**{job_posting.job_title}** at {job_posting.company_name}
Match Score: {match.match_score:.1f}%

{match.strengths if match.strengths else ''}

Apply here: {job_posting.job_link}
            """.strip()
        else:
            message = f"🎯 You have {len(matches)} new job matches!\n\n"
            for i, match in enumerate(matches[:5], 1):  # Limit to top 5
                # Get job posting details
                job_posting = self.job_postings_repo.get_job_postings_by_ids([match.job_posting_id])[0]
                message += f"{i}. **{job_posting.job_title}** at {job_posting.company_name} ({match.match_score:.1f}%)\n"
            
            if len(matches) > 5:
                message += f"\n... and {len(matches) - 5} more matches!"
            
            return message
