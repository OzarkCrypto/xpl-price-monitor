#!/usr/bin/env python3
"""
간단한 ALKIMI 가격 알람 봇
SUI 체인에서 ALKIMI 가격이 $0.25가 되면 알람을 보냅니다
"""

import requests
import time
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from notification_system import NotificationSystem

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('alkimi_alert.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleALKIMIAlert:
    def __init__(self):
        self.target_price = 0.25  # 목표 가격 $0.25
        self.alert_sent = False
        
        # 알림 시스템 초기화
        self.notification_system = NotificationSystem()
        
        logger.info(f"🚀 ALKIMI 가격 알람 봇 시작")
        logger.info(f"🎯 목표 가격: ${self.target_price}")
    
    def get_alkimi_price(self):
        """ALKIMI 가격을 가져옵니다 (여러 소스 시도)"""
        try:
            # 1. CoinGecko 시도
            url = "https://api.coingecko.com/api/v3/simple/price?ids=alkimi&vs_currencies=usd"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'alkimi' in data and 'usd' in data['alkimi']:
                    price = data['alkimi']['usd']
                    logger.info(f"📊 ALKIMI 가격: ${price}")
                    return price
            
            logger.warning("CoinGecko API 실패, 다른 소스 시도...")
            
            # 2. 모의 가격 (테스트용)
            mock_price = 0.20  # 실제로는 Oracle에서 가져와야 함
            logger.info(f"📊 모의 ALKIMI 가격: ${mock_price}")
            return mock_price
            
        except Exception as e:
            logger.error(f"가격 조회 오류: {e}")
            return None
    
    def check_and_alert(self, current_price):
        """가격을 확인하고 알람을 보냅니다"""
        if current_price is None:
            return
        
        # 목표 가격에 도달했는지 확인
        if current_price >= self.target_price and not self.alert_sent:
            logger.info(f"🚨 ALKIMI 가격이 ${self.target_price}에 도달했습니다!")
            
            # 알림 메시지 생성
            message = f"""
🚨 ALKIMI 가격 알람! 🚨

ALKIMI 가격이 목표 가격 ${self.target_price}에 도달했습니다!

📊 현재 가격: ${current_price:.4f}
🎯 목표 가격: ${self.target_price}
⏰ 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚠️  투자에 주의하세요!
"""
            
            # 텔레그램으로 전송
            success = self.notification_system.send_telegram_message(message)
            
            if success:
                logger.info("✅ 알람 전송 성공!")
                self.alert_sent = True
            else:
                logger.error("❌ 알람 전송 실패")
        else:
            logger.info(f"📊 현재 가격: ${current_price:.4f} (목표: ${self.target_price})")
    
    def run(self):
        """메인 실행 루프"""
        logger.info("🔄 ALKIMI 가격 모니터링 시작...")
        
        try:
            while True:
                # 가격 확인
                price = self.get_alkimi_price()
                self.check_and_alert(price)
                
                # 30초 대기
                time.sleep(30)
                
        except KeyboardInterrupt:
            logger.info("⏹️  모니터링 중단됨")
        except Exception as e:
            logger.error(f"❌ 오류 발생: {e}")

def main():
    print("🚀 간단한 ALKIMI 가격 알람 봇")
    print("=" * 40)
    
    # 환경 변수 확인
    if not os.getenv("TELEGRAM_BOT_TOKEN") or not os.getenv("TELEGRAM_CHAT_ID"):
        print("⚠️  TELEGRAM_BOT_TOKEN과 TELEGRAM_CHAT_ID가 설정되지 않았습니다.")
        return
    
    # 봇 실행
    bot = SimpleALKIMIAlert()
    bot.run()

if __name__ == "__main__":
    main()
