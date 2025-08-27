from flask import Flask, request, jsonify
import requests
import json
import time
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class XPLPriceMonitor:
    def __init__(self):
        self.binance_price = None
        self.hyperliquid_price = None
        self.last_update = None
        
    def get_binance_xpl_price(self):
        """Binance에서 XPL 가격을 가져옵니다."""
        try:
            # Binance Futures API
            url = "https://fapi.binance.com/fapi/v1/ticker/price"
            params = {'symbol': 'XPLUSDT'}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            price = float(data['price'])
            
            logger.info(f"Binance XPL 가격: ${price:.6f}")
            return price
            
        except Exception as e:
            logger.error(f"Binance API 오류: {e}")
            return None
    
    def get_hyperliquid_xpl_price(self):
        """Hyperliquid에서 XPL 가격을 가져옵니다."""
        try:
            # Hyperliquid API
            url = "https://api.hyperliquid.xyz/info"
            payload = {
                "type": "allMids"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # XPL 심볼 찾기 (데이터는 딕셔너리 형태)
            if 'XPL' in data:
                xpl_price = float(data['XPL'])
                logger.info(f"Hyperliquid XPL 가격: ${xpl_price:.6f}")
                return xpl_price
            else:
                logger.warning("Hyperliquid에서 XPL 가격을 찾을 수 없습니다.")
                return None
                
        except Exception as e:
            logger.error(f"Hyperliquid API 오류: {e}")
            return None
    
    def calculate_gap(self, binance_price, hyperliquid_price):
        """가격 갭을 계산합니다."""
        if binance_price is None or hyperliquid_price is None:
            return {
                'absolute': None,
                'percentage': None,
                'status': 'unknown'
            }
        
        absolute_gap = abs(hyperliquid_price - binance_price)
        percentage_gap = (absolute_gap / binance_price) * 100
        
        # 갭 상태 결정
        if percentage_gap < 1:
            status = 'low'
        elif percentage_gap < 5:
            status = 'medium'
        else:
            status = 'high'
        
        return {
            'absolute': round(absolute_gap, 6),
            'percentage': round(percentage_gap, 2),
            'status': status
        }
    
    def update_prices(self):
        """가격을 업데이트합니다."""
        logger.info("가격 업데이트 시작...")
        
        self.binance_price = self.get_binance_xpl_price()
        self.hyperliquid_price = self.get_hyperliquid_xpl_price()
        self.last_update = datetime.now()
        
        logger.info("가격 업데이트 완료")
    
    def get_price_data(self):
        """현재 가격 데이터를 반환합니다."""
        gap = self.calculate_gap(self.binance_price, self.hyperliquid_price)
        
        # 현재 시간과 마지막 업데이트 시간의 차이 계산
        current_time = datetime.now()
        seconds_ago = None
        if self.last_update:
            time_diff = current_time - self.last_update
            seconds_ago = int(time_diff.total_seconds())
        
        return {
            'binance': {
                'price': self.binance_price,
                'exchange': 'Binance Futures',
                'url': 'https://www.binance.com/en/futures/XPLUSDT'
            },
            'hyperliquid': {
                'price': self.hyperliquid_price,
                'exchange': 'Hyperliquid',
                'url': 'https://app.hyperliquid.xyz/trade'
            },
            'gap': gap,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'seconds_ago': seconds_ago,
            'timestamp': current_time.isoformat()
        }

# 전역 모니터 인스턴스
monitor = XPLPriceMonitor()

@app.route('/')
def index():
    """메인 페이지"""
    # HTML 템플릿 반환
    html_template = '''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>XPL 가격 모니터</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .card { border: none; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
            .price-card { background: linear-gradient(45deg, #ff6b6b, #ee5a24); color: white; }
            .price-card.hyperliquid { background: linear-gradient(45deg, #4834d4, #686de0); }
            .gap-card { background: linear-gradient(45deg, #00b894, #00cec9); color: white; }
            .status-low { background: linear-gradient(45deg, #00b894, #00cec9) !important; }
            .status-medium { background: linear-gradient(45deg, #fdcb6e, #e17055) !important; }
            .status-high { background: linear-gradient(45deg, #e17055, #d63031) !important; }
            .btn-refresh { background: linear-gradient(45deg, #6c5ce7, #a29bfe); border: none; }
            .last-update { color: #636e72; font-size: 0.9rem; }
        </style>
    </head>
    <body>
        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-lg-10">
                    <div class="text-center mb-5">
                        <h1 class="display-4 text-white mb-3">🚀 XPL 가격 모니터</h1>
                        <p class="lead text-white-50">Binance vs Hyperliquid 실시간 가격 비교</p>
                    </div>
                    
                    <div class="row mb-4">
                        <div class="col-md-6 mb-3">
                            <div class="card price-card h-100">
                                <div class="card-body text-center">
                                    <h5 class="card-title">Binance Futures</h5>
                                    <div class="display-6 mb-3" id="binancePrice">-</div>
                                    <a href="https://www.binance.com/en/futures/XPLUSDT" target="_blank" class="btn btn-outline-light btn-sm">거래소 방문</a>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6 mb-3">
                            <div class="card price-card hyperliquid h-100">
                                <div class="card-body text-center">
                                    <h5 class="card-title">Hyperliquid</h5>
                                    <div class="display-6 mb-3" id="hyperliquidPrice">-</div>
                                    <a href="https://app.hyperliquid.xyz/trade" target="_blank" class="btn btn-outline-light btn-sm">거래소 방문</a>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row mb-4">
                        <div class="col-md-6 mb-3">
                            <div class="card gap-card h-100">
                                <div class="card-body text-center">
                                    <h5 class="card-title">절대 갭</h5>
                                    <div class="display-6 mb-3" id="absoluteGap">-</div>
                                    <small class="text-white-50">USD 차이</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6 mb-3">
                            <div class="card gap-card h-100">
                                <div class="card-body text-center">
                                    <h5 class="card-title">상대 갭</h5>
                                    <div class="display-6 mb-3" id="relativeGap">-</div>
                                    <small class="text-white-50">백분율 차이</small>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row mb-4">
                        <div class="col-12">
                            <div class="card">
                                <div class="card-body text-center">
                                    <h5 class="card-title">갭 상태</h5>
                                    <div class="display-6 mb-3" id="gapStatus">-</div>
                                    <div id="gapDescription" class="text-muted">-</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="text-center mb-4">
                        <button class="btn btn-refresh btn-lg text-white" onclick="refreshPrices()">
                            🔄 즉시 업데이트
                        </button>
                    </div>
                    
                    <div class="text-center mt-4">
                        <div class="row">
                            <div class="col-md-6">
                                <p class="last-update">
                                    마지막 업데이트: <span id="lastUpdate">-</span>
                                </p>
                            </div>
                            <div class="col-md-6">
                                <p class="last-update">
                                    <span id="secondsAgo">-</span>초 전
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            let updateInterval;
            
            function updatePrices() {
                fetch('/api/prices')
                    .then(response => response.json())
                    .then(data => {
                        // Binance 가격
                        if (data.binance.price !== null) {
                            document.getElementById('binancePrice').textContent = '$' + data.binance.price.toFixed(6);
                        } else {
                            document.getElementById('binancePrice').textContent = '오류';
                        }
                        
                        // Hyperliquid 가격
                        if (data.hyperliquid.price !== null) {
                            document.getElementById('hyperliquidPrice').textContent = '$' + data.hyperliquid.price.toFixed(6);
                        } else {
                            document.getElementById('hyperliquidPrice').textContent = '오류';
                        }
                        
                        // 갭 정보
                        if (data.gap.absolute !== null) {
                            document.getElementById('absoluteGap').textContent = '$' + data.gap.absolute.toFixed(6);
                            document.getElementById('relativeGap').textContent = data.gap.percentage + '%';
                            
                            // 갭 상태
                            const statusElement = document.getElementById('gapStatus');
                            const descriptionElement = document.getElementById('gapDescription');
                            
                            if (data.gap.status === 'low') {
                                statusElement.textContent = '🟢 낮음';
                                descriptionElement.textContent = '효율적인 시장';
                            } else if (data.gap.status === 'medium') {
                                statusElement.textContent = '🟡 보통';
                                descriptionElement.textContent = '차익거래 기회 가능';
                            } else if (data.gap.status === 'high') {
                                statusElement.textContent = '🔴 높음';
                                descriptionElement.textContent = '시장 비효율성';
                            }
                        } else {
                            document.getElementById('absoluteGap').textContent = '-';
                            document.getElementById('relativeGap').textContent = '-';
                            document.getElementById('gapStatus').textContent = '-';
                            document.getElementById('gapDescription').textContent = '-';
                        }
                        
                        // 마지막 업데이트 시간
                        if (data.last_update) {
                            const updateTime = new Date(data.last_update);
                            document.getElementById('lastUpdate').textContent = updateTime.toLocaleString('ko-KR');
                        }
                        
                        // 몇 초 전인지 표시
                        if (data.seconds_ago !== null && data.seconds_ago !== undefined) {
                            document.getElementById('secondsAgo').textContent = data.seconds_ago;
                        } else {
                            document.getElementById('secondsAgo').textContent = '-';
                        }
                    })
                    .catch(error => {
                        console.error('가격 업데이트 오류:', error);
                        showError('가격 업데이트 중 오류가 발생했습니다.');
                    });
            }
            
            function refreshPrices() {
                fetch('/api/update')
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            updatePrices();
                        }
                    })
                    .catch(error => {
                        console.error('수동 업데이트 오류:', error);
                        showError('수동 업데이트 중 오류가 발생했습니다.');
                    });
            }
            
            function showError(message) {
                // 에러 메시지 표시 (간단한 구현)
                console.error(message);
            }
            
            // 페이지 로드 시 가격 업데이트
            document.addEventListener('DOMContentLoaded', function() {
                updatePrices();
                
                // 30초마다 자동 업데이트
                updateInterval = setInterval(updatePrices, 30000);
            });
            
            // 페이지 언로드 시 인터벌 정리
            window.addEventListener('beforeunload', function() {
                if (updateInterval) {
                    clearInterval(updateInterval);
                }
            });
        </script>
    </body>
    </html>
    '''
    return html_template

@app.route('/api/prices')
def get_prices():
    """현재 가격 데이터를 반환합니다."""
    return jsonify(monitor.get_price_data())

@app.route('/api/update')
def update_prices():
    """가격을 강제로 업데이트합니다."""
    monitor.update_prices()
    return jsonify({'success': True, 'message': '가격이 업데이트되었습니다.'})

if __name__ == '__main__':
    app.run(debug=False)
