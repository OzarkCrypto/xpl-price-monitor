import json
import requests
from datetime import datetime

def handler(request, context):
    """Vercel 서버리스 함수 핸들러"""
    try:
        path = request.get('path', '/')
        
        if path == '/':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/html; charset=utf-8',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': get_html_content()
            }
        
        elif path == '/api/prices':
            data = get_price_data()
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json; charset=utf-8',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(data, ensure_ascii=False)
            }
        
        elif path == '/api/update':
            data = update_prices()
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json; charset=utf-8',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(data, ensure_ascii=False)
            }
        
        else:
            return {
                'statusCode': 404,
                'body': 'Not Found'
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Internal Server Error: {str(e)}'
        }

def get_binance_xpl_price():
    """Binance에서 XPL 가격을 가져옵니다."""
    try:
        url = "https://fapi.binance.com/fapi/v1/ticker/price"
        params = {'symbol': 'XPLUSDT'}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        price = float(data['price'])
        return price
        
    except Exception as e:
        print(f"Binance API 오류: {e}")
        return None

def get_hyperliquid_xpl_price():
    """Hyperliquid에서 XPL 가격을 가져옵니다."""
    try:
        url = "https://api.hyperliquid.xyz/info"
        payload = {"type": "allMids"}
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'XPL' in data:
            xpl_price = float(data['XPL'])
            return xpl_price
        else:
            return None
            
    except Exception as e:
        print(f"Hyperliquid API 오류: {e}")
        return None

def calculate_gap(binance_price, hyperliquid_price):
    """가격 갭을 계산합니다."""
    if binance_price is None or hyperliquid_price is None:
        return {
            'absolute': None,
            'percentage': None,
            'status': 'unknown'
        }
    
    absolute_gap = abs(hyperliquid_price - binance_price)
    percentage_gap = (absolute_gap / binance_price) * 100
    
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

def get_price_data():
    """현재 가격 데이터를 반환합니다."""
    binance_price = get_binance_xpl_price()
    hyperliquid_price = get_hyperliquid_xpl_price()
    
    gap = calculate_gap(binance_price, hyperliquid_price)
    current_time = datetime.now()
    
    return {
        'binance': {
            'price': binance_price,
            'exchange': 'Binance Futures',
            'url': 'https://www.binance.com/en/futures/XPLUSDT'
        },
        'hyperliquid': {
            'price': hyperliquid_price,
            'exchange': 'Hyperliquid',
            'url': 'https://app.hyperliquid.xyz/trade'
        },
        'gap': gap,
        'last_update': current_time.isoformat(),
        'seconds_ago': 0,
        'timestamp': current_time.isoformat()
    }

def update_prices():
    """가격을 업데이트합니다."""
    return {'success': True, 'message': '가격이 업데이트되었습니다.'}

def get_html_content():
    """HTML 콘텐츠를 반환합니다."""
    return '''
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
                        if (data.binance.price !== null) {
                            document.getElementById('binancePrice').textContent = '$' + data.binance.price.toFixed(6);
                        } else {
                            document.getElementById('binancePrice').textContent = '오류';
                        }
                        
                        if (data.hyperliquid.price !== null) {
                            document.getElementById('hyperliquidPrice').textContent = '$' + data.hyperliquid.price.toFixed(6);
                        } else {
                            document.getElementById('hyperliquidPrice').textContent = '오류';
                        }
                        
                        if (data.gap.absolute !== null) {
                            document.getElementById('absoluteGap').textContent = '$' + data.gap.absolute.toFixed(6);
                            document.getElementById('relativeGap').textContent = data.gap.percentage + '%';
                            
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
                        
                        if (data.last_update) {
                            const updateTime = new Date(data.last_update);
                            document.getElementById('lastUpdate').textContent = updateTime.toLocaleString('ko-KR');
                        }
                        
                        if (data.seconds_ago !== null && data.seconds_ago !== undefined) {
                            document.getElementById('secondsAgo').textContent = data.seconds_ago;
                        } else {
                            document.getElementById('secondsAgo').textContent = '-';
                        }
                    })
                    .catch(error => {
                        console.error('가격 업데이트 오류:', error);
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
                    });
            }
            
            document.addEventListener('DOMContentLoaded', function() {
                updatePrices();
                updateInterval = setInterval(updatePrices, 30000);
            });
            
            window.addEventListener('beforeunload', function() {
                if (updateInterval) {
                    clearInterval(updateInterval);
                }
            });
        </script>
    </body>
    </html>
    '''
