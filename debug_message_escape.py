#!/usr/bin/env python3
"""
Debug message escaping issues
"""
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crypto_fundraising_monitor.scraper import CryptoFundraisingScraper
from crypto_fundraising_monitor.scoring import InvestorQualityScorer
from crypto_fundraising_monitor.notify import TelegramNotifier

def debug_message_escape():
    """Debug message escaping issues"""
    print("🔍 메시지 이스케이프 디버깅")
    print("=" * 50)
    
    scraper = CryptoFundraisingScraper()
    
    try:
        # Scrape data
        scraped_data = scraper.scrape_fundraising_data()
        
        if not scraped_data:
            print("❌ 스크래핑 실패")
            return
        
        # Get first few projects
        projects = scraped_data.projects[:3]
        
        print(f"📋 테스트할 프로젝트: {len(projects)}개\n")
        
        notifier = TelegramNotifier()
        
        for i, project in enumerate(projects):
            print(f"--- 프로젝트 {i+1}: {project.name} ---")
            
            # Test escaping
            original_name = project.name
            escaped_name = notifier.escape_markdown_v2(original_name)
            
            print(f"원본 이름: {original_name}")
            print(f"이스케이프된 이름: {escaped_name}")
            
            # Check for problematic characters
            problematic_chars = ['(', ')', '[', ']', '_', '*', '`', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
            found_problematic = []
            
            for char in problematic_chars:
                if char in original_name:
                    found_problematic.append(char)
            
            if found_problematic:
                print(f"⚠️  문제가 될 수 있는 문자: {found_problematic}")
            else:
                print("✅ 특수문자 없음")
            
            print()
        
        # Test full message formatting
        print("📱 전체 메시지 포맷 테스트:")
        print("=" * 50)
        
        messages = notifier.format_project_message(projects, len(projects))
        
        for i, message in enumerate(messages):
            print(f"\n--- 메시지 {i+1} ---")
            print(f"길이: {len(message)} 문자")
            
            # Show first 200 characters
            preview = message[:200] + "..." if len(message) > 200 else message
            print(f"미리보기: {preview}")
            
            # Check for unescaped special characters
            for char in ['(', ')', '[', ']', '_', '*', '`', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']:
                if char in message and f'\\{char}' not in message:
                    print(f"⚠️  이스케이프되지 않은 문자 '{char}' 발견")
        
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        scraper.close()

if __name__ == "__main__":
    debug_message_escape() 