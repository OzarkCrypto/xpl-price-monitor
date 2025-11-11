#!/usr/bin/env python3
"""
Hyperliquid와 Binance 간 가격 갭 모니터링 서버
실시간 가격 데이터 수집 및 갭 계산
"""

import asyncio
import aiohttp
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass, asdict
import requests

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PriceData:
    """가격 데이터"""
    exchange: str
    symbol: str
    price: float
    timestamp: float
    volume_24h: Optional[float] = None
    change_24h: Optional[float] = None

@dataclass
class GapData:
    """가격 갭 데이터"""
    symbol: str
    hyperliquid_price: float
    binance_price: float
    gap: float
    gap_percentage: float
    timestamp: float
    opportunity: str  # "buy_on_hyperliquid" or "buy_on_binance"

class HyperliquidBinanceGapMonitor:
    """Hyperliquid와 Binance 간 가격 갭 모니터"""
    
    def __init__(self):
        self.hyperliquid_base_url = "https://api.hyperliquid.xyz"
        self.binance_base_url = "https://fapi.binance.com"
        self.price_data: Dict[str, Dict[str, PriceData]] = {}  # {symbol: {exchange: PriceData}}
        self.gap_history: List[GapData] = []
        
        # API Rate Limiting
        self.binance_last_call_time = 0.0
        self.binance_min_interval = 1.0  # 1초에 한번만 호출
        self.binance_cache: Dict[str, Tuple[PriceData, float]] = {}  # {symbol: (data, timestamp)}
        self.binance_cache_ttl = 2.0  # 캐시 유효 시간 (초)
        
    async def fetch_hyperliquid_price(self, symbol: str) -> Optional[PriceData]:
        """Hyperliquid에서 가격 데이터 가져오기"""
        try:
            async with aiohttp.ClientSession() as session:
                # Hyperliquid API - 가격 정보 가져오기
                url = f"{self.hyperliquid_base_url}/info"
                
                # Hyperliquid는 POST 요청을 사용
                # allMids 타입으로 모든 심볼의 중간 가격 가져오기
                price_payload = {
                    "type": "allMids"
                }
                
                async with session.post(url, json=price_payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 데이터 형태에 따라 처리
                        if isinstance(data, dict):
                            # {symbol: price} 형태
                            # 심볼 매핑 (예: MONUSDT -> MON)
                            base_symbol = symbol.replace('USDT', '').replace('USD', '')
                            if base_symbol in data:
                                price = float(data[base_symbol])
                                return PriceData(
                                    exchange="hyperliquid",
                                    symbol=symbol,
                                    price=price,
                                    timestamp=time.time()
                                )
                            # 전체 심볼 검색
                            for key, value in data.items():
                                if key.upper() == base_symbol.upper() or key.upper() == symbol.upper():
                                    price = float(value)
                                    return PriceData(
                                        exchange="hyperliquid",
                                        symbol=symbol,
                                        price=price,
                                        timestamp=time.time()
                                    )
                        elif isinstance(data, list):
                            # 리스트 형태: [{"coin": "BTC", "mid": 50000}, ...]
                            base_symbol = symbol.replace('USDT', '').replace('USD', '')
                            for item in data:
                                if isinstance(item, dict):
                                    coin = item.get('coin', '').upper()
                                    if coin == base_symbol.upper() or coin == symbol.upper():
                                        price = float(item.get('mid', 0))
                                        if price > 0:
                                            return PriceData(
                                                exchange="hyperliquid",
                                                symbol=symbol,
                                                price=price,
                                                timestamp=time.time()
                                            )
                
                # 대체 방법: 특정 심볼의 가격 직접 조회
                # Hyperliquid는 때때로 개별 심볼 조회를 지원
                logger.warning(f"Hyperliquid에서 {symbol} 가격을 찾을 수 없습니다. allMids 응답: {data}")
                
        except aiohttp.ClientError as e:
            logger.error(f"Hyperliquid API 연결 오류 ({symbol}): {e}")
        except Exception as e:
            logger.error(f"Hyperliquid 가격 데이터 수집 실패 ({symbol}): {e}")
        
        return None
    
    async def fetch_binance_price(self, symbol: str) -> Optional[PriceData]:
        """Binance에서 가격 데이터 가져오기 (Rate Limited: 1초에 한번)"""
        current_time = time.time()
        
        # 캐시 확인
        if symbol in self.binance_cache:
            cached_data, cache_time = self.binance_cache[symbol]
            if current_time - cache_time < self.binance_cache_ttl:
                logger.debug(f"Binance 캐시 사용: {symbol}")
                return cached_data
        
        # Rate Limiting: 마지막 호출로부터 1초 이상 경과했는지 확인
        time_since_last_call = current_time - self.binance_last_call_time
        if time_since_last_call < self.binance_min_interval:
            wait_time = self.binance_min_interval - time_since_last_call
            logger.debug(f"Binance Rate Limit 대기: {wait_time:.2f}초")
            await asyncio.sleep(wait_time)
        
        try:
            # Binance 선물 API
            url = f"{self.binance_base_url}/fapi/v1/ticker/24hr"
            params = {"symbol": symbol}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    self.binance_last_call_time = time.time()
                    
                    if response.status == 200:
                        data = await response.json()
                        price_data = PriceData(
                            exchange="binance",
                            symbol=symbol,
                            price=float(data.get('lastPrice', 0)),
                            timestamp=time.time(),
                            volume_24h=float(data.get('quoteVolume', 0)),
                            change_24h=float(data.get('priceChangePercent', 0))
                        )
                        # 캐시에 저장
                        self.binance_cache[symbol] = (price_data, time.time())
                        return price_data
                    elif response.status == 429:
                        # Too Many Requests
                        logger.warning(f"Binance API Rate Limit 초과 (429). 대기 후 재시도...")
                        retry_after = int(response.headers.get('Retry-After', 5))
                        await asyncio.sleep(retry_after)
                        # 캐시된 데이터가 있으면 반환
                        if symbol in self.binance_cache:
                            return self.binance_cache[symbol][0]
                        return None
                    else:
                        logger.error(f"Binance API 오류: HTTP {response.status}")
                        # 캐시된 데이터가 있으면 반환
                        if symbol in self.binance_cache:
                            logger.info(f"Binance 캐시된 데이터 사용: {symbol}")
                            return self.binance_cache[symbol][0]
                        return None
        except asyncio.TimeoutError:
            logger.error(f"Binance API 타임아웃 ({symbol})")
            # 캐시된 데이터가 있으면 반환
            if symbol in self.binance_cache:
                logger.info(f"Binance 캐시된 데이터 사용 (타임아웃): {symbol}")
                return self.binance_cache[symbol][0]
            return None
        except Exception as e:
            logger.error(f"Binance 가격 데이터 수집 실패 ({symbol}): {e}")
            # 캐시된 데이터가 있으면 반환
            if symbol in self.binance_cache:
                logger.info(f"Binance 캐시된 데이터 사용 (오류): {symbol}")
                return self.binance_cache[symbol][0]
            return None
    
    async def fetch_prices(self, symbol: str) -> Dict[str, Optional[PriceData]]:
        """두 거래소에서 가격 데이터 수집"""
        hyperliquid_price, binance_price = await asyncio.gather(
            self.fetch_hyperliquid_price(symbol),
            self.fetch_binance_price(symbol),
            return_exceptions=True
        )
        
        # 예외 처리
        if isinstance(hyperliquid_price, Exception):
            logger.error(f"Hyperliquid 오류: {hyperliquid_price}")
            hyperliquid_price = None
        if isinstance(binance_price, Exception):
            logger.error(f"Binance 오류: {binance_price}")
            binance_price = None
        
        return {
            "hyperliquid": hyperliquid_price,
            "binance": binance_price
        }
    
    def calculate_gap(self, symbol: str, prices: Dict[str, Optional[PriceData]]) -> Optional[GapData]:
        """가격 갭 계산"""
        hyperliquid_price = prices.get("hyperliquid")
        binance_price = prices.get("binance")
        
        if not hyperliquid_price or not binance_price:
            return None
        
        gap = binance_price.price - hyperliquid_price.price
        gap_percentage = (gap / hyperliquid_price.price) * 100 if hyperliquid_price.price > 0 else 0
        
        # 차익거래 기회 판단
        if gap > 0:
            opportunity = "buy_on_hyperliquid"  # Hyperliquid가 더 저렴
        else:
            opportunity = "buy_on_binance"  # Binance가 더 저렴
        
        gap_data = GapData(
            symbol=symbol,
            hyperliquid_price=hyperliquid_price.price,
            binance_price=binance_price.price,
            gap=gap,
            gap_percentage=gap_percentage,
            timestamp=time.time(),
            opportunity=opportunity
        )
        
        # 히스토리 저장 (최근 24시간 데이터만 유지)
        self.gap_history.append(gap_data)
        
        # 24시간 이전 데이터 삭제
        current_time = time.time()
        twenty_four_hours_ago = current_time - (24 * 60 * 60)  # 24시간 = 86400초
        self.gap_history = [
            g for g in self.gap_history 
            if g.timestamp >= twenty_four_hours_ago
        ]
        
        return gap_data
    
    async def monitor_symbol(self, symbol: str) -> Optional[GapData]:
        """심볼 모니터링"""
        logger.info(f"{symbol} 가격 데이터 수집 중...")
        prices = await self.fetch_prices(symbol)
        
        # 가격 데이터 저장
        if symbol not in self.price_data:
            self.price_data[symbol] = {}
        
        for exchange, price_data in prices.items():
            if price_data:
                self.price_data[symbol][exchange] = price_data
        
        # 갭 계산
        gap_data = self.calculate_gap(symbol, prices)
        
        if gap_data:
            logger.info(f"{symbol} 갭: {gap_data.gap_percentage:.2f}% "
                       f"(Hyperliquid: ${gap_data.hyperliquid_price:.4f}, "
                       f"Binance: ${gap_data.binance_price:.4f})")
        
        return gap_data
    
    def get_statistics(self, symbol: str) -> Dict:
        """통계 정보 반환 (최근 24시간 데이터)"""
        current_time = time.time()
        twenty_four_hours_ago = current_time - (24 * 60 * 60)  # 24시간 = 86400초
        
        # 최근 24시간 데이터만 필터링
        symbol_gaps = [
            g for g in self.gap_history 
            if g.symbol == symbol and g.timestamp >= twenty_four_hours_ago
        ]
        
        if not symbol_gaps:
            return {
                'current_gap': 0,
                'current_gap_percentage': 0,
                'avg_gap': 0,
                'max_gap': 0,
                'min_gap': 0,
                'avg_gap_percentage': 0,
                'total_samples': 0
            }
        
        current_gap = symbol_gaps[-1]
        gaps = [g.gap for g in symbol_gaps]
        gap_percentages = [g.gap_percentage for g in symbol_gaps]
        
        return {
            'current_gap': current_gap.gap,
            'current_gap_percentage': current_gap.gap_percentage,
            'avg_gap': sum(gaps) / len(gaps) if gaps else 0,
            'max_gap': max(gaps) if gaps else 0,
            'min_gap': min(gaps) if gaps else 0,
            'avg_gap_percentage': sum(gap_percentages) / len(gap_percentages) if gap_percentages else 0,
            'total_samples': len(symbol_gaps)
        }

# 웹 서버 (Flask 사용)
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import threading

# 템플릿 경로 설정 (Vercel 환경 고려)
template_dir = None
possible_paths = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'),
    'templates',
    os.path.join(os.getcwd(), 'templates'),
    '/var/task/templates',  # Vercel Lambda 경로
]

