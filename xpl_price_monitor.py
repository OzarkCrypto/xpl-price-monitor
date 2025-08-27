#!/usr/bin/env python3
"""
XPL 가격 모니터 - Binance vs Hyperliquid
두 거래소의 XPL 가격을 비교하고 갭을 실시간으로 보여줍니다.
"""

import requests
import json
import time
from datetime import datetime
from flask import Flask, render_template, jsonify
import threading
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
        self.update_interval = 30  # 30초마다 업데이트
        
    def get_binance_xpl_price(self):
        """Binance에서 XPL 가격을 가져옵니다."""
        try:
            # Binance Futures API
            url = "https://fapi.binance.com/fapi/v1/ticker/price"
            params = {'symbol': 'XPLUSDT'}
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # 응답이 리스트인 경우 XPLUSDT 찾기
            if isinstance(data, list):
                for item in data:
                    if item.get('symbol') == 'XPLUSDT':
                        price = float(item['price'])
                        logger.info(f"Binance XPL 가격: ${price:.6f}")
                        return price
                logger.warning("Binance에서 XPLUSDT를 찾을 수 없습니다.")
                return None
            # 응답이 단일 객체인 경우
            elif isinstance(data, dict) and 'price' in data:
                price = float(data['price'])
                logger.info(f"Binance XPL 가격: ${price:.6f}")
                return price
            else:
                logger.warning(f"Binance API 응답 형식 오류: {data}")
                return None
            
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
    
    def calculate_gap(self, price1, price2):
        """두 가격 간의 갭을 계산합니다."""
        if price1 is None or price2 is None:
            return None
        
        gap = abs(price1 - price2)
        gap_percentage = (gap / min(price1, price2)) * 100
        
        return {
            'absolute': gap,
            'percentage': gap_percentage
        }
    
    def update_prices(self):
        """가격을 업데이트합니다."""
        logger.info("가격 업데이트 시작...")
        
        binance_price = self.get_binance_xpl_price()
        hyperliquid_price = self.get_hyperliquid_xpl_price()
        
        if binance_price is not None:
            self.binance_price = binance_price
        
        if hyperliquid_price is not None:
            self.hyperliquid_price = hyperliquid_price
        
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
    
    def start_monitoring(self):
        """백그라운드에서 가격 모니터링을 시작합니다."""
        def monitor_loop():
            while True:
                try:
                    self.update_prices()
                    time.sleep(self.update_interval)
                except Exception as e:
                    logger.error(f"모니터링 루프 오류: {e}")
                    time.sleep(self.update_interval)
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        logger.info("가격 모니터링 시작됨")

# 전역 모니터 인스턴스
price_monitor = XPLPriceMonitor()

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/api/prices')
def get_prices():
    """가격 데이터 API 엔드포인트"""
    return jsonify(price_monitor.get_price_data())

@app.route('/api/update')
def force_update():
    """강제 가격 업데이트"""
    price_monitor.update_prices()
    return jsonify({'status': 'success', 'message': '가격이 업데이트되었습니다.'})

