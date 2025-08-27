#!/usr/bin/env python3
"""
Test the entire Crypto Fundraising Monitor system
"""
import sys
import os
import logging

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crypto_fundraising_monitor.config import validate_config, HIGHLIGHT_THRESHOLD
from crypto_fundraising_monitor.scraper import CryptoFundraisingScraper
from crypto_fundraising_monitor.storage import ProjectStorage
from crypto_fundraising_monitor.scoring import InvestorQualityScorer
from crypto_fundraising_monitor.notify import TelegramNotifier

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_config():
    """Test configuration validation"""
    print("🔧 Testing Configuration...")
    
    try:
        validate_config()
        print("✅ Configuration validation passed")
        print(f"   Highlight threshold: {HIGHLIGHT_THRESHOLD}")
        return True
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

def test_scraper():
    """Test the scraper"""
    print("\n🔍 Testing Scraper...")
    
    scraper = CryptoFundraisingScraper()
    
    try:
        scraped_data = scraper.scrape_fundraising_data()
        
        if not scraped_data:
            print("❌ Scraper failed")
            return None
        
        print(f"✅ Scraper successful: {len(scraped_data.projects)} projects")
        
        # Show sample projects with scores
        print("\n📋 Sample Projects with Scores:")
        for i, project in enumerate(scraped_data.projects[:3]):
            score = InvestorQualityScorer.calculate_project_score(project)
            should_highlight = InvestorQualityScorer.should_highlight(project)
            
            print(f"\n{i+1}. {project.name}")
            print(f"   Round: {project.round_type}")
            print(f"   Amount: {project.formatted_amount}")
            print(f"   Category: {project.project_category}")
            print(f"   Investors: {', '.join(project.investor_names)}")
            print(f"   Score: {score} {'(HIGHLIGHT)' if should_highlight else ''}")
        
        return scraped_data
        
    except Exception as e:
        print(f"❌ Scraper error: {e}")
        return None
    finally:
        scraper.close()

def test_storage():
    """Test the storage system"""
    print("\n💾 Testing Storage...")
    
    try:
        storage = ProjectStorage()
        
        # Test stats
        stats = storage.get_stats()
        print(f"✅ Storage initialized: {stats}")
        
        # Test cleanup
        storage.cleanup_old_records()
        print("✅ Storage cleanup completed")
        
        return storage
        
    except Exception as e:
        print(f"❌ Storage error: {e}")
        return None

def test_scoring():
    """Test the scoring system"""
    print("\n📊 Testing Scoring System...")
    
    try:
        # Test with sample data
        from crypto_fundraising_monitor.models import FundraisingProject, Investor
        
        test_project = FundraisingProject(
            name="Test Project",
            round_type="Series A",
            date="Aug 2025",
            amount_usd=10000000,
            project_category="Infrastructure",
            investors=[
                Investor(name="Sequoia", is_lead=True),
                Investor(name="Electric", is_lead=False)
            ]
        )
        
        score = InvestorQualityScorer.calculate_project_score(test_project)
        should_highlight = InvestorQualityScorer.should_highlight(test_project)
        
        print(f"✅ Scoring test: Score={score}, Highlight={should_highlight}")
        
        # Test message formatting
        summary = InvestorQualityScorer.get_project_summary(test_project)
        print(f"✅ Message formatting: {len(summary)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Scoring error: {e}")
        return False

def test_notification_formatting():
    """Test notification formatting without sending"""
    print("\n💬 Testing Notification Formatting...")
    
    try:
        from crypto_fundraising_monitor.models import FundraisingProject, Investor
        
        # Create test projects
        test_projects = [
            FundraisingProject(
                name="High Score Project",
                round_type="Series A",
                date="Aug 2025",
                amount_usd=15000000,
                project_category="Infrastructure",
                investors=[
                    Investor(name="Sequoia", is_lead=True),
                    Investor(name="a16z", is_lead=False)
                ]
            ),
            FundraisingProject(
                name="Low Score Project",
                round_type="Pre-seed",
                date="Aug 2025",
                amount_usd=1000000,
                project_category="Gaming",
                investors=[
                    Investor(name="Unknown VC", is_lead=True)
                ]
            )
        ]
        
        # Test message formatting
        notifier = TelegramNotifier()
        messages = notifier.format_project_message(test_projects, len(test_projects))
        
        print(f"✅ Generated {len(messages)} message(s)")
        for i, msg in enumerate(messages):
            print(f"   Message {i+1}: {len(msg)} characters")
            if len(msg) > 100:
                print(f"      Preview: {msg[:100]}...")
            else:
                print(f"      Content: {msg}")
        
        return True
        
    except Exception as e:
        print(f"❌ Notification formatting error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Crypto Fundraising Monitor System Tests\n")
    
    results = []
    
    # Test configuration
    results.append(("Configuration", test_config()))
    
    # Test scraper
    scraped_data = test_scraper()
    results.append(("Scraper", scraped_data is not None))
    
    # Test storage
    storage = test_storage()
    results.append(("Storage", storage is not None))
    
    # Test scoring
    results.append(("Scoring", test_scoring()))
    
    # Test notification formatting
    results.append(("Notification Formatting", test_notification_formatting()))
    
    # Summary
    print("\n📊 Test Results Summary:")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The system is ready to use.")
        print("\n다음 단계:")
        print("1. .env 파일에 TELEGRAM_BOT_TOKEN 설정")
        print("2. python crypto_fundraising_monitor/run.py 실행")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 