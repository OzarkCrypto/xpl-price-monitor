"""
Telegram notification module for Crypto Fundraising Monitor
"""
import re
import logging
from typing import List
import requests
from .models import FundraisingProject, TelegramMessage
from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, MAX_MESSAGE_LENGTH, SAFE_SPLIT_LENGTH, HEADER_MESSAGE

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Send notifications via Telegram Bot API"""
    
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def escape_markdown_v2(self, text: str) -> str:
        """
        Escape special characters for Telegram MarkdownV2 format
        
        Characters to escape: _ * [ ] ( ) ~ ` > # + - = | { } . !
        """
        if not text:
            return text
            
        # First, escape backslashes
        text = text.replace('\\', '\\\\')
        
        # Then escape all special characters
        escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        
        return text
    
    def format_project_message(self, projects: List[FundraisingProject], new_count: int) -> List[str]:
        """
        Format projects into Telegram messages with proper splitting
        
        Args:
            projects: List of projects to format
            new_count: Number of new projects
            
        Returns:
            List of message strings (split if needed)
        """
        messages = []
        
        # Header message - escape it properly
        header = f"{self.escape_markdown_v2(HEADER_MESSAGE)}\n오늘 신규 {new_count}건\n\n"
        current_message = header
        
        for i, project in enumerate(projects):
            # Format project summary
            project_summary = self._format_single_project(project)
            
            # Add separator between projects (except for the first one)
            if i > 0:
                project_summary = f"\\-\\-\\-\\-\\-\\-\\-\\-\n{project_summary}"
            
            # Check if adding this project would exceed safe length
            if len(current_message + project_summary) > SAFE_SPLIT_LENGTH:
                # Current message is ready, start a new one
                messages.append(current_message)
                current_message = project_summary
            else:
                current_message += project_summary
        
        # Add the last message if it has content
        if current_message.strip() != header.strip():
            messages.append(current_message)
        
        return messages
    
    def _format_single_project(self, project: FundraisingProject) -> str:
        """Format a single project for Telegram message"""
        # Get project summary from scoring module
        from .scoring import InvestorQualityScorer
        
        summary = InvestorQualityScorer.get_project_summary(project)
        
        # Escape for MarkdownV2
        escaped_summary = self.escape_markdown_v2(summary)
        
        # Handle bold formatting (already escaped **)
        # Replace ** with * for MarkdownV2
        escaped_summary = escaped_summary.replace('\\*\\*', '*')
        
        return escaped_summary
    
    def send_message(self, text: str) -> bool:
        """Send a single message to Telegram"""
        try:
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'MarkdownV2',
                'disable_web_page_preview': True
            }
            
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    logger.info("Message sent successfully")
                    return True
                else:
                    logger.error(f"Telegram API error: {result}")
                    return False
            else:
                logger.error(f"HTTP error {response.status_code}: {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Failed to send message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            return False
    
    def send_project_notifications(self, projects: List[FundraisingProject]) -> bool:
        """
        Send notifications for new projects
        
        Args:
            projects: List of new projects to notify about
            
        Returns:
            True if all messages were sent successfully
        """
        if not projects:
            logger.info("No new projects to notify about")
            return True
        
        logger.info(f"Sending notifications for {len(projects)} new projects")
        
        # Format messages
        message_texts = self.format_project_message(projects, len(projects))
        
        # Send each message
        success_count = 0
        for i, message_text in enumerate(message_texts):
            logger.debug(f"Sending message {i+1}/{len(message_texts)} (length: {len(message_text)})")
            
            if self.send_message(message_text):
                success_count += 1
            else:
                logger.error(f"Failed to send message {i+1}")
        
        logger.info(f"Successfully sent {success_count}/{len(message_texts)} messages")
        return success_count == len(message_texts)
    
    def test_connection(self) -> bool:
        """Test Telegram bot connection"""
        try:
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    bot_info = result.get('result', {})
                    logger.info(f"Bot connected: @{bot_info.get('username', 'Unknown')}")
                    return True
                else:
                    logger.error(f"Telegram API error: {result}")
                    return False
            else:
                logger.error(f"HTTP error {response.status_code}: {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Connection test failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in connection test: {e}")
            return False 