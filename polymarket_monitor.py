#!/usr/bin/env python3
"""
폴리마켓 신규 마켓 모니터링 봇
새로운 마켓이 생성되면 텔레그램으로 알림을 보냅니다.
"""

import os
import time
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import hashlib
from notification_system import NotificationSystem

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('polymarket_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PolymarketMonitor:
    """폴리마켓 마켓 모니터링 클래스"""
    
    def __init__(self):
        self.notification = NotificationSystem()
        self.known_markets: Set[str] = set()
        self.market_cache_file = "polymarket_known_markets.json"
        self.last_check_time = None
        
        # 폴리마켓 API 설정
        self.base_url = "https://clob.polymarket.com"
        self.markets_url = f"{self.base_url}/markets"
        self.orders_url = f"{self.base_url}/orders"
        
        # 모니터링 설정
        self.check_interval = int(os.getenv("POLYMARKET_CHECK_INTERVAL", "60"))  # 초 단위
        self.max_markets_per_check = int(os.getenv("POLYMARKET_MAX_MARKETS", "100"))
        
        # 알림 설정
        self.enable_new_market_alerts = os.getenv("ENABLE_NEW_MARKET_ALERTS", "true").lower() == "true"
        self.enable_market_updates = os.getenv("ENABLE_MARKET_UPDATES", "false").lower() == "true"
        
        # 알림 템플릿
        self.alert_templates = {
            "new_market": """
🚨 <b>새로운 폴리마켓 마켓 발견!</b>

📊 <b>마켓:</b> {title}
🔗 <b>링크:</b> <a href="https://polymarket.com/markets/{slug}">폴리마켓에서 보기</a>
📅 <b>만료일:</b> {expiration_date}
💰 <b>총 거래량:</b> ${total_volume:,.0f}
👥 <b>참여자 수:</b> {participant_count}

⏰ <b>발견 시간:</b> {discovery_time}
            """,
            "market_update": """
📈 <b>폴리마켓 마켓 업데이트</b>

📊 <b>마켓:</b> {title}
💰 <b>총 거래량:</b> ${total_volume:,.0f} (변화: {volume_change:+.0f}%)
👥 <b>참여자 수:</b> {participant_count}
⏰ <b>업데이트 시간:</b> {update_time}
            """
        }
        
        self._load_known_markets()
        logger.info("폴리마켓 모니터 초기화 완료")
    
    def _load_known_markets(self):
        """이미 알려진 마켓들을 로드합니다."""
        try:
            if os.path.exists(self.market_cache_file):
                with open(self.market_cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.known_markets = set(data.get('known_markets', []))
                    self.last_check_time = data.get('last_check_time')
                    logger.info(f"기존 마켓 {len(self.known_markets)}개 로드됨")
            else:
                logger.info("기존 마켓 데이터가 없습니다. 처음부터 시작합니다.")
        except Exception as e:
            logger.error(f"마켓 데이터 로드 오류: {e}")
            self.known_markets = set()
    
    def _save_known_markets(self):
        """알려진 마켓들을 저장합니다."""
        try:
            data = {
                'known_markets': list(self.known_markets),
                'last_check_time': self.last_check_time,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.market_cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"마켓 데이터 저장 오류: {e}")
    
    def _get_market_hash(self, market: Dict) -> str:
        """마켓의 고유 해시를 생성합니다."""
        market_id = market.get('id', '')
        title = market.get('title', '')
        return hashlib.md5(f"{market_id}:{title}".encode()).hexdigest()
    
    def fetch_markets(self) -> List[Dict]:
        """폴리마켓에서 마켓 목록을 가져옵니다."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            params = {
                'limit': self.max_markets_per_check,
                'offset': 0
            }
            
            response = requests.get(
                self.markets_url,
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                markets = data.get('data', [])
                logger.info(f"폴리마켓에서 {len(markets)}개 마켓 가져옴")
                return markets
            else:
                logger.error(f"폴리마켓 API 오류: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"마켓 데이터 가져오기 오류: {e}")
            return []
    
    def fetch_market_details(self, market_id: str) -> Optional[Dict]:
        """특정 마켓의 상세 정보를 가져옵니다."""
        try:
            url = f"{self.base_url}/markets/{market_id}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"마켓 상세 정보 가져오기 실패: {market_id}")
                return None
                
        except Exception as e:
            logger.error(f"마켓 상세 정보 가져오기 오류: {e}")
            return None
    
    def format_market_info(self, market: Dict) -> Dict:
        """마켓 정보를 포맷팅합니다."""
        try:
            # 기본 정보
            title = market.get('question', 'Unknown Market')
            slug = market.get('market_slug', '')
            market_id = market.get('condition_id', market.get('question_id', ''))
            
            # 만료일
            expiration_date = 'Unknown'
            if 'end_date_iso' in market:
                try:
                    exp_date = datetime.fromisoformat(market['end_date_iso'].replace('Z', '+00:00'))
                    expiration_date = exp_date.strftime('%Y-%m-%d %H:%M UTC')
                except:
                    expiration_date = market['end_date_iso']
            
            # 마켓 상태
            closed = market.get('closed', False)
            accepting_orders = market.get('accepting_orders', False)
            active = market.get('active', True)
            
            # 토큰 정보에서 거래량과 참여자 수 추정
            tokens = market.get('tokens', [])
            total_volume = 0
            participant_count = len(tokens)
            
            # 토큰 가격 정보로 거래량 추정
            for token in tokens:
                price = token.get('price', 0)
                if isinstance(price, (int, float)):
                    total_volume += price * 1000  # 추정값
            
            # 상태 결정
            if closed:
                status = 'Closed'
            elif not accepting_orders:
                status = 'Not Accepting Orders'
            elif not active:
                status = 'Inactive'
            else:
                status = 'Active'
            
            return {
                'id': market_id,
                'title': title,
                'slug': slug,
                'expiration_date': expiration_date,
                'total_volume': total_volume,
                'participant_count': participant_count,
                'status': status,
                'closed': closed,
                'accepting_orders': accepting_orders,
                'raw_data': market
            }
        except Exception as e:
            logger.error(f"마켓 정보 포맷팅 오류: {e}")
            return {
                'id': market.get('condition_id', market.get('question_id', 'Unknown')),
                'title': market.get('question', 'Unknown Market'),
                'slug': market.get('market_slug', ''),
                'expiration_date': 'Unknown',
                'total_volume': 0,
                'participant_count': 0,
                'status': 'Unknown',
                'closed': True,
                'accepting_orders': False,
                'raw_data': market
            }
    
    def check_new_markets(self) -> List[Dict]:
        """새로운 마켓을 확인합니다."""
        current_markets = self.fetch_markets()
        new_markets = []
        
        for market in current_markets:
            # 종료되지 않은 마켓만 확인 (closed=False인 마켓)
            if market.get('closed', True):
                continue
                
            market_hash = self._get_market_hash(market)
            
            if market_hash not in self.known_markets:
                # 새로운 마켓 발견
                formatted_market = self.format_market_info(market)
                new_markets.append(formatted_market)
                self.known_markets.add(market_hash)
                logger.info(f"새로운 활성 마켓 발견: {formatted_market['title']}")
        
        if new_markets:
            self._save_known_markets()
            logger.info(f"총 {len(new_markets)}개 새로운 활성 마켓 발견")
        
        return new_markets
    
    def send_new_market_alert(self, market: Dict):
        """새로운 마켓 발견 알림을 보냅니다."""
        if not self.enable_new_market_alerts:
            return
        
        try:
            message = self.alert_templates["new_market"].format(
                title=market['title'],
                slug=market['slug'],
                expiration_date=market['expiration_date'],
                total_volume=market['total_volume'],
                participant_count=market['participant_count'],
                discovery_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')
            ).strip()
            
            # 텔레그램 알림 전송
            success = self.notification.send_telegram_message(message)
            
            if success:
                logger.info(f"새로운 마켓 알림 전송 성공: {market['title']}")
            else:
                logger.error(f"새로운 마켓 알림 전송 실패: {market['title']}")
                
        except Exception as e:
            logger.error(f"새로운 마켓 알림 전송 오류: {e}")
    
    def run_monitoring(self):
        """마켓 모니터링을 실행합니다."""
        logger.info("폴리마켓 마켓 모니터링 시작")
        
        try:
            while True:
                current_time = datetime.now()
                logger.info(f"마켓 확인 중... ({current_time.strftime('%Y-%m-%d %H:%M:%S')})")
                
                # 새로운 마켓 확인
                new_markets = self.check_new_markets()
                
                # 새로운 마켓이 있으면 알림 전송
                for market in new_markets:
                    self.send_new_market_alert(market)
                
                # 마지막 확인 시간 업데이트
                self.last_check_time = current_time.isoformat()
                
                # 다음 확인까지 대기
                logger.info(f"다음 확인까지 {self.check_interval}초 대기...")
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("모니터링 중단됨")
        except Exception as e:
            logger.error(f"모니터링 실행 오류: {e}")
        finally:
            self._save_known_markets()
            logger.info("폴리마켓 모니터 종료")

def main():
    """메인 함수"""
    try:
        monitor = PolymarketMonitor()
        monitor.run_monitoring()
    except Exception as e:
        logger.error(f"프로그램 실행 오류: {e}")

if __name__ == "__main__":
    main() 