def create_templates():
    """HTML 템플릿을 생성합니다."""
    import os
    
    templates_dir = 'templates'
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # index.html 템플릿
    index_html = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XPL 가격 모니터 - Binance vs Hyperliquid</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .price-card {
            transition: all 0.3s ease;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .price-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
        }
        .gap-indicator {
            font-size: 2rem;
            font-weight: bold;
        }
        .gap-small { color: #28a745; }
        .gap-medium { color: #ffc107; }
        .gap-large { color: #dc3545; }
        .price-value {
            font-size: 2.5rem;
            font-weight: bold;
        }
        .exchange-name {
            font-size: 1.2rem;
            color: #6c757d;
        }
        .last-update {
            font-size: 0.9rem;
            color: #6c757d;
        }
        .refresh-btn {
            border-radius: 50px;
            padding: 10px 25px;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        .status-live { background-color: #28a745; }
        .status-offline { background-color: #dc3545; }
    </style>
</head>
<body class="bg-light">
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-lg-10">
                <!-- 헤더 -->
                <div class="text-center mb-5">
                    <h1 class="display-4 fw-bold text-primary mb-3">
                        <i class="fas fa-chart-line me-3"></i>XPL 가격 모니터
                    </h1>
                    <p class="lead text-muted">
                        Binance Futures와 Hyperliquid의 XPL 가격을 실시간으로 비교하고 갭을 분석합니다
                    </p>
                    <div class="d-flex justify-content-center align-items-center gap-3">
                        <span class="status-indicator status-live"></span>
                        <span class="text-success fw-bold">실시간 모니터링</span>
                        <button id="refreshBtn" class="btn btn-outline-primary refresh-btn ms-3">
                            <i class="fas fa-sync-alt me-2"></i>수동 새로고침
                        </button>
                    </div>
                </div>

                <!-- 가격 카드들 -->
                <div class="row g-4 mb-4">
                    <!-- Binance -->
                    <div class="col-md-6">
                        <div class="card price-card h-100 border-0">
                            <div class="card-body text-center p-4">
                                <div class="mb-3">
                                    <i class="fab fa-bitcoin fa-3x text-warning"></i>
                                </div>
                                <h5 class="exchange-name mb-2">Binance Futures</h5>
                                <div class="price-value text-primary mb-2" id="binancePrice">
                                    <i class="fas fa-spinner fa-spin"></i>
                                </div>
                                <div class="mb-3">
                                    <a href="https://www.binance.com/en/futures/XPLUSDT" 
                                       target="_blank" class="btn btn-sm btn-outline-primary">
                                        <i class="fas fa-external-link-alt me-2"></i>거래소 방문
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Hyperliquid -->
                    <div class="col-md-6">
                        <div class="card price-card h-100 border-0">
                            <div class="card-body text-center p-4">
                                <div class="mb-3">
                                    <i class="fas fa-rocket fa-3x text-info"></i>
                                </div>
                                <h5 class="exchange-name mb-2">Hyperliquid</h5>
                                <div class="price-value text-info mb-2" id="hyperliquidPrice">
                                    <i class="fas fa-spinner fa-spin"></i>
                                </div>
                                <div class="mb-3">
                                    <a href="https://app.hyperliquid.xyz/trade" 
                                       target="_blank" class="btn btn-sm btn-outline-info">
                                        <i class="fas fa-external-link-alt me-2"></i>거래소 방문
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 갭 분석 -->
                <div class="row justify-content-center">
                    <div class="col-lg-8">
                        <div class="card price-card border-0">
                            <div class="card-body text-center p-4">
                                <h4 class="mb-4">
                                    <i class="fas fa-balance-scale me-3 text-secondary"></i>가격 갭 분석
                                </h4>
                                
                                <div class="row g-4">
                                    <div class="col-md-4">
                                        <div class="text-center">
                                            <h6 class="text-muted mb-2">절대 갭</h6>
                                            <div class="gap-indicator text-primary" id="absoluteGap">
                                                <i class="fas fa-spinner fa-spin"></i>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="text-center">
                                            <h6 class="text-muted mb-2">상대 갭</h6>
                                            <div class="gap-indicator text-warning" id="percentageGap">
                                                <i class="fas fa-spinner fa-spin"></i>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="text-center">
                                            <h6 class="text-muted mb-2">갭 상태</h6>
                                            <div class="gap-indicator" id="gapStatus">
                                                <i class="fas fa-spinner fa-spin"></i>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div class="mt-4">
                                    <div class="alert alert-info" role="alert">
                                        <i class="fas fa-info-circle me-2"></i>
                                        <strong>갭 분석:</strong> 
                                        <span id="gapAnalysis">데이터 로딩 중...</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 마지막 업데이트 -->
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
        
        // 페이지 로드 시 가격 데이터 가져오기
        document.addEventListener('DOMContentLoaded', function() {
            loadPrices();
            // 30초마다 자동 업데이트
            updateInterval = setInterval(loadPrices, 30000);
        });

        // 수동 새로고침 버튼
        document.getElementById('refreshBtn').addEventListener('click', function() {
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>업데이트 중...';
            
            loadPrices().finally(() => {
                this.disabled = false;
                this.innerHTML = '<i class="fas fa-sync-alt me-2"></i>수동 새로고침';
            });
        });

        async function loadPrices() {
            try {
                const response = await fetch('/api/prices');
                const data = await response.json();
                
                updateUI(data);
            } catch (error) {
                console.error('가격 데이터 로드 오류:', error);
                showError('가격 데이터를 불러오는 중 오류가 발생했습니다.');
            }
        }

        function updateUI(data) {
            // Binance 가격
            if (data.binance.price) {
                document.getElementById('binancePrice').textContent = `$${data.binance.price.toFixed(6)}`;
            } else {
                document.getElementById('binancePrice').innerHTML = '<span class="text-danger">오류</span>';
            }

            // Hyperliquid 가격
            if (data.hyperliquid.price) {
                document.getElementById('hyperliquidPrice').textContent = `$${data.hyperliquid.price.toFixed(6)}`;
            } else {
                document.getElementById('hyperliquidPrice').innerHTML = '<span class="text-danger">오류</span>';
            }

            // 갭 정보
            if (data.gap) {
                document.getElementById('absoluteGap').textContent = `$${data.gap.absolute.toFixed(6)}`;
                document.getElementById('percentageGap').textContent = `${data.gap.percentage.toFixed(2)}%`;
                
                // 갭 상태에 따른 색상 설정
                const gapStatus = document.getElementById('gapStatus');
                if (data.gap.percentage < 1) {
                    gapStatus.textContent = '낮음';
                    gapStatus.className = 'gap-indicator gap-small';
                } else if (data.gap.percentage < 5) {
                    gapStatus.textContent = '보통';
                    gapStatus.className = 'gap-indicator gap-medium';
                } else {
                    gapStatus.textContent = '높음';
                    gapStatus.className = 'gap-indicator gap-large';
                }

                // 갭 분석 텍스트
                let analysis = '';
                if (data.gap.percentage < 1) {
                    analysis = '두 거래소 간 가격 차이가 매우 작습니다. 효율적인 시장 상태입니다.';
                } else if (data.gap.percentage < 5) {
                    analysis = '적당한 가격 차이가 있습니다. 차익거래 기회가 있을 수 있습니다.';
                } else {
                    analysis = '큰 가격 차이가 있습니다. 시장 비효율성이 높습니다.';
                }
                document.getElementById('gapAnalysis').textContent = analysis;
            } else {
                document.getElementById('absoluteGap').innerHTML = '<span class="text-danger">오류</span>';
                document.getElementById('percentageGap').innerHTML = '<span class="text-danger">오류</span>';
                document.getElementById('gapStatus').innerHTML = '<span class="text-danger">오류</span>';
                document.getElementById('gapAnalysis').textContent = '가격 데이터를 불러올 수 없습니다.';
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
        }

        function showError(message) {
            // 에러 메시지 표시 (간단한 구현)
            console.error(message);
        }

        // 페이지 언로드 시 인터벌 정리
        window.addEventListener('beforeunload', function() {
            if (updateInterval) {
                clearInterval(updateInterval);
            }
        });
    </script>
</body>
</html>'''
    
    with open(os.path.join(templates_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    logger.info("HTML 템플릿이 생성되었습니다.")

def main():
    """메인 함수"""
    print("🚀 XPL 가격 모니터 시작...")
    
    # 템플릿 생성
    create_templates()
    
    # 가격 모니터링 시작
    price_monitor.start_monitoring()
    
    # Flask 앱 실행
    print("🌐 웹 서버를 시작합니다...")
    print("📱 브라우저에서 http://localhost:5000 을 열어주세요")
    print("⏰ 30초마다 자동으로 가격이 업데이트됩니다")
    print("🔄 수동 새로고침 버튼으로 즉시 업데이트할 수 있습니다")
    
    app.run(host='0.0.0.0', port=5001, debug=False)

if __name__ == "__main__":
    main()
