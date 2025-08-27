#!/usr/bin/env python3
"""
텔레그램 알림 테스트 스크립트
"""

import os
from notification_system import NotificationSystem

def test_telegram_notification():
    """텔레그램 알림 테스트"""
    # 환경 변수 설정
    os.environ['TELEGRAM_BOT_TOKEN'] = '7086607684:AAFEAN-E6XJJW77OfXs4tThEQyxOdi_t98w'
    os.environ['TELEGRAM_CHAT_ID'] = '1339285013'
    
    # 알림 시스템 초기화
    notification = NotificationSystem()
    
    # 테스트 메시지 전송
    test_message = """
🚨 <b>폴리마켓 모니터 테스트 알림</b>

📊 <b>테스트 마켓:</b> Will this test message work?
🔗 <b>링크:</b> <a href="https://polymarket.com">폴리마켓에서 보기</a>
📅 <b>만료일:</b> 2024-12-31 23:59 UTC
💰 <b>총 거래량:</b> $1,000,000
👥 <b>참여자 수:</b> 999

⏰ <b>테스트 시간:</b> 지금
🤖 <b>상태:</b> 봇이 정상적으로 작동 중입니다!
    """.strip()
    
    print("텔레그램 테스트 메시지를 전송합니다...")
    success = notification.send_telegram_message(test_message)
    
    if success:
        print("✅ 텔레그램 테스트 메시지 전송 성공!")
        print("텔레그램에서 메시지를 확인해보세요.")
        return True
    else:
        print("❌ 텔레그램 테스트 메시지 전송 실패!")
        return False

if __name__ == "__main__":
    test_telegram_notification()