for path in possible_paths:
    if os.path.exists(path):
        template_dir = path
        break

if template_dir is None:
    # 기본값 사용
    template_dir = 'templates'

app = Flask(__name__, template_folder=template_dir)
CORS(app)

# 전역 모니터 인스턴스
monitor = HyperliquidBinanceGapMonitor()
latest_gap_data: Dict[str, GapData] = {}
monitoring_active = False

def background_monitor(symbol: str = "MONUSDT"):
    """백그라운드 모니터링 스레드"""
    global latest_gap_data, monitoring_active
    
    # Vercel 환경에서는 실행하지 않음
    if os.environ.get('VERCEL') == '1' or os.environ.get('DISABLE_BACKGROUND_MONITOR') == '1':
        return
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    monitoring_active = True
    
    while monitoring_active:
        try:
            gap_data = loop.run_until_complete(monitor.monitor_symbol(symbol))
            if gap_data:
                latest_gap_data[symbol] = gap_data
            time.sleep(3)  # 3초마다 업데이트 (Binance는 1초 제한이므로 충분)
        except Exception as e:
            logger.error(f"모니터링 오류: {e}")
            time.sleep(5)  # 오류 시 5초 대기

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('hyperliquid_binance_gap_dashboard.html')

@app.route('/api/gap/<symbol>')
def get_gap(symbol: str):
    """가격 갭 데이터 API"""
    # Vercel 환경에서는 요청 시마다 데이터를 가져옴
    if os.environ.get('VERCEL') == '1' or os.environ.get('DISABLE_BACKGROUND_MONITOR') == '1':
        # 서버리스 환경: 요청 시마다 실시간 데이터 가져오기
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        gap_data = loop.run_until_complete(monitor.monitor_symbol(symbol))
        loop.close()
        
        if gap_data:
            stats = monitor.get_statistics(symbol)
            return jsonify({
                'gap': asdict(gap_data),
                'statistics': stats,
                'timestamp': time.time()
            })
        else:
            return jsonify({'error': 'Failed to fetch data'}), 500
    
    # 일반 환경: 캐시된 데이터 사용
    if symbol in latest_gap_data:
        gap_data = latest_gap_data[symbol]
        stats = monitor.get_statistics(symbol)
        
        return jsonify({
            'gap': asdict(gap_data),
            'statistics': stats,
            'timestamp': time.time()
        })
    else:
        return jsonify({'error': 'No data available'}), 404

