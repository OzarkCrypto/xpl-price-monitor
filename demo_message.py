#!/usr/bin/env python3
"""
Demo script to show the formatted message without sending to Telegram
"""
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crypto_fundraising_monitor.scraper import CryptoFundraisingScraper
from crypto_fundraising_monitor.scoring import InvestorQualityScorer
from crypto_fundraising_monitor.notify import TelegramNotifier

def demo_message():
    """Show the formatted message that would be sent to Telegram"""
    print("🚀 Crypto Fundraising Monitor - Demo Message")
    print("=" * 60)
    
    scraper = CryptoFundraisingScraper()
    
    try:
        # Scrape data
        print("🔍 스크래핑 중...")
        scraped_data = scraper.scrape_fundraising_data()
        
        if not scraped_data:
            print("❌ 스크래핑 실패")
            return
        
        print(f"✅ {len(scraped_data.projects)}개 프로젝트 발견\n")
        
        # Get new projects (filter out already sent ones)
        from crypto_fundraising_monitor.storage import ProjectStorage
        storage = ProjectStorage()
        new_projects = storage.get_new_projects(scraped_data.projects)
        
        if not new_projects:
            print("📝 새로운 프로젝트가 없습니다.")
            return
        
        print(f"📝 새로운 프로젝트: {len(new_projects)}개\n")
        
        # Sort projects by investor quality score
        sorted_projects = InvestorQualityScorer.get_projects_by_score(new_projects)
        
        # Get score distribution
        score_dist = InvestorQualityScorer.get_score_distribution(sorted_projects)
        print(f"📊 점수 분포: High={score_dist['high']}, Medium={score_dist['medium']}, Low={score_dist['low']}\n")
        
        # Show projects that will be highlighted
        highlighted_projects = [p for p in sorted_projects if InvestorQualityScorer.should_highlight(p)]
        if highlighted_projects:
            print(f"✨ 하이라이트될 프로젝트 ({len(highlighted_projects)}개):")
            for project in highlighted_projects:
                score = InvestorQualityScorer.calculate_project_score(project)
                print(f"   • {project.name} (Score: {score})")
            print()
        
        # Generate and show the message that would be sent
        print("📱 텔레그램으로 전송될 메시지:")
        print("=" * 60)
        
        notifier = TelegramNotifier()
        messages = notifier.format_project_message(sorted_projects, len(sorted_projects))
        
        for i, message in enumerate(messages, 1):
            if len(messages) > 1:
                print(f"\n--- 메시지 {i}/{len(messages)} ---")
            print(message)
            print(f"\n[메시지 길이: {len(message)} 문자]")
        
        print("=" * 60)
        
        # Show what would happen if we had a real bot token
        print("\n🤖 실제 텔레그램 전송을 위해서는:")
        print("1. BotFather에서 봇 생성")
        print("2. .env 파일에 TELEGRAM_BOT_TOKEN 설정")
        print("3. python3 crypto_fundraising_monitor/run.py 실행")
        
        # Mark projects as sent for demo purposes
        print(f"\n💾 데모용으로 {len(sorted_projects)}개 프로젝트를 '전송됨'으로 표시")
        for project in sorted_projects:
            storage.mark_project_sent(project)
        
        print("✅ 데모 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        scraper.close()

if __name__ == "__main__":
    demo_message() 