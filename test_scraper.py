#!/usr/bin/env python3
"""
Test scraper functionality with actual website
"""
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crypto_fundraising_monitor.scraper import CryptoFundraisingScraper
from crypto_fundraising_monitor.scoring import InvestorQualityScorer

def test_scraper():
    """Test the scraper with actual website"""
    print("🔍 Testing scraper with crypto-fundraising.info...")
    
    scraper = CryptoFundraisingScraper()
    
    try:
        # Scrape data
        scraped_data = scraper.scrape_fundraising_data()
        
        if not scraped_data:
            print("❌ Failed to scrape data")
            return
        
        print(f"✅ Successfully scraped {len(scraped_data.projects)} projects")
        
        # Show first few projects
        print("\n📋 Sample Projects:")
        for i, project in enumerate(scraped_data.projects[:5]):
            score = InvestorQualityScorer.calculate_project_score(project)
            should_highlight = InvestorQualityScorer.should_highlight(project)
            
            print(f"\n{i+1}. {project.name}")
            print(f"   Round: {project.round_type}")
            print(f"   Amount: {project.formatted_amount}")
            print(f"   Category: {project.project_category}")
            print(f"   Investors: {', '.join(project.investor_names)}")
            print(f"   Score: {score} {'(HIGHLIGHT)' if should_highlight else ''}")
        
        # Show score distribution
        score_dist = InvestorQualityScorer.get_score_distribution(scraped_data.projects)
        print(f"\n📊 Score Distribution:")
        print(f"   High (≥7): {score_dist['high']}")
        print(f"   Medium (3-6): {score_dist['medium']}")
        print(f"   Low (0-2): {score_dist['low']}")
        
        # Test message formatting
        print(f"\n💬 Testing message formatting for first project...")
        first_project = scraped_data.projects[0]
        summary = InvestorQualityScorer.get_project_summary(first_project)
        print("Formatted message:")
        print(summary)
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        scraper.close()

if __name__ == "__main__":
    test_scraper() 