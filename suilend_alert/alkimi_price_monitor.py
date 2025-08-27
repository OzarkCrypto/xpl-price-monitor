#!/usr/bin/env python3
"""
ALKIMI 가격 모니터링 봇
CoinMarketCap에서 ALKIMI 가격을 가져와서 텔레그램으로 전송하는 봇
"""

import requests
import time
import logging
import os
import re
from datetime import datetime
from dotenv import load_dotenv
from notification_system import NotificationSystem
from bs4 import BeautifulSoup

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

class ALKIMIPriceMonitor:
    def __init__(self):
        self.asset = "ALKIMI"
        self.target_price = 0.25  # 목표 가격 $0.25
        self.alert_threshold = 0.01  # $0.01 이내로 접근하면 알림
        
        # 데이터 소스 설정 (우선순위: DexScreener > CoinMarketCap)
        self.dexscreener_api_url = "https://api.dexscreener.com/latest/dex/tokens/0x2ae42f340d32653cd079f3e80e2e6c2f9485cd8a91491bac0b47e93708c8f049"
        self.coinmarketcap_url = "https://coinmarketcap.com/currencies/alkimiexchange/"
        
        # 알림 시스템 초기화
        self.notification_system = NotificationSystem()
        
        # 모니터링 상태
        self.last_alert_time = None
        self.alert_cooldown = 300  # 5분 쿨다운
        
        logger.info(f"🚀 ALKIMI 가격 모니터링 시작")
        logger.info(f"🎯 목표 가격: ${self.target_price}")
        logger.info(f"🔔 알림 임계값: ${self.alert_threshold}")
        logger.info(f"🌐 주요 데이터 소스: DexScreener API")
        logger.info(f"🌐 백업 데이터 소스: CoinMarketCap")
    
    def get_alkimi_price_from_dexscreener(self):
        """DexScreener API에서 ALKIMI 가격을 가져옵니다."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(self.dexscreener_api_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"📡 DexScreener API 응답: {len(data.get('pairs', []))}개 페어 발견")
            
            if 'pairs' in data and data['pairs']:
                # 첫 번째 페어 정보 사용 (보통 가장 유동성이 높은 페어)
                pair = data['pairs'][0]
                
                price_data = {}
                
                # 현재 가격
                if 'priceUsd' in pair:
                    price_data['current_price'] = float(pair['priceUsd'])
                    logger.info(f"📊 DexScreener ALKIMI 가격: ${price_data['current_price']:.6f}")
                
                # 24시간 변화율
                if 'priceChange' in pair and 'h24' in pair['priceChange']:
                    price_data['24h_change'] = float(pair['priceChange']['h24'])
                    logger.info(f"📈 24시간 변화율: {price_data['24h_change']}%")
                
                # 유동성
                if 'liquidity' in pair and 'usd' in pair['liquidity']:
                    price_data['liquidity'] = float(pair['liquidity']['usd'])
                    logger.info(f"💧 유동성: ${price_data['liquidity']:,.0f}")
                
                # 24시간 거래량
                if 'volume' in pair and 'h24' in pair['volume']:
                    price_data['24h_volume'] = float(pair['volume']['h24'])
                    logger.info(f"📊 24시간 거래량: ${price_data['24h_volume']:,.0f}")
                
                # 거래소 정보
                if 'dexId' in pair:
                    price_data['dex'] = pair['dexId']
                    logger.info(f"🏪 거래소: {price_data['dex']}")
                
                # 페어 주소
                if 'pairAddress' in pair:
                    price_data['pair_address'] = pair['pairAddress']
                
                # 토큰 정보
                if 'baseToken' in pair:
                    base_token = pair['baseToken']
                    if 'name' in base_token:
                        price_data['token_name'] = base_token['name']
                    if 'symbol' in base_token:
                        price_data['token_symbol'] = base_token['symbol']
                
                if 'current_price' in price_data:
                    return price_data
                else:
                    logger.warning("DexScreener API에서 가격 정보를 찾을 수 없습니다.")
                    return None
            else:
                logger.warning("DexScreener API에서 페어 정보를 찾을 수 없습니다.")
                return None
            
        except Exception as e:
            logger.error(f"DexScreener API 오류: {e}")
            return None
    
    def get_alkimi_price_from_coinmarketcap(self):
        """CoinMarketCap 웹사이트에서 ALKIMI 가격을 스크래핑합니다."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(self.coinmarketcap_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 가격 정보 추출
            price_data = {}
            
            # 현재 가격 추출 - 메인 가격 표시 영역에서 찾기
            main_price_elements = soup.find_all('div', class_='coin-price-performance')
            if main_price_elements:
                for element in main_price_elements:
                    # 24시간 Low/High 가격에서 현재 가격 추정
                    price_texts = element.get_text()
                    price_matches = re.findall(r'\$([\d,]+\.?\d*)', price_texts)
                    if price_matches:
                        # 첫 번째 가격을 현재 가격으로 사용 (보통 Low 가격)
                        current_price = float(price_matches[0].replace(',', ''))
                        price_data['current_price'] = current_price
                        logger.info(f"📊 메인 가격 영역에서 가격 발견: ${current_price:.4f}")
                        break
            
            # 메인 가격 영역에서 찾지 못한 경우, 전체 페이지에서 가격 찾기
            if 'current_price' not in price_data:
                all_price_elements = soup.find_all(string=re.compile(r'\$[\d,]+\.?\d*'))
                for element in all_price_elements:
                    price_text = element.strip()
                    if price_text.startswith('$'):
                        price_match = re.search(r'\$([\d,]+\.?\d*)', price_text)
                        if price_match:
                            price_str = price_match.group(1).replace(',', '')
                            try:
                                price_value = float(price_str)
                                if 0.01 <= price_value <= 10.0:  # ALKIMI 가격 범위
                                    price_data['current_price'] = price_value
                                    logger.info(f"📊 전체 페이지에서 가격 발견: ${price_value:.4f}")
                                    break
                            except ValueError:
                                continue
            
            # 24시간 변화율 추출
            change_elements = soup.find_all(string=re.compile(r'[\+\-]?\d+\.?\d*%'))
            if change_elements:
                for element in change_elements:
                    change_text = element.strip()
                    if '%' in change_text:
                        change_match = re.search(r'([\+\-]?\d+\.?\d*)%', change_text)
                        if change_match:
                            try:
                                change_value = float(change_match.group(1))
                                if -100 <= change_value <= 100:  # 합리적인 변화율 범위
                                    price_data['24h_change'] = change_value
                                    logger.info(f"📈 24시간 변화율 발견: {change_value}%")
                                    break
                            except ValueError:
                                continue
            
            # 시가총액 추출
            market_cap_elements = soup.find_all(string=re.compile(r'\$[\d,]+\.?\d*[MBK]'))
            if market_cap_elements:
                for element in market_cap_elements:
                    cap_text = element.strip()
                    if '$' in cap_text and any(unit in cap_text for unit in ['M', 'B', 'K']):
                        cap_match = re.search(r'\$([\d,]+\.?\d*)([MBK])', cap_text)
                        if cap_match:
                            try:
                                value = float(cap_match.group(1).replace(',', ''))
                                unit = cap_match.group(2)
                                if unit == 'M':
                                    price_data['market_cap'] = value * 1000000
                                elif unit == 'B':
                                    price_data['market_cap'] = value * 1000000000
                                elif unit == 'K':
                                    price_data['market_cap'] = value * 1000
                                logger.info(f"💰 시가총액 발견: ${price_data['market_cap']:,.0f}")
                                break
                            except ValueError:
                                continue
            
            # 24시간 거래량 추출
            volume_elements = soup.find_all(string=re.compile(r'\$[\d,]+\.?\d*[MBK]'))
            if volume_elements:
                for element in volume_elements:
                    vol_text = element.strip()
                    if '$' in vol_text and any(unit in vol_text for unit in ['M', 'B', 'K']):
                        vol_match = re.search(r'\$([\d,]+\.?\d*)([MBK])', vol_text)
                        if vol_match:
                            try:
                                value = float(vol_match.group(1).replace(',', ''))
                                unit = vol_match.group(2)
                                if unit == 'M':
                                    price_data['24h_volume'] = value * 1000000
                                elif unit == 'B':
                                    price_data['24h_volume'] = value * 1000000000
                                elif unit == 'K':
                                    price_data['24h_volume'] = value * 1000
                                logger.info(f"📊 24시간 거래량 발견: ${price_data['24h_volume']:,.0f}")
                                break
                            except ValueError:
                                continue
            
            # 순위 추출
            rank_elements = soup.find_all(string=re.compile(r'#\d+'))
            if rank_elements:
                for element in rank_elements:
                    rank_text = element.strip()
                    if rank_text.startswith('#'):
                        rank_match = re.search(r'#(\d+)', rank_text)
                        if rank_match:
                            try:
                                rank_value = int(rank_match.group(1))
                                if 1 <= rank_value <= 10000:  # 합리적인 순위 범위
                                    price_data['rank'] = rank_value
                                    logger.info(f"🏆 순위 발견: #{rank_value}")
                                    break
                            except ValueError:
                                continue
            
            if 'current_price' in price_data:
                logger.info(f"📊 CoinMarketCap ALKIMI 가격: ${price_data['current_price']:.4f}")
                return price_data
            else:
                logger.warning("CoinMarketCap에서 가격 정보를 찾을 수 없습니다.")
                return None
            
        except Exception as e:
            logger.error(f"CoinMarketCap 스크래핑 오류: {e}")
            return None
    
    def check_price_alert(self, price_data):
        """가격 알림 조건을 확인합니다."""
        if price_data is None or 'current_price' not in price_data:
            return None
        
        current_price = price_data['current_price']
        
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
                
                return {
                    'asset': self.asset,
                    'current_price': current_price,
                    'target_price': self.target_price,
                    'status': status,
                    'price_data': price_data
                }
        
        return None
    
    def send_price_alert(self, alert):
        """가격 알림을 전송합니다."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            price_data = alert['price_data']
            
            # 알림 메시지 생성
            if alert['status'] == "BELOW_TARGET":
                status_emoji = "🚨"
                status_text = "목표 가격 이하"
            elif alert['status'] == "ABOVE_TARGET":
                status_emoji = "📈"
                status_text = "목표 가격 초과"
            else:
                status_emoji = "🎯"
                status_text = "목표 가격 달성"
            
            # 데이터 소스에 따른 링크 결정
            if 'pair_address' in price_data:
                detail_link = f"https://dexscreener.com/sui/{price_data['pair_address']}"
                detail_text = "DexScreener 보기"
            else:
                detail_link = self.coinmarketcap_url
                detail_text = "CoinMarketCap 보기"
            
            message = f"""
{status_emoji} <b>ALKIMI 가격 알림!</b> {status_emoji}

