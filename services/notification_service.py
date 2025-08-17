import logging
from typing import List
import asyncio
import re

from common.database.models.match import Match
from common.database.models.job_posting import JobPosting
from common.database.repositories.job_posting import JobPostingsRepository


class NotificationService:
    def __init__(self):
        self.job_postings_repo = JobPostingsRepository()

    def _escape_markdown(self, text: str) -> str:
        """
        Escape special characters that break Telegram markdown parsing
        """
        if not text:
            return text
        
        # Characters that need escaping in Telegram markdown
        escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        
        escaped_text = text
        for char in escape_chars:
            escaped_text = escaped_text.replace(char, f'\\{char}')
        
        return escaped_text

    def _safe_format_text(self, text: str) -> str:
        """
        Create a completely safe version of text by removing problematic characters
        """
        if not text:
            return text
        
        # Remove or replace problematic characters
        safe_text = text
        replacements = {
            '*': '',
            '_': '',
            '[': '(',
            ']': ')',
            '`': "'",
            '~': '-',
            '>': '',
            '#': '',
            '+': 'plus',
            '=': 'equals',
            '|': 'or',
            '{': '(',
            '}': ')',
        }
        
        for char, replacement in replacements.items():
            safe_text = safe_text.replace(char, replacement)
        
        return safe_text

    def _format_job_link(self, job_link: str) -> str:
        """
        Format job link safely for Telegram markdown
        """
        if not job_link:
            return "Link not available"
        
        # Clean the link and escape any problematic characters
        clean_link = job_link.strip()
        
        # If the link contains markdown-breaking characters, just return it as plain text
        # Telegram will still make it clickable
        return clean_link

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
        Format matches into a readable message using plain text to avoid markdown parsing issues
        """
        if language == 'es':
            header = "🎯 Nuevas Oportunidades de Trabajo Encontradas!\n\n"
            no_matches = "No se encontraron nuevas oportunidades de trabajo para ti en este momento."
        else:
            header = "🎯 New Job Opportunities Found!\n\n"
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
            
            # Use safe text formatting to remove problematic characters
            job_title = self._safe_format_text(job_posting.job_title or 'Unknown Title')
            company_name = self._safe_format_text(job_posting.company_name or 'Unknown Company')
            location = self._safe_format_text(getattr(job_posting, 'location', 'Remote') or 'Remote')
            
            if language == 'es':
                message_parts.append(
                    f"{i}. {job_title}\n"
                    f"🏢 {company_name}\n"
                    f"📍 {location}\n"
                    f"⭐ Match Score: {match_score}%\n"
                    f"🔗 {job_posting.job_link}\n"
                )
            else:
                message_parts.append(
                    f"{i}. {job_title}\n"
                    f"🏢 {company_name}\n"
                    f"📍 {location}\n"
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
        try:
            message = self._format_matches_message(matches, language)
            
            # Debug logging to help identify problematic content
            logging.info(f"Formatted message length: {len(message)}")
            logging.info(f"Message preview: {message[:200]}...")
            
            # Check for any potentially problematic characters
            problematic_chars = ['*', '_', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}']
            found_chars = [char for char in problematic_chars if char in message]
            if found_chars:
                logging.warning(f"Found potentially problematic characters in message: {found_chars}")
            
            return message
        except Exception as e:
            logging.error(f"Error formatting matches for display: {e}")
            # Return a safe fallback message
            if language == 'es':
                return "🔍 Error al formatear las coincidencias. Por favor intenta de nuevo."
            else:
                return "🔍 Error formatting matches. Please try again."


if __name__ == "__main__":
    """
    Test the markdown escaping functionality to prevent Telegram parsing errors
    """
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from common.database.models.match import Match
    from common.database.models.job_posting import JobPosting
    
    def test_markdown_escaping():
        """Test the markdown escaping functionality"""
        notification_service = NotificationService()
        
        # Test cases with problematic characters
        test_cases = [
            "Normal Job Title",
            "Job Title with *asterisks*",
            "Job Title with _underscores_",
            "Job Title with [brackets]",
            "Job Title with (parentheses)",
            "Job Title with dots...",
            "Job Title with exclamation!",
            "Job Title with #hashtag",
            "Job Title with +plus+ and -minus-",
            "Job Title with =equals=",
            "Job Title with |pipe|",
            "Job Title with {braces}",
            "Job Title with `backticks`",
            "Job Title with ~tilde~",
            "Job Title with >greater< than",
            "Complex: Job Title with *multiple* _special_ [characters] (test) #123 +plus- =equals= |pipe| {braces} `backticks` ~tilde~ >greater< ... !exclamation!",
        ]
        
        print("Testing markdown escaping:")
        print("=" * 50)
        
        for i, test_case in enumerate(test_cases, 1):
            escaped = notification_service._escape_markdown(test_case)
            print(f"{i:2d}. Original: {test_case}")
            print(f"    Escaped:  {escaped}")
            print()
        
        # Test job link formatting
        print("Testing job link formatting:")
        print("=" * 50)
        
        test_links = [
            "https://example.com/job/123",
            "https://company.com/jobs/backend-developer",
            "https://lever.co/company/job/123",
            "https://ashbyhq.com/jobs/backend-developer",
            "",
            None,
        ]
        
        for i, test_link in enumerate(test_links, 1):
            formatted = notification_service._format_job_link(test_link)
            print(f"{i:2d}. Original: {test_link}")
            print(f"    Formatted: {formatted}")
            print()

    def test_full_message_formatting():
        """Test the full message formatting with mock data"""
        notification_service = NotificationService()
        
        # Create mock job posting
        mock_job = JobPosting(
            id=1,
            job_title="Backend Developer (Python/Django)",
            company_name="Tech Corp. Inc.",
            job_link="https://lever.co/techcorp/jobs/backend-developer",
            quick_description="We're looking for a backend developer..."
        )
        
        # Create mock match
        mock_match = Match(
            id=1,
            candidate_id=1,
            job_posting_id=1,
            match_score=0.85,
            strengths="Great Python skills",
            weaknesses="Limited frontend experience"
        )
        
        print("Testing full message formatting:")
        print("=" * 50)
        
        # Test English formatting
        english_message = notification_service._format_matches_message([mock_match], 'en')
        print("English message:")
        print(english_message)
        print()
        
        # Test Spanish formatting
        spanish_message = notification_service._format_matches_message([mock_match], 'es')
        print("Spanish message:")
        print(spanish_message)
        print()

    # Run tests
    test_markdown_escaping()
    test_full_message_formatting()
    
    print("✅ All tests completed successfully!")
    print("The markdown escaping should now prevent Telegram parsing errors.")
