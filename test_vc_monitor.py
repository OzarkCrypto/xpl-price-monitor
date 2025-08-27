#!/usr/bin/env python3
"""
VC Investment Monitor Bot 테스트 스크립트
봇의 주요 기능을 테스트합니다.
"""

import asyncio
import logging
from vc_scraper import VCFundraisingScraper
from vc_monitor_enhanced import EnhancedVCInvestmentMonitor

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_scraper():
    """스크래퍼 테스트"""
    print("🔍 스크래퍼 테스트 시작...")
    
    try:
        async with VCFundraisingScraper() as scraper:
            investments = await scraper.scrape_recent_fundraising()
            
            print(f"✅ 스크래핑 성공: {len(investments)}개 투자 정보 발견")
            
            if investments:
                print("\n📊 발견된 투자 정보:")
                for i, investment in enumerate(investments[:3], 1):
                    print(f"\n{i}. {investment['project_name']}")
                    print(f"   라운드: {investment['round_type']}")
                    print(f"   날짜: {investment['date']}")
                    print(f"   금액: {investment['amount']}")
                    print(f"   카테고리: {investment['categories']}")
                    print(f"   투자자: {investment['investors']}")
            else:
                print("⚠️ 투자 정보를 찾을 수 없습니다.")
                
    except Exception as e:
        print(f"❌ 스크래퍼 테스트 실패: {e}")

async def test_vc_detection():
    """VC 감지 기능 테스트"""
    print("\n🔍 VC 감지 기능 테스트...")
    
    monitor = EnhancedVCInvestmentMonitor()
    
    # 테스트 투자자 목록
    test_investors = [
        "Republic, YZi Labs (ex Binance Labs), HyperChain Capital",
        "LayerZero",
        "KuCoin Ventures",
        "a16z, Paradigm, Electric Capital",
        "Unknown investors"
    ]
    
    for investors in test_investors:
        has_top_vc, top_vcs, vc_score, tier_level = monitor.check_top_vc_involvement(investors)
        
        print(f"\n투자자: {investors}")
        print(f"Top VC 참여: {has_top_vc}")
        print(f"발견된 VC: {top_vcs}")
        print(f"VC 점수: {vc_score}/100")
        print(f"Tier 레벨: {tier_level}")

async def test_telegram():
    """텔레그램 메시지 전송 테스트"""
    print("\n📱 텔레그램 메시지 전송 테스트...")
    
    monitor = EnhancedVCInvestmentMonitor()
    
    # 테스트 메시지
    test_message = """
🧪 <b>VC 모니터링 봇 테스트</b>

이것은 테스트 메시지입니다.
봇이 정상적으로 작동하고 있습니다.

✅ 스크래퍼 테스트 완료
✅ VC 감지 기능 테스트 완료
✅ 텔레그램 연동 테스트 완료
    """
    
    try:
        await monitor.send_telegram_message(test_message.strip())
        print("✅ 텔레그램 메시지 전송 성공")
    except Exception as e:
        print(f"❌ 텔레그램 메시지 전송 실패: {e}")

async def test_database():
    """데이터베이스 기능 테스트"""
    print("\n🗄️ 데이터베이스 기능 테스트...")
    
    monitor = EnhancedVCInvestmentMonitor()
    
    # 테스트 투자 정보
    test_investment = {
        'project_name': 'Test Project',
        'round_type': 'Seed',
        'date': '2025-01-01',
        'amount': '$1,000,000',
        'categories': 'DeFi, Infrastructure',
        'investors': 'a16z, Paradigm',
        'source': 'test'
    }
    
    try:
        # 투자 정보 저장 테스트
        monitor.save_investment(test_investment, 80)
        print("✅ 투자 정보 저장 성공")
        
        # 중복 확인 테스트
        exists = monitor.is_investment_exists(test_investment)
        print(f"✅ 중복 확인 테스트: {exists}")
        
    except Exception as e:
        print(f"❌ 데이터베이스 테스트 실패: {e}")

async def main():
    """메인 테스트 함수"""
    print("🚀 VC 투자 모니터링 봇 테스트 시작\n")
    
    try:
        # 1. 스크래퍼 테스트
        await test_scraper()
        
        # 2. VC 감지 기능 테스트
        await test_vc_detection()
        
        # 3. 데이터베이스 기능 테스트
        await test_database()
        
        # 4. 텔레그램 메시지 전송 테스트
        await test_telegram()
        
        print("\n🎉 모든 테스트 완료!")
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(main())