ALKIMI 가격이 목표 가격 ${self.target_price}에 도달했습니다!

📊 <b>현재 가격:</b> <code>${price_data['current_price']:.6f}</code>
🎯 <b>목표 가격:</b> <code>${self.target_price}</code>
⏰ <b>시간:</b> {timestamp}
📉 <b>상태:</b> {status_text}

📈 <b>24시간 변화:</b> <code>{price_data.get('24h_change', 'N/A')}%</code>
💧 <b>유동성:</b> <code>${price_data.get('liquidity', 0):,.0f}</code>
📊 <b>24시간 거래량:</b> <code>${price_data.get('24h_volume', 0):,.0f}</code>
🏪 <b>거래소:</b> <code>{price_data.get('dex', 'N/A')}</code>

🔗 <b>상세 정보:</b> <a href="{detail_link}">{detail_text}</a>

⚠️  투자에 주의하세요!
"""
            
            # 텔레그램으로 전송
            success = self.notification_system.send_telegram_message(message)
            
            if success:
                logger.info(f"🚨 가격 알림 전송 성공: {alert['status']}")
                self.last_alert_time = datetime.now()
            else:
                logger.error("❌ 가격 알림 전송 실패")
                
        except Exception as e:
            logger.error(f"가격 알림 전송 중 오류: {e}")
    
    def send_daily_price_update(self, price_data):
        """일일 가격 업데이트를 전송합니다."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 데이터 소스에 따른 링크 결정
            if 'pair_address' in price_data:
                detail_link = f"https://dexscreener.com/sui/{price_data['pair_address']}"
                detail_text = "DexScreener 보기"
            else:
                detail_link = self.coinmarketcap_url
                detail_text = "CoinMarketCap 보기"
            
            message = f"""
📊 <b>ALKIMI 일일 가격 업데이트</b> 📊

⏰ <b>시간:</b> {timestamp}

💰 <b>현재 가격:</b> <code>${price_data['current_price']:.6f}</code>
📈 <b>24시간 변화:</b> <code>{price_data.get('24h_change', 'N/A')}%</code>
💧 <b>유동성:</b> <code>${price_data.get('liquidity', 0):,.0f}</code>
📊 <b>24시간 거래량:</b> <code>${price_data.get('24h_volume', 0):,.0f}</code>
🏪 <b>거래소:</b> <code>{price_data.get('dex', 'N/A')}</code>

🎯 <b>목표 가격:</b> <code>${self.target_price}</code>
📏 <b>목표까지 거리:</b> <code>${abs(price_data['current_price'] - self.target_price):.6f}</code>

🔗 <b>상세 정보:</b> <a href="{detail_link}">{detail_text}</a>
"""
            
            # 텔레그램으로 전송
            success = self.notification_system.send_telegram_message(message)
            
            if success:
                logger.info("📊 일일 가격 업데이트 전송 성공")
            else:
                logger.error("❌ 일일 가격 업데이트 전송 실패")
                
        except Exception as e:
            logger.error(f"일일 가격 업데이트 전송 중 오류: {e}")
    
    def log_price_data(self, price_data, alert=None):
        """가격 데이터를 로그에 기록합니다."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        logger.info("=" * 60)
        logger.info("📊 ALKIMI 가격 모니터링 결과")
        logger.info("=" * 60)
        logger.info(f"시간: {timestamp}")
        logger.info(f"자산: {self.asset}")
        logger.info(f"현재 가격: ${price_data.get('current_price', 'N/A')}")
        logger.info(f"24시간 변화: {price_data.get('24h_change', 'N/A')}%")
        logger.info(f"유동성: ${price_data.get('liquidity', 0):,.0f}")
        logger.info(f"24시간 거래량: ${price_data.get('24h_volume', 0):,.0f}")
        logger.info(f"거래소: {price_data.get('dex', 'N/A')}")
        logger.info(f"목표 가격: ${self.target_price}")
        
        if 'current_price' in price_data:
            price_diff = abs(price_data['current_price'] - self.target_price)
            logger.info(f"가격 차이: ${price_diff:.6f}")
        
        logger.info(f"알림 임계값: ${self.alert_threshold}")
        
        if alert:
            logger.info(f"알림 상태: {alert['status']}")
            logger.info(f"알림 시간: {timestamp}")
        else:
            logger.info("알림 상태: 알림 없음")
        
        logger.info("=" * 60)
    
    def monitor_once(self):
        """한 번의 가격 모니터링을 수행합니다."""
        try:
            logger.info("🔄 ALKIMI 가격 모니터링 시작...")
            
            # DexScreener API에서 가격 조회 (우선)
            price_data = self.get_alkimi_price_from_dexscreener()
            
            # DexScreener에서 실패한 경우 CoinMarketCap으로 백업
            if price_data is None:
                logger.info("📡 DexScreener API 실패, CoinMarketCap으로 백업 시도...")
                price_data = self.get_alkimi_price_from_coinmarketcap()
            
            if price_data is None:
                logger.error("❌ 모든 데이터 소스에서 가격 정보를 가져올 수 없습니다.")
                return
            
            # 가격 알림 확인
            alert = self.check_price_alert(price_data)
            
            # 로그 기록
            self.log_price_data(price_data, alert)
            
            # 알림 전송
            if alert:
                self.send_price_alert(alert)
            else:
                # 일일 업데이트 전송 (선택사항)
                if os.getenv("SEND_DAILY_UPDATES", "false").lower() == "true":
                    self.send_daily_price_update(price_data)
                else:
                    logger.info("📊 알림 조건을 만족하지 않습니다.")
            
        except Exception as e:
            logger.error(f"모니터링 중 오류: {e}")
    
    def start_monitoring(self, interval_seconds=60):
        """지속적인 가격 모니터링을 시작합니다."""
        logger.info(f"🚀 ALKIMI 가격 모니터링 시작")
        logger.info(f"🎯 목표 가격: ${self.target_price}")
        logger.info(f"⏰ 모니터링 간격: {interval_seconds}초")
        logger.info(f"🌐 데이터 소스: {self.coinmarketcap_url}")
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
