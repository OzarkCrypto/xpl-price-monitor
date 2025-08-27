#!/usr/bin/env python3
"""
ALKIMI 가격 모니터링 봇
ALKIMI 가격이 $0.25에 도달하면 알람을 보내는 봇
"""

import requests
import json
import time
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass

from dotenv import load_dotenv
from notification_system import NotificationSystem

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('alkimi_price_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class PriceAlert:
    """가격 알림 정보"""
    asset: str
    current_price: float
    target_price: float
    timestamp: datetime
    status: str  # "BELOW_TARGET", "ABOVE_TARGET", "AT_TARGET"

class ALKIMIPriceMonitor:
    def __init__(self):
        self.asset = "ALKIMI"
        self.target_price = 0.25  # 목표 가격 $0.25
        self.alert_threshold = 0.01  # $0.01 이내로 접근하면 알림
        
        # 알림 시스템 초기화
        self.notification_system = NotificationSystem()
        
        # 모니터링 상태
        self.last_price = None
        self.last_alert_time = None
        self.alert_cooldown = 300  # 5분 쿨다운
        self.price_history = []
        
        # 가격 소스들
        self.price_sources = {
            "coingecko": "https://api.coingecko.com/api/v3/simple/price?ids=alkimi&vs_currencies=usd",
            "pyth": "https://api.pyth.network/v2/price_feeds/",  # Pyth Network Oracle
            "sui_oracle": "https://fullnode.mainnet.sui.io:443"  # SUI 체인 Oracle
        }
        
        logger.info(f"🚀 ALKIMI 가격 모니터링 시작")
        logger.info(f"🎯 목표 가격: ${self.target_price}")
        logger.info(f"🔔 알림 임계값: ${self.alert_threshold}")
    
    def get_alkimi_price_from_coingecko(self) -> Optional[float]:
        """CoinGecko API에서 ALKIMI 가격을 가져옵니다."""
        try:
            response = requests.get(self.price_sources["coingecko"], timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'alkimi' in data and 'usd' in data['alkimi']:
                    price = data['alkimi']['usd']
                    logger.info(f"📊 CoinGecko ALKIMI 가격: ${price}")
                    return price
            
            logger.warning(f"CoinGecko API 응답 오류: {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"CoinGecko API 오류: {e}")
            return None
    
    def get_alkimi_price_from_pyth(self) -> Optional[float]:
        """Pyth Network Oracle에서 ALKIMI 가격을 가져옵니다."""
        try:
            # ALKIMI의 Pyth Network price feed ID (실제 ID로 업데이트 필요)
            alkimi_feed_id = "ALKIMI_USD"  # 예시 ID
            
            url = f"{self.price_sources['pyth']}{alkimi_feed_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Pyth Network 응답 구조에 따라 파싱
                if 'data' in data and 'price' in data['data']:
                    price = float(data['data']['price'])
                    logger.info(f"📊 Pyth Network ALKIMI 가격: ${price}")
                    return price
            
            logger.warning(f"Pyth Network API 응답 오류: {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"Pyth Network API 오류: {e}")
            return None
    
    def get_alkimi_price_from_sui_oracle(self) -> Optional[float]:
        """SUI 체인 Oracle에서 ALKIMI 가격을 가져옵니다."""
        try:
            # SUI 체인에서 Oracle 데이터 조회 (실제 컨트랙트 주소 필요)
            oracle_address = "0x..."  # Oracle 컨트랙트 주소
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sui_call",
                "params": [
                    oracle_address,
                    "get_price",
                    ["ALKIMI"],
                    []
                ]
            }
            
            response = requests.post(self.price_sources["sui_oracle"], json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # SUI Oracle 응답 구조에 따라 파싱
                if 'result' in data:
                    price = float(data['result'])
                    logger.info(f"📊 SUI Oracle ALKIMI 가격: ${price}")
                    return price
            
            logger.warning(f"SUI Oracle API 응답 오류: {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"SUI Oracle API 오류: {e}")
            return None
    
    def get_current_alkimi_price(self) -> Optional[float]:
        """여러 소스에서 ALKIMI 가격을 가져오려고 시도합니다."""
        # 1. CoinGecko 시도
        price = self.get_alkimi_price_from_coingecko()
        if price is not None:
            return price
        
        # 2. Pyth Network 시도
        price = self.get_alkimi_price_from_pyth()
        if price is not None:
            return price
        
        # 3. SUI Oracle 시도
        price = self.get_alkimi_price_from_sui_oracle()
        if price is not None:
            return price
        
        # 4. 모든 소스 실패 시 모의 가격 사용 (테스트용)
        logger.warning("⚠️  모든 가격 소스 실패, 모의 가격 사용")
        mock_price = 0.20  # 모의 가격
        logger.info(f"📊 모의 ALKIMI 가격: ${mock_price}")
        return mock_price
    
    def check_price_alert(self, current_price: float) -> Optional[PriceAlert]:
        """가격 알림 조건을 확인합니다."""
        if current_price is None:
            return None
        
        # 목표 가격에 근접했는지 확인
        price_diff = abs(current_price - self.target_price)
        
        if price_diff <= self.alert_threshold:
            # 쿨다운 확인
            if (self.last_alert_time is None or 
                (datetime.now() - self.last_alert_time).total_seconds() > self.alert_cooldown):
                
                if current_price <= self.target_price:
                    status = "BELOW_TARGET"
                elif current_price >= self.target_price:
                    status = "ABOVE_TARGET"
                else:
                    status = "AT_TARGET"
                
                return PriceAlert(
                    asset=self.asset,
                    current_price=current_price,
                    target_price=self.target_price,
                    timestamp=datetime.now(),
                    status=status
                )
        
        return None
    
    def send_price_alert(self, alert: PriceAlert):
        """가격 알림을 전송합니다."""
        try:
            timestamp = alert.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            
            # 알림 메시지 생성
            if alert.status == "BELOW_TARGET":
                message = f"""
🚨 ALKIMI 가격 알림! 🚨

ALKIMI 가격이 목표 가격 ${self.target_price}에 도달했습니다!

📊 현재 가격: ${alert.current_price:.4f}
🎯 목표 가격: ${self.target_price}
⏰ 시간: {timestamp}
📉 상태: 목표 가격 이하

⚠️  투자에 주의하세요!
"""
            elif alert.status == "ABOVE_TARGET":
                message = f"""
📈 ALKIMI 가격 알림! 📈

ALKIMI 가격이 목표 가격 ${self.target_price}를 초과했습니다!

📊 현재 가격: ${alert.current_price:.4f}
🎯 목표 가격: ${self.target_price}
⏰ 시간: {timestamp}
📈 상태: 목표 가격 초과

💡 투자 기회를 확인해보세요!
"""
            else:
                message = f"""
🎯 ALKIMI 가격 알림! 🎯

ALKIMI 가격이 목표 가격 ${self.target_price}에 정확히 도달했습니다!

📊 현재 가격: ${alert.current_price:.4f}
🎯 목표 가격: ${self.target_price}
⏰ 시간: {timestamp}
🎯 상태: 목표 가격 달성

📊 시장 상황을 주의깊게 관찰하세요!
"""
            
            # 긴급 알림 전송
            alert_data = {
                'asset': alert.asset,
                'current_price': alert.current_price,
                'target_price': alert.target_price,
                'status': alert.status,
                'timestamp': timestamp,
                'message': message
            }
            
            success = self.notification_system.send_emergency_alert(alert_data)
            
            if success:
                logger.info(f"🚨 가격 알림 전송 성공: {alert.status}")
                self.last_alert_time = datetime.now()
            else:
                logger.error("❌ 가격 알림 전송 실패")
                
        except Exception as e:
            logger.error(f"가격 알림 전송 중 오류: {e}")
    
    def log_price_data(self, current_price: float, alert: Optional[PriceAlert] = None):
        """가격 데이터를 로그에 기록합니다."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        logger.info("=" * 60)
        logger.info("📊 ALKIMI 가격 모니터링 결과")
        logger.info("=" * 60)
        logger.info(f"시간: {timestamp}")
        logger.info(f"자산: {self.asset}")
        logger.info(f"현재 가격: ${current_price:.4f}")
        logger.info(f"목표 가격: ${self.target_price}")
        logger.info(f"가격 차이: ${abs(current_price - self.target_price):.4f}")
        logger.info(f"알림 임계값: ${self.alert_threshold}")
        
        if alert:
            logger.info(f"알림 상태: {alert.status}")
            logger.info(f"알림 시간: {alert.timestamp}")
        else:
            logger.info("알림 상태: 알림 없음")
        
        # 가격 히스토리 업데이트
        self.price_history.append({
            'timestamp': timestamp,
            'price': current_price,
            'alert': alert.status if alert else None
        })
        
        # 최근 100개만 유지
        if len(self.price_history) > 100:
            self.price_history = self.price_history[-100:]
        
        logger.info("=" * 60)
    
    def monitor_once(self):
        """한 번의 가격 모니터링을 수행합니다."""
        try:
            logger.info("🔄 ALKIMI 가격 모니터링 시작...")
            
            # 현재 가격 조회
            current_price = self.get_current_alkimi_price()
            
            if current_price is None:
                logger.error("❌ 가격 정보를 가져올 수 없습니다.")
                return
            
            # 가격 알림 확인
            alert = self.check_price_alert(current_price)
            
            # 로그 기록
            self.log_price_data(current_price, alert)
            
            # 알림 전송
            if alert:
                self.send_price_alert(alert)
            else:
                logger.info("📊 알림 조건을 만족하지 않습니다.")
            
            # 가격 업데이트
            self.last_price = current_price
            
        except Exception as e:
            logger.error(f"모니터링 중 오류: {e}")
    
    def start_monitoring(self, interval_seconds: int = 60):
        """지속적인 가격 모니터링을 시작합니다."""
        logger.info(f"🚀 ALKIMI 가격 모니터링 시작")
        logger.info(f"🎯 목표 가격: ${self.target_price}")
        logger.info(f"⏰ 모니터링 간격: {interval_seconds}초")
        logger.info("=" * 60)
        
        # 즉시 한 번 실행
        self.monitor_once()
        
        try:
            while True:
                time.sleep(interval_seconds)
                self.monitor_once()
                
        except KeyboardInterrupt:
            logger.info("⏹️  모니터링 중단됨")
        except Exception as e:
            logger.error(f"❌ 모니터링 루프 오류: {e}")

def main():
    """메인 함수"""
    print("🚀 ALKIMI 가격 모니터링 봇 시작")
    print("=" * 50)
    
    # 환경 변수 확인
    required_env_vars = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  다음 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        print("📝 .env 파일을 확인하세요.")
        return
    
    # 가격 모니터링 봇 생성 및 시작
    monitor = ALKIMIPriceMonitor()
    
    # 모니터링 간격 설정 (초 단위)
    interval = int(os.getenv("PRICE_MONITORING_INTERVAL", "60"))
    
    try:
        monitor.start_monitoring(interval)
    except Exception as e:
        logger.error(f"모니터링 시작 실패: {e}")

if __name__ == "__main__":
    main() 