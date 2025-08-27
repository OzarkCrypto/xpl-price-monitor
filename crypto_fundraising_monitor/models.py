"""
Data models for Crypto Fundraising Monitor
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import hashlib


class Investor(BaseModel):
    """Investor information"""
    name: str
    is_lead: bool = False


class FundraisingProject(BaseModel):
    """Fundraising project data"""
    name: str
    round_type: str
    date: str
    amount_usd: int
    project_category: str
    investors: List[Investor]
    url: Optional[str] = None
    
    @property
    def unique_id(self) -> str:
        """Generate unique ID for deduplication"""
        # Use name + date + amount as unique identifier
        identifier = f"{self.name}_{self.date}_{self.amount_usd}"
        return hashlib.md5(identifier.encode()).hexdigest()
    
    @property
    def formatted_amount(self) -> str:
        """Format amount with commas"""
        return f"${self.amount_usd:,}"
    
    @property
    def investor_names(self) -> List[str]:
        """Get list of investor names"""
        return [investor.name for investor in self.investors]
    
    @property
    def lead_investors(self) -> List[str]:
        """Get list of lead investor names"""
        return [investor.name for investor in self.investors if investor.is_lead]


class ScrapedData(BaseModel):
    """Raw scraped data from website"""
    projects: List[FundraisingProject]
    scraped_at: datetime = Field(default_factory=datetime.now)
    
    @property
    def new_projects_count(self) -> int:
        """Count of new projects"""
        return len(self.projects)


class TelegramMessage(BaseModel):
    """Telegram message structure"""
    text: str
    parse_mode: str = "MarkdownV2"
    disable_web_page_preview: bool = True
    
    @property
    def length(self) -> int:
        """Message length"""
        return len(self.text)
    
    def needs_split(self, max_length: int = 4096) -> bool:
        """Check if message needs to be split"""
        return self.length > max_length 