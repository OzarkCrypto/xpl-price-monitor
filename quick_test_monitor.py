#!/usr/bin/env python3
"""
폴리마켓 모니터 빠른 테스트 스크립트
"""

import os
import time
from polymarket_monitor import PolymarketMonitor

def quick_test():
    """빠른 테스트 실행"""
    # 환경 변수 설정
    os.environ['TELEGRAM_BOT_TOKEN'] = '7086607684:AAFEAN-E6XJJW77OfXs4tThEQyxOdi_t98w'
    os.environ['TELEGRAM_CHAT_ID'] = '1339285013'
    os.environ['POLYMARKET_CHECK_INTERVAL'] = '30'  # 30초 간격으로 설정
    
    print("🚀 폴리마켓 모니터 빠른 테스트 시작")
    print("30초간 모니터링하여 현재 마켓 상황을 확인합니다...")
    
    # 모니터 초기화
    monitor = PolymarketMonitor()
    
    try:
        # 첫 번째 마켓 확인
        print("\n1차 마켓 확인 중...")
        new_markets = monitor.check_new_markets()
        
        if new_markets:
            print(f"✅ {len(new_markets)}개의 새로운 마켓을 발견했습니다!")
            for market in new_markets:
                print(f"  - {market['title']}")
                monitor.send_new_market_alert(market)
        else:
            print("새로운 마켓이 없습니다. (정상 - 이미 알려진 마켓들)")
        
        print(f"\n현재 알려진 마켓 수: {len(monitor.known_markets)}")
        
        # 30초 대기
        print("\n30초 후 다시 확인합니다...")
        time.sleep(30)
        
        # 두 번째 마켓 확인
        print("\n2차 마켓 확인 중...")
        new_markets = monitor.check_new_markets()
        
        if new_markets:
            print(f"✅ {len(new_markets)}개의 새로운 마켓을 발견했습니다!")
            for market in new_markets:
                print(f"  - {market['title']}")
                monitor.send_new_market_alert(market)
        else:
            print("새로운 마켓이 없습니다. (정상)")
        
        print(f"\n최종 알려진 마켓 수: {len(monitor.known_markets)}")
        print("\n✅ 빠른 테스트 완료!")
        print("봇이 정상적으로 작동합니다. 실제 모니터링을 시작하려면:")
        print("  python3 polymarket_monitor.py")
        
    except KeyboardInterrupt:
        print("\n테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")

if __name__ == "__main__":
    quick_test()