@app.route('/api/gap/<symbol>/history')
def get_gap_history(symbol: str):
    """가격 갭 히스토리 API (최근 24시간 데이터)"""
    current_time = time.time()
    twenty_four_hours_ago = current_time - (24 * 60 * 60)  # 24시간 = 86400초
    
    # 해당 심볼의 최근 24시간 데이터만 필터링
    symbol_gaps = [
        g for g in monitor.gap_history 
        if g.symbol == symbol and g.timestamp >= twenty_four_hours_ago
    ]
    
    # 시간순으로 정렬 (오래된 것부터)
    symbol_gaps.sort(key=lambda x: x.timestamp)
    
    return jsonify([asdict(g) for g in symbol_gaps])

@app.route('/api/statistics/<symbol>')
def get_statistics(symbol: str):
    """통계 API"""
    stats = monitor.get_statistics(symbol)
    return jsonify(stats)

@app.route('/api/start/<symbol>')
def start_monitoring(symbol: str):
    """모니터링 시작"""
    global monitoring_active
    
    # Vercel 환경에서는 백그라운드 스레드 시작하지 않음
    if os.environ.get('VERCEL') == '1' or os.environ.get('DISABLE_BACKGROUND_MONITOR') == '1':
        return jsonify({
            'status': 'serverless_mode',
            'symbol': symbol,
            'message': 'Vercel serverless mode: data fetched on request'
        })
    
    if not monitoring_active:
        monitor_thread = threading.Thread(target=background_monitor, args=(symbol,), daemon=True)
        monitor_thread.start()
        return jsonify({'status': 'started', 'symbol': symbol})
    else:
        return jsonify({'status': 'already_running', 'symbol': symbol})

if __name__ == '__main__':
    # Vercel 환경이 아닐 때만 백그라운드 모니터링 시작
    if os.environ.get('DISABLE_BACKGROUND_MONITOR') != '1':
        # 기본 모니터링 시작 (MONUSDT)
        monitor_thread = threading.Thread(target=background_monitor, args=("MONUSDT",), daemon=True)
        monitor_thread.start()
    
    # Flask 서버 시작
    # 환경 변수에서 포트 가져오기 (클라우드 배포용)
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)

