#!/usr/bin/env python3
"""
XPL 가격 모니터 API 테스트
"""

import requests
import json
import time

def test_binance_api():
    """Binance API 테스트"""
    print("🔍 Binance API 테스트...")
    try:
        url = "https://fapi.binance.com/fapi/v1/ticker/price"
        params = {'symbol': 'XPLUSDT'}
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Binance API 성공: {data}")
        
        if 'price' in data:
            price = float(data['price'])
            print(f"💰 XPL 가격: ${price:.6f}")
            return price
        else:
            print("❌ 가격 데이터가 없습니다")
            return None
            
    except Exception as e:
        print(f"❌ Binance API 오류: {e}")
        return None

def test_hyperliquid_api():
    """Hyperliquid API 테스트"""
    print("\n🔍 Hyperliquid API 테스트...")
    try:
        url = "https://api.hyperliquid.xyz/info"
        payload = {
            "type": "allMids"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Hyperliquid API 성공: {len(data)}개 심볼")
        
        # XPL 심볼 찾기 (데이터는 딕셔너리 형태)
        if 'XPL' in data:
            xpl_price = float(data['XPL'])
            print(f"💰 XPL 가격: ${xpl_price:.6f}")
        else:
            print("❌ XPL 심볼을 찾을 수 없습니다")
            print("사용 가능한 심볼들:")
            # 상위 10개만 표시
            symbols = list(data.keys())[:10]
            for i, symbol in enumerate(symbols):
                if symbol.startswith('@'):  # 숫자 키는 건너뛰기
                    continue
                print(f"  {i+1}. {symbol}: ${data[symbol]}")
        
        return xpl_price
        
    except Exception as e:
        print(f"❌ Hyperliquid API 오류: {e}")
        return None

def test_local_server():
    """로컬 서버 테스트"""
    print("\n🔍 로컬 서버 테스트...")
    try:
        # 가격 데이터 가져오기
        response = requests.get('http://localhost:5001/api/prices', timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print("✅ 로컬 서버 API 성공")
        print(f"📊 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 로컬 서버 오류: {e}")
        return False

def main():
    """메인 함수"""
    print("🚀 XPL 가격 모니터 API 테스트")
    print("=" * 50)
    
    # Binance API 테스트
    binance_price = test_binance_api()
    
    # Hyperliquid API 테스트
    hyperliquid_price = test_hyperliquid_api()
    
    # 가격 비교
    if binance_price and hyperliquid_price:
        gap = abs(binance_price - hyperliquid_price)
        gap_percentage = (gap / min(binance_price, hyperliquid_price)) * 100
        
        print(f"\n📊 가격 비교 결과:")
        print(f"Binance: ${binance_price:.6f}")
        print(f"Hyperliquid: ${hyperliquid_price:.6f}")
        print(f"절대 갭: ${gap:.6f}")
        print(f"상대 갭: {gap_percentage:.2f}%")
        
        if gap_percentage < 1:
            print("🟢 갭이 낮습니다 (효율적인 시장)")
        elif gap_percentage < 5:
            print("🟡 갭이 보통입니다 (차익거래 기회 가능)")
        else:
            print("🔴 갭이 높습니다 (시장 비효율성)")
    
    # 로컬 서버 테스트
    print("\n" + "=" * 50)
    test_local_server()
    
    print("\n✅ 테스트 완료!")

if __name__ == "__main__":
    main()
