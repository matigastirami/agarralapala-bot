import logging
from datetime import datetime, timedelta
from typing import List

from crons.cron_manager import CronJob
from common.database.repositories.candidates import CandidatesRepository
from common.database.repositories.matches import MatchesRepository
from services.notification_service import NotificationService
from common.config.config import CRON_MATCH_NOTIFICATION_INTERVAL_HOURS, CRON_MATCH_NOTIFICATION_START_TIME


class MatchNotificationCron(CronJob):
    @property
    def name(self) -> str:
        return "match_notification"

    @property
    def interval_hours(self) -> int:
        return CRON_MATCH_NOTIFICATION_INTERVAL_HOURS
    
    @property
    def start_time(self) -> str:
        return CRON_MATCH_NOTIFICATION_START_TIME

    def run(self):
        logging.info("[MatchNotificationCron] Starting daily match notifications")
        
        try:
            # Get candidates with telegram chat IDs
            candidates_repo = CandidatesRepository()
            candidates = candidates_repo.get_candidates_with_telegram()
            
            if not candidates:
                logging.info("[MatchNotificationCron] No candidates with telegram chat IDs found")
                return
            
            # Get matches from the last 24 hours
            matches_repo = MatchesRepository()
            since_date = datetime.now() - timedelta(hours=24)
            recent_matches = matches_repo.get_matches_since(since_date)
            
            if not recent_matches:
                logging.info("[MatchNotificationCron] No recent matches found")
                return
            
            # Group matches by candidate
            matches_by_candidate = {}
            for match in recent_matches:
                candidate_id = match.candidate_id
                if candidate_id not in matches_by_candidate:
                    matches_by_candidate[candidate_id] = []
                matches_by_candidate[candidate_id].append(match)
            
            # Send notifications to each candidate
            notification_service = NotificationService()
            sent_count = 0
            
            # Import here to avoid circular imports
            from bot.telegram_bot import TelegramBot
            telegram_bot = TelegramBot()
            
            for candidate in candidates:
                candidate_matches = matches_by_candidate.get(candidate.id, [])
                if candidate_matches:
                    try:
                        # Format the message
                        message = notification_service.send_matches_notification(
                            telegram_chat_id=candidate.telegram_chat_id,
                            matches=candidate_matches,
                            language=candidate.language
                        )
                        
                        # Send via Telegram
                        import asyncio
                        asyncio.run(telegram_bot.send_message(
                            chat_id=candidate.telegram_chat_id,
                            message=message
                        ))
                        
                        sent_count += 1
                        logging.info(f"[MatchNotificationCron] Sent notification to candidate {candidate.id}")
                    except Exception as e:
                        logging.error(f"[MatchNotificationCron] Failed to send notification to candidate {candidate.id}: {e}")
            
            logging.info(f"[MatchNotificationCron] Completed. Sent {sent_count} notifications")
            
        except Exception as e:
            logging.error(f"[MatchNotificationCron] Error during execution: {e}")
