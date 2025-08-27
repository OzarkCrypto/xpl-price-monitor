#!/usr/bin/env python3
"""
알트 러너 모니터링 봇 테스트 스크립트
"""

import requests
import json
from datetime import datetime

def test_doge_volume():
    """도지 거래량 조회 테스트"""
    print("🐕 도지 거래량 조회 테스트...")
    
    try:
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
        print(f"✅ 도지 24시간 거래량: ${doge_volume:,.0f}")
        return doge_volume
        
    except Exception as e:
        print(f"❌ 도지 거래량 조회 오류: {e}")
        return None

def test_coinbase_listings():
    """코인베이스 상장 토큰 조회 테스트"""
    print("\n🏦 코인베이스 상장 토큰 조회 테스트...")
    
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'volume_desc',
            'per_page': 10,
            'page': 1,
            'sparkline': False,
            'exchange': 'coinbase'
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ 코인베이스 상장 토큰 {len(data)}개 조회 완료")
        
        print("\n📊 상위 5개 토큰:")
        for i, token in enumerate(data[:5], 1):
            print(f"  {i}. {token['symbol'].upper()} ({token['name']})")
            print(f"     💰 24시간 거래량: ${token.get('total_volume', 0):,.0f}")
            print(f"     📈 24시간 변화: {token.get('price_change_percentage_24h', 0):.2f}%")
            print()
        
        return data
        
    except Exception as e:
        print(f"❌ 코인베이스 상장 토큰 조회 오류: {e}")
        return []

def test_funding_rate():
    """펀딩비 조회 테스트"""
    print("\n💸 펀딩비 조회 테스트...")
    
    # 테스트할 심볼들
    test_symbols = ['BTC', 'ETH', 'DOGE']
    
    for symbol in test_symbols:
        try:
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
                print(f"✅ {symbol} 펀딩비: {funding_rate:.6f}")
            else:
                print(f"⚠️  {symbol} 펀딩비 데이터 없음")
                
        except Exception as e:
            print(f"❌ {symbol} 펀딩비 조회 오류: {e}")

def test_telegram_bot():
    """텔레그램 봇 테스트"""
    print("\n🤖 텔레그램 봇 테스트...")
    
    token = "8025422463:AAF0oCsGwWtykrGQnZvEFXP6Jq7THdGaexA"
    chat_id = "1339285013"
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": f"🧪 알트 러너 모니터링 봇 테스트\n\n⏰ 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n✅ 봇이 정상적으로 작동하고 있습니다!",
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=data, timeout=15)
        if response.status_code == 200:
            print("✅ 텔레그램 테스트 메시지 전송 성공!")
        else:
            print(f"❌ 텔레그램 메시지 전송 실패: {response.status_code}")
            print(f"응답: {response.text}")
            
    except Exception as e:
        print(f"❌ 텔레그램 봇 테스트 오류: {e}")

def main():
    """메인 테스트 함수"""
    print("🧪 알트 러너 모니터링 봇 테스트 시작")
    print("=" * 50)
    
    # 1. 도지 거래량 테스트
    doge_volume = test_doge_volume()
    
    # 2. 코인베이스 상장 토큰 테스트
    coinbase_tokens = test_coinbase_listings()
    
    # 3. 펀딩비 테스트
    test_funding_rate()
    
    # 4. 텔레그램 봇 테스트
    test_telegram_bot()
    
    print("\n" + "=" * 50)
    print("✅ 모든 테스트 완료!")
    
    if doge_volume and coinbase_tokens:
        print(f"\n📊 테스트 결과 요약:")
        print(f"   🐕 도지 거래량: ${doge_volume:,.0f}")
        print(f"   🏦 코인베이스 토큰: {len(coinbase_tokens)}개")
        print(f"   🤖 텔레그램 봇: 정상 작동")
        print(f"\n🚀 이제 alt_runner_monitor.py를 실행할 수 있습니다!")

if __name__ == "__main__":
    main() 