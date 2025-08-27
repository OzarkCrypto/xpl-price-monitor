#!/usr/bin/env python3
"""
알트 러너 찾는 모니터링 텔레그램 봇

조건:
1. 코인베이스에 상장되어있어야함
2. 코인베이스에서 거래량이 폭팔적으로 터져야함 (도지보다 많아야함)
3. 펀딩비가 음수여야함
"""

import requests
import json
import time
import logging
from datetime import datetime, timedelta
import asyncio
import aiohttp
from typing import Dict, List, Optional

# 텔레그램 설정
TELEGRAM_TOKEN = "8025422463:AAF0oCsGwWtykrGQnZvEFXP6Jq7THdGaexA"
CHAT_ID = "1339285013"

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('alt_runner_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AltRunnerMonitor:
    def __init__(self):
        self.telegram_token = TELEGRAM_TOKEN
        self.chat_id = CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.telegram_token}"
        self.monitored_tokens = set()
        self.volume_threshold = 1.1  # 도지 거래량 대비 1.1배 이상
        self.funding_rate_threshold = -0.001  # 펀딩비 -0.1% 이하
        
    async def send_telegram_message(self, message: str) -> bool:
        """텔레그램으로 메시지를 전송합니다."""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
                }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        logger.info("텔레그램 메시지 전송 성공")
                        return True
                    else:
                        logger.error(f"텔레그램 메시지 전송 실패: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"텔레그램 메시지 전송 오류: {e}")
            return False
    
    def get_doge_volume(self) -> Optional[float]:
        """도지의 24시간 거래량을 가져옵니다."""
        try:
            # CoinGecko API로 도지 거래량 조회
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': 'dogecoin',
                'vs_currencies': 'usd',
                'include_24hr_vol': 'true'
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            doge_volume = data['dogecoin']['usd_24h_vol']
            logger.info(f"도지 24시간 거래량: ${doge_volume:,.0f}")
            return doge_volume
            
        except Exception as e:
            logger.error(f"도지 거래량 조회 오류: {e}")
            return None
    
    def get_coinbase_listings(self) -> List[Dict]:
        """코인베이스에 상장된 토큰 목록을 가져옵니다."""
        try:
            # CoinGecko API로 코인베이스 상장 토큰 조회
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'volume_desc',
                'per_page': 100,
                'page': 1,
                'sparkline': False,
                'exchange': 'coinbase'
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"코인베이스 상장 토큰 {len(data)}개 조회 완료")
            return data
            
        except Exception as e:
            logger.error(f"코인베이스 상장 토큰 조회 오류: {e}")
            return []
    
    def get_funding_rate(self, symbol: str) -> Optional[float]:
        """바이낸스에서 펀딩비를 조회합니다."""
        try:
            # 바이낸스 API로 펀딩비 조회
            url = "https://fapi.binance.com/fapi/v1/fundingRate"
            params = {
                'symbol': f"{symbol}USDT",
                'limit': 1
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            if data:
                funding_rate = float(data[0]['fundingRate'])
                logger.info(f"{symbol} 펀딩비: {funding_rate:.6f}")
                return funding_rate
            return None
            
        except Exception as e:
            logger.error(f"{symbol} 펀딩비 조회 오류: {e}")
            return None
    
    def check_alt_runner_conditions(self, token: Dict, doge_volume: float) -> Dict:
        """알트 러너 조건을 확인합니다."""
        try:
            symbol = token['symbol'].upper()
            volume_24h = token.get('total_volume', 0)
            price_change_24h = token.get('price_change_percentage_24h', 0)
            
            # 조건 1: 코인베이스 상장 확인 (이미 확인됨)
            is_coinbase_listed = True
            
            # 조건 2: 도지보다 거래량이 많아야함
            volume_condition = volume_24h > (doge_volume * self.volume_threshold)
            
            # 조건 3: 펀딩비가 음수여야함 (바이낸스에서 확인)
            funding_rate = self.get_funding_rate(symbol)
            funding_condition = funding_rate is not None and funding_rate < self.funding_rate_threshold
            
            result = {
                'symbol': symbol,
                'name': token['name'],
                'volume_24h': volume_24h,
                'doge_volume': doge_volume,
                'volume_ratio': volume_24h / doge_volume if doge_volume > 0 else 0,
                'price_change_24h': price_change_24h,
                'funding_rate': funding_rate,
                'is_coinbase_listed': is_coinbase_listed,
                'volume_condition': volume_condition,
                'funding_condition': funding_condition,
                'is_alt_runner': is_coinbase_listed and volume_condition and funding_condition
            }
            
            return result
            
        except Exception as e:
            logger.error(f"{token.get('symbol', 'Unknown')} 조건 확인 오류: {e}")
            return None
    
    async def monitor_alt_runners(self):
        """알트 러너를 모니터링합니다."""
        logger.info("🚀 알트 러너 모니터링 시작")
        
        # 도지 거래량 조회
        doge_volume = self.get_doge_volume()
        if not doge_volume:
            logger.error("도지 거래량을 가져올 수 없어 모니터링을 중단합니다.")
            return
        
        # 코인베이스 상장 토큰 조회
        coinbase_tokens = self.get_coinbase_listings()
        if not coinbase_tokens:
            logger.error("코인베이스 상장 토큰을 가져올 수 없습니다.")
            return
        
        # 알트 러너 조건 확인
        alt_runners = []
        for token in coinbase_tokens[:50]:  # 상위 50개만 확인 (API 제한 고려)
            try:
                result = self.check_alt_runner_conditions(token, doge_volume)
                if result and result['is_alt_runner']:
                    alt_runners.append(result)
                    logger.info(f"🎯 알트 러너 발견: {result['symbol']}")
                
                # API 제한 고려하여 잠시 대기
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"토큰 {token.get('symbol', 'Unknown')} 확인 오류: {e}")
                continue
        
        # 결과 요약 및 알림
        if alt_runners:
            await self.send_alt_runner_alert(alt_runners, doge_volume)
        else:
            logger.info("현재 알트 러너 조건을 만족하는 토큰이 없습니다.")
    
    async def send_alt_runner_alert(self, alt_runners: List[Dict], doge_volume: float):
        """알트 러너 발견 알림을 전송합니다."""
        message = f"🚨 <b>알트 러너 발견!</b> 🚨\n\n"
        message += f"📊 <b>도지 24시간 거래량:</b> ${doge_volume:,.0f}\n"
        message += f"🎯 <b>발견된 알트 러너:</b> {len(alt_runners)}개\n\n"
        
        for i, runner in enumerate(alt_runners, 1):
            message += f"<b>{i}. {runner['symbol']} ({runner['name']})</b>\n"
            message += f"   💰 24시간 거래량: ${runner['volume_24h']:,.0f}\n"
            message += f"   📈 도지 대비: {runner['volume_ratio']:.2f}배\n"
            message += f"   📊 24시간 변화: {runner['price_change_24h']:.2f}%\n"
            message += f"   💸 펀딩비: {runner['funding_rate']:.6f}\n\n"
        
        message += f"⏰ <i>발견 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        
        await self.send_telegram_message(message)
    
    async def run_monitoring_loop(self, interval_minutes: int = 30):
        """모니터링 루프를 실행합니다."""
        logger.info(f"🔄 모니터링 루프 시작 (간격: {interval_minutes}분)")
        
        while True:
            try:
                await self.monitor_alt_runners()
                logger.info(f"✅ 모니터링 완료. {interval_minutes}분 후 재실행...")
                await asyncio.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("🛑 사용자에 의해 모니터링이 중단되었습니다.")
                break
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                await asyncio.sleep(60)  # 오류 발생 시 1분 후 재시도

async def main():
    """메인 함수"""
    monitor = AltRunnerMonitor()
    
    # 즉시 한 번 실행
    await monitor.monitor_alt_runners()
    
    # 모니터링 루프 시작 (30분 간격)
    await monitor.run_monitoring_loop(30)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("프로그램이 종료되었습니다.")
    except Exception as e:
        logger.error(f"프로그램 실행 오류: {e}") 