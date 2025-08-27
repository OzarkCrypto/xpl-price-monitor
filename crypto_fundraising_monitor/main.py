"""
Main module for Crypto Fundraising Monitor
"""
import logging
import sys
from datetime import datetime
from .config import validate_config
from .scraper import CryptoFundraisingScraper
from .storage import ProjectStorage
from .notify import TelegramNotifier
from .scoring import InvestorQualityScorer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crypto_fundraising_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class CryptoFundraisingMonitor:
    """Main monitoring class"""
    
    def __init__(self):
        self.scraper = None
        self.storage = None
        self.notifier = None
        
    def initialize(self):
        """Initialize all components"""
        try:
            # Validate configuration
            validate_config()
            logger.info("Configuration validated successfully")
            
            # Initialize components
            self.scraper = CryptoFundraisingScraper()
            self.storage = ProjectStorage()
            self.notifier = TelegramNotifier()
            
            # Test Telegram connection
            if not self.notifier.test_connection():
                logger.error("Failed to connect to Telegram")
                return False
            
            logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    def run_monitoring_cycle(self):
        """Run one complete monitoring cycle"""
        try:
            logger.info("Starting monitoring cycle")
            
            # Scrape data
            scraped_data = self.scraper.scrape_fundraising_data()
            if not scraped_data:
                logger.error("Failed to scrape data")
                return False
            
            logger.info(f"Scraped {len(scraped_data.projects)} total projects")
            
            # Get new projects (filter out already sent ones)
            new_projects = self.storage.get_new_projects(scraped_data.projects)
            
            if not new_projects:
                logger.info("No new projects found")
                return True
            
            logger.info(f"Found {len(new_projects)} new projects")
            
            # Sort projects by investor quality score
            sorted_projects = InvestorQualityScorer.get_projects_by_score(new_projects)
            
            # Get score distribution for logging
            score_dist = InvestorQualityScorer.get_score_distribution(sorted_projects)
            logger.info(f"Score distribution: High={score_dist['high']}, Medium={score_dist['medium']}, Low={score_dist['low']}")
            
            # Log projects that will be highlighted
            highlighted_projects = [p for p in sorted_projects if InvestorQualityScorer.should_highlight(p)]
            if highlighted_projects:
                logger.info(f"Projects to highlight: {[p.name for p in highlighted_projects]}")
            
            # Send notifications
            if self.notifier.send_project_notifications(sorted_projects):
                # Mark projects as sent
                for project in sorted_projects:
                    self.storage.mark_project_sent(project)
                
                logger.info(f"Successfully notified about {len(sorted_projects)} new projects")
                return True
            else:
                logger.error("Failed to send notifications")
                return False
                
        except Exception as e:
            logger.error(f"Monitoring cycle failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.scraper:
                self.scraper.close()
            
            if self.storage:
                self.storage.cleanup_old_records()
                self.storage.close()
                
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def run(self):
        """Main run method"""
        try:
            if not self.initialize():
                return False
            
            success = self.run_monitoring_cycle()
            
            return success
            
        finally:
            self.cleanup()


def main():
    """Main entry point"""
    logger.info("Starting Crypto Fundraising Monitor")
    
    monitor = CryptoFundraisingMonitor()
    success = monitor.run()
    
    if success:
        logger.info("Monitoring cycle completed successfully")
        sys.exit(0)
    else:
        logger.error("Monitoring cycle failed")
        sys.exit(1)


if __name__ == "__main__":
    main() 