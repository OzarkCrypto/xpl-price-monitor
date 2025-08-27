#!/usr/bin/env python3
"""
ALKIMI 가격 5분마다 알람 봇
5분마다 ALKIMI 가격을 체크하고 알람을 보냅니다
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
        logging.FileHandler('alkimi_5min_alert.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ALKIMI5MinAlert:
    def __init__(self):
        self.asset = "ALKIMI"
        self.coingecko_url = "https://api.coingecko.com/api/v3/simple/price?ids=alkimi&vs_currencies=usd"
        
        # 알림 시스템 초기화
        self.notification_system = NotificationSystem()
        
        # 모니터링 상태
        self.last_price = None
        self.price_change = 0.0
        
        logger.info(f"🚀 ALKIMI 5분마다 가격 알람 봇 시작")
        logger.info(f"⏰ 알람 간격: 5분")
    
    def get_alkimi_price(self):
        """CoinGecko에서 ALKIMI 가격을 가져옵니다"""
        try:
            response = requests.get(self.coingecko_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'alkimi' in data and 'usd' in data['alkimi']:
                    price = data['alkimi']['usd']
                    return price
            
            logger.warning(f"CoinGecko API 응답 오류: {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"가격 조회 오류: {e}")
            return None
    
    def calculate_price_change(self, current_price):
        """가격 변화율을 계산합니다"""
        if self.last_price is None:
            self.price_change = 0.0
        else:
            self.price_change = ((current_price - self.last_price) / self.last_price) * 100
        
        return self.price_change
    
    def send_price_alert(self, current_price, price_change):
        """가격 알람을 전송합니다"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 가격 변화 방향에 따른 이모지
            if price_change > 0:
                direction = "📈"
                change_text = f"+{price_change:.2f}%"
            elif price_change < 0:
                direction = "📉"
                change_text = f"{price_change:.2f}%"
            else:
                direction = "➡️"
                change_text = "0.00%"
            
            # 알림 메시지 생성
            message = f"""
{direction} ALKIMI 가격 알람 {direction}

⏰ 시간: {timestamp}
💰 현재 가격: ${current_price:.4f}
📊 가격 변화: {change_text}

🔗 CoinGecko: https://www.coingecko.com/en/coins/alkimi

📈 실시간 차트와 거래량을 확인하세요!
"""
            
            # 텔레그램으로 전송
            success = self.notification_system.send_telegram_message(message)
            
            if success:
                logger.info(f"✅ 가격 알람 전송 성공: ${current_price:.4f}")
            else:
                logger.error("❌ 가격 알람 전송 실패")
                
        except Exception as e:
            logger.error(f"가격 알람 전송 중 오류: {e}")
    
    def log_price_data(self, current_price, price_change):
        """가격 데이터를 로그에 기록합니다"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        logger.info("=" * 60)
        logger.info("📊 ALKIMI 가격 모니터링 결과")
        logger.info("=" * 60)
        logger.info(f"시간: {timestamp}")
        logger.info(f"자산: {self.asset}")
        logger.info(f"현재 가격: ${current_price:.4f}")
        
        if self.last_price is not None:
            logger.info(f"이전 가격: ${self.last_price:.4f}")
            logger.info(f"가격 변화: {price_change:.2f}%")
        else:
            logger.info("이전 가격: 첫 번째 조회")
            logger.info("가격 변화: 0.00%")
        
        logger.info("=" * 60)
    
    def monitor_once(self):
        """한 번의 가격 모니터링을 수행합니다"""
        try:
            logger.info("🔄 ALKIMI 가격 모니터링 시작...")
            
            # 현재 가격 조회
            current_price = self.get_alkimi_price()
            
            if current_price is None:
                logger.error("❌ 가격 정보를 가져올 수 없습니다.")
                return
            
            # 가격 변화율 계산
            price_change = self.calculate_price_change(current_price)
            
            # 로그 기록
            self.log_price_data(current_price, price_change)
            
            # 가격 알람 전송
            self.send_price_alert(current_price, price_change)
            
            # 가격 업데이트
            self.last_price = current_price
            
        except Exception as e:
            logger.error(f"모니터링 중 오류: {e}")
    
    def start_monitoring(self):
        """5분마다 가격 모니터링을 시작합니다"""
        logger.info(f"🚀 ALKIMI 5분마다 가격 모니터링 시작")
        logger.info(f"⏰ 모니터링 간격: 5분")
        logger.info("=" * 60)
        
        # 즉시 한 번 실행
        self.monitor_once()
        
        try:
            while True:
                # 5분(300초) 대기
                time.sleep(300)
                self.monitor_once()
                
        except KeyboardInterrupt:
            logger.info("⏹️  모니터링 중단됨")
        except Exception as e:
            logger.error(f"❌ 모니터링 루프 오류: {e}")

def main():
    """메인 함수"""
    print("🚀 ALKIMI 5분마다 가격 알람 봇")
    print("=" * 50)
    
    # 환경 변수 확인
    required_env_vars = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  다음 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        print("📝 .env 파일을 확인하세요.")
        return
    
    # 가격 모니터링 봇 생성 및 시작
    monitor = ALKIMI5MinAlert()
    
    try:
        monitor.start_monitoring()
    except Exception as e:
        logger.error(f"모니터링 시작 실패: {e}")

if __name__ == "__main__":
    main()
