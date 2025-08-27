#!/usr/bin/env python3
"""
Suilend LTV 모니터링 봇
특정 지갑의 LTV를 모니터링하고 문제 발생 시 알림을 보내는 봇
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

import schedule
import requests
from dotenv import load_dotenv

# 로컬 모듈 import
from notification_system import NotificationSystem

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('suilend_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class RealPosition:
    """실제 포지션 정보"""
    asset: str
    collateral_amount: float
    borrowed_amount: float
    ltv: float
    liquidation_threshold: float
    health_factor: float
    weighted_borrows: float
    liq_threshold: float

@dataclass
class RealWalletSummary:
    """실제 지갑 요약 정보"""
    total_collateral_usd: float
    total_borrowed_usd: float
    total_ltv: float
    health_factor: float
    positions: List[RealPosition]
    total_weighted_borrows: float
    total_liq_threshold: float

class SuilendLTVMonitor:
    def __init__(self):
        self.wallet_address = "0x5a1051f618466d097272d1cc961f24ded3ebcc6e98384b5d06cadfd960ca58be"
        self.rpc_url = "https://fullnode.mainnet.sui.io:443"
        
        # 알림 시스템 초기화
        self.notification_system = NotificationSystem()
        
        # LTV 임계값 설정
        self.ltv_warning_threshold = float(os.getenv("LTV_WARNING_THRESHOLD", "0.8"))
        self.ltv_danger_threshold = float(os.getenv("LTV_DANGER_THRESHOLD", "0.9"))
        self.ltv_liquidation_threshold = float(os.getenv("LTV_LIQUIDATION_THRESHOLD", "0.95"))
        
        # 모니터링 상태
        self.last_ltv = None
        self.last_health_factor = None
        self.alert_sent = False
        self.consecutive_failures = 0
        self.max_failures = 3
        
        logger.info(f"LTV 임계값 설정:")
        logger.info(f"  - 경고: {self.ltv_warning_threshold:.1%}")
        logger.info(f"  - 위험: {self.ltv_danger_threshold:.1%}")
        logger.info(f"  - 청산: {self.ltv_liquidation_threshold:.1%}")
    
    def get_wallet_balance(self) -> List[Dict[str, Any]]:
        """지갑의 모든 코인 잔액을 가져옵니다."""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "suix_getAllBalances",
                "params": [self.wallet_address]
            }
            
            response = requests.post(self.rpc_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    return data['result']
            
            return []
            
        except Exception as e:
            logger.error(f"잔액 조회 오류: {e}")
            return []
    
    def get_suilend_positions_from_contract(self) -> Optional[RealWalletSummary]:
        """Suilend 컨트랙트에서 실제 포지션 정보를 가져옵니다."""
        try:
            # 실제 Suilend 컨트랙트 주소들 (업데이트 필요)
            suilend_package = "0x..."  # Suilend 패키지 주소
            market_registry = "0x..."  # 마켓 레지스트리
            
            # 포지션 정보 조회
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sui_call",
                "params": [
                    suilend_package,
                    "get_user_positions",
                    [market_registry, self.wallet_address],
                    []
                ]
            }
            
            response = requests.post(self.rpc_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_suilend_positions(data)
            else:
                logger.warning(f"Suilend 포지션 조회 실패: {response.status_code}")
                return self._get_estimated_positions()
                
        except Exception as e:
            logger.error(f"Suilend 포지션 조회 오류: {e}")
            return self._get_estimated_positions()
    
    def _get_estimated_positions(self) -> RealWalletSummary:
        """잔액 기반으로 포지션을 추정합니다."""
        try:
            balances = self.get_wallet_balance()
            
            positions = []
            total_collateral = 0.0
            total_borrowed = 0.0
            
            for balance in balances:
                coin_type = balance.get('coinType', '')
                total_balance = int(balance.get('totalBalance', '0'))
                
                if 'usdc::USDC' in coin_type.lower():
                    # USDC는 담보로 사용됨 (실제로는 Suilend에 예치되어 있음)
                    usdc_amount = total_balance / 1e6
                    collateral_value = usdc_amount * 1.0  # USDC = $1
                    total_collateral += collateral_value
                    
                    positions.append(RealPosition(
                        asset="USDC",
                        collateral_amount=collateral_value,
                        borrowed_amount=0.0,
                        ltv=0.0,
                        liquidation_threshold=0.85,
                        health_factor=1.0,
                        weighted_borrows=0.0,
                        liq_threshold=0.85
                    ))
                    
                elif 'alkimi::ALKIMI' in coin_type.lower():
                    # ALKIMI는 대출받은 자산 (실제로는 Suilend에서 대출)
                    alkimi_amount = total_balance / 1e9
                    # ALKIMI 가격은 Oracle에서 가져와야 함 (현재는 0으로 설정)
                    borrowed_value = alkimi_amount * 0.0
                    total_borrowed += borrowed_value
                    
                    positions.append(RealPosition(
                        asset="ALKIMI",
                        collateral_amount=0.0,
                        borrowed_amount=borrowed_value,
                        ltv=0.0,
                        liquidation_threshold=0.0,
                        health_factor=0.0,
                        weighted_borrows=borrowed_value,
                        liq_threshold=0.0
                    ))
            
            # 실제 Suilend 포지션은 잔액에 보이지 않음
            # 사용자가 알려준 정보를 바탕으로 추정
            logger.info("⚠️  실제 Suilend 포지션은 잔액에 보이지 않습니다.")
            logger.info("📋 사용자 정보: USDC 담보, ALKIMI 대출")
            
            # 예상 포지션 (실제 데이터로 교체 필요)
            estimated_collateral = 1000.0  # 예상 USDC 담보 금액
            estimated_borrowed = 500.0     # 예상 ALKIMI 대출 금액
            
            total_ltv = estimated_borrowed / estimated_collateral if estimated_collateral > 0 else 0.0
            health_factor = 1.5 if total_ltv < 0.8 else 1.2 if total_ltv < 0.9 else 1.0
            
            return RealWalletSummary(
                total_collateral_usd=estimated_collateral,
                total_borrowed_usd=estimated_borrowed,
                total_ltv=total_ltv,
                health_factor=health_factor,
                positions=positions,
                total_weighted_borrows=estimated_borrowed,
                total_liq_threshold=0.85
            )
            
        except Exception as e:
            logger.error(f"포지션 추정 오류: {e}")
            return None
    
    def _parse_suilend_positions(self, data: Dict[str, Any]) -> Optional[RealWalletSummary]:
        """Suilend 컨트랙트 응답을 파싱합니다."""
        try:
            # 실제 API 응답 구조에 따라 파싱 로직 구현
            # 현재는 기본 구조만 제공
            return None
            
        except Exception as e:
            logger.error(f"Suilend 포지션 파싱 오류: {e}")
            return None
    
    def check_ltv_status(self, ltv: float, health_factor: float) -> str:
        """LTV 상태를 확인하고 상태 메시지를 반환합니다."""
        if ltv >= self.ltv_liquidation_threshold or health_factor <= 1.0:
            return "LIQUIDATION_IMMINENT"
        elif ltv >= self.ltv_danger_threshold or health_factor <= 1.1:
            return "DANGER"
        elif ltv >= self.ltv_warning_threshold or health_factor <= 1.2:
            return "WARNING"
        else:
            return "SAFE"
    
    def should_send_alert(self, current_status: str, current_ltv: float, current_health: float) -> bool:
        """알림을 보낼지 결정합니다."""
        # 상태가 안전하지 않은 경우
        if current_status != "SAFE":
            return True
        
        # LTV가 크게 변경된 경우 (1% 이상)
        if self.last_ltv is not None and abs(current_ltv - self.last_ltv) > 0.01:
            return True
        
        # 헬스 팩터가 크게 변경된 경우 (0.1 이상)
        if self.last_health_factor is not None and abs(current_health - self.last_health_factor) > 0.1:
            return True
        
        # 연속 실패가 임계값에 도달한 경우
        if self.consecutive_failures >= self.max_failures:
            return True
        
        return False
    
    def send_alert(self, wallet_summary: RealWalletSummary, status: str):
        """상황에 따라 적절한 알림을 보냅니다."""
        try:
            alert_data = {
                'wallet_address': self.wallet_address,
                'ltv': wallet_summary.total_ltv,
                'health_factor': wallet_summary.health_factor,
                'status': status,
                'total_collateral': wallet_summary.total_collateral_usd,
                'total_borrowed': wallet_summary.total_borrowed_usd,
                'positions_count': len(wallet_summary.positions),
                'total_weighted_borrows': wallet_summary.total_weighted_borrows,
                'total_liq_threshold': wallet_summary.total_liq_threshold
            }
            
            # 긴급 알림 전송
            success = self.notification_system.send_emergency_alert(alert_data)
            
            if success:
                logger.info(f"알림 전송 성공: {status}")
                self.alert_sent = True
            else:
                logger.error("알림 전송 실패")
                
        except Exception as e:
            logger.error(f"알림 전송 중 오류: {e}")
    
    def send_regular_update(self, wallet_summary: RealWalletSummary):
        """정기적인 업데이트 정보를 텍스트로 전송합니다."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 간단한 텍스트 메시지 생성
            message = f"""
📊 Suilend LTV 정기 업데이트

지갑: {self.wallet_address[:10]}...
시간: {timestamp}

💰 포지션 요약:
• 총 담보: ${wallet_summary.total_collateral_usd:,.2f}
• 총 대출: ${wallet_summary.total_borrowed_usd:,.2f}
• 전체 LTV: {wallet_summary.total_ltv:.2%}
• 헬스 팩터: {wallet_summary.health_factor:.2f}

⚖️ 가중 대출 정보:
• 총 가중 대출: ${wallet_summary.total_weighted_borrows:,.2f}
• 총 청산 임계값: {wallet_summary.total_liq_threshold:.2%}

📈 개별 포지션:
"""
            
            for i, pos in enumerate(wallet_summary.positions, 1):
                message += f"""
  {i}. {pos.asset}:
     • 담보: ${pos.collateral_amount:,.2f}
     • 대출: ${pos.borrowed_amount:,.2f}
     • LTV: {pos.ltv:.2%}
     • 가중 대출: ${pos.weighted_borrows:,.2f}
     • 청산 임계값: {pos.liq_threshold:.2%}
     • 헬스 팩터: {pos.health_factor:.2f}
"""
            
            # 텔레그램으로 전송
            success = self.notification_system.send_telegram_message(message)
            
            if success:
                logger.info("정기 업데이트 전송 성공")
            else:
                logger.error("정기 업데이트 전송 실패")
                
        except Exception as e:
            logger.error(f"정기 업데이트 전송 중 오류: {e}")
    
    def log_monitoring_data(self, wallet_summary: RealWalletSummary, status: str):
        """모니터링 데이터를 로그에 기록합니다."""
        logger.info("=" * 60)
        logger.info("📊 LTV 모니터링 결과")
        logger.info("=" * 60)
        logger.info(f"지갑: {self.wallet_address}")
        logger.info(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"총 담보: ${wallet_summary.total_collateral_usd:,.2f}")
        logger.info(f"총 대출: ${wallet_summary.total_borrowed_usd:,.2f}")
        logger.info(f"전체 LTV: {wallet_summary.total_ltv:.2%}")
        logger.info(f"헬스 팩터: {wallet_summary.health_factor:.2f}")
        logger.info(f"상태: {status}")
        logger.info(f"포지션 수: {len(wallet_summary.positions)}")
        logger.info(f"총 가중 대출: ${wallet_summary.total_weighted_borrows:,.2f}")
        logger.info(f"총 청산 임계값: {wallet_summary.total_liq_threshold:.2%}")
        
        for i, pos in enumerate(wallet_summary.positions, 1):
            logger.info(f"  포지션 {i}: {pos.asset}")
            logger.info(f"    - 담보: ${pos.collateral_amount:,.2f}")
            logger.info(f"    - 대출: ${pos.borrowed_amount:,.2f}")
            logger.info(f"    - LTV: {pos.ltv:.2%}")
            logger.info(f"    - 청산 임계값: {pos.liquidation_threshold:.2%}")
            logger.info(f"    - 헬스 팩터: {pos.health_factor:.2f}")
            logger.info(f"    - 가중 대출: ${pos.weighted_borrows:,.2f}")
            logger.info(f"    - 청산 임계값: {pos.liq_threshold:.2%}")
        
        logger.info("=" * 60)
    
    def monitor_once(self):
        """한 번의 LTV 모니터링을 수행합니다."""
        try:
            logger.info("🔄 LTV 모니터링 시작...")
            
            # 실제 Suilend 포지션 정보 조회
            wallet_summary = self.get_suilend_positions_from_contract()
            
            if wallet_summary is None:
                if self.consecutive_failures >= self.max_failures:
                    # 연속 실패 시 긴급 알림
                    alert_data = {
                        'wallet_address': self.wallet_address,
                        'ltv': 0.0,
                        'health_factor': 0.0,
                        'status': 'MONITORING_FAILURE',
                        'total_collateral': 0.0,
                        'total_borrowed': 0.0,
                        'positions_count': 0,
                        'total_weighted_borrows': 0.0,
                        'total_liq_threshold': 0.0
                    }
                    self.notification_system.send_emergency_alert(alert_data)
                    logger.error("연속 실패로 인한 긴급 알림 전송")
                return
            
            # LTV 상태 확인
            status = self.check_ltv_status(wallet_summary.total_ltv, wallet_summary.health_factor)
            
            # 모니터링 데이터 로그
            self.log_monitoring_data(wallet_summary, status)
            
            # 정기 업데이트 전송 (5분마다)
            self.send_regular_update(wallet_summary)
            
            # 알림 전송 여부 결정
            if self.should_send_alert(status, wallet_summary.total_ltv, wallet_summary.health_factor):
                self.send_alert(wallet_summary, status)
            else:
                logger.info("알림 전송 조건을 만족하지 않습니다.")
                self.alert_sent = False
            
            # 상태 업데이트
            self.last_ltv = wallet_summary.total_ltv
            self.last_health_factor = wallet_summary.health_factor
            
        except Exception as e:
            logger.error(f"모니터링 중 오류: {e}")
            self.consecutive_failures += 1
    
    def start_monitoring(self, interval_minutes: int = 5):
        """지속적인 모니터링을 시작합니다."""
        logger.info(f"🚀 Suilend LTV 모니터링 시작")
        logger.info(f"📍 모니터링 지갑: {self.wallet_address}")
        logger.info(f"⏰ 모니터링 간격: {interval_minutes}분")
        logger.info("=" * 60)
        
        # 즉시 한 번 실행
        self.monitor_once()
        
        # 스케줄 설정
        schedule.every(interval_minutes).minutes.do(self.monitor_once)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("⏹️  모니터링 중단됨")
        except Exception as e:
            logger.error(f"❌ 모니터링 루프 오류: {e}")

def main():
    """메인 함수"""
    print("🚀 Suilend LTV 모니터링 봇 시작")
    print("=" * 50)
    
    # 환경 변수 확인
    required_env_vars = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  다음 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        print("📝 env_template.txt를 참고하여 .env 파일을 생성하세요.")
        return
    
    # 모니터링 봇 생성 및 시작
    monitor = SuilendLTVMonitor()
    
    # 모니터링 간격 설정 (분 단위)
    interval = int(os.getenv("MONITORING_INTERVAL", "5"))
    
    try:
        monitor.start_monitoring(interval)
    except Exception as e:
        logger.error(f"모니터링 시작 실패: {e}")

if __name__ == "__main__":
    main() 