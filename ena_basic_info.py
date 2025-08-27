#!/usr/bin/env python3
"""
ENA 토큰 기본 정보 확인
API 키 없이도 기본적인 정보를 확인할 수 있습니다.
"""

import requests
import json
from datetime import datetime
import time

def search_ena_token():
    """ENA 토큰을 검색합니다."""
    print("🔍 ENA 토큰 검색 중...")
    print("=" * 50)
    
    try:
        # CoinGecko API로 ENA 검색
        url = "https://api.coingecko.com/api/v3/search"
        params = {'query': 'ena'}
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        coins = data.get('coins', [])
        
        print(f"🔍 'ena' 검색 결과: {len(coins)}개 토큰 발견")
        
        # ENA 관련 토큰들 찾기
        ena_tokens = []
        for coin in coins:
            if 'ena' in coin['id'].lower() or 'ena' in coin['symbol'].lower():
                ena_tokens.append(coin)
        
        if ena_tokens:
            print(f"\n📋 ENA 관련 토큰들:")
            for i, token in enumerate(ena_tokens[:10]):  # 상위 10개 표시
                print(f"  {i+1}. {token['name']} ({token['symbol'].upper()}) - {token['id']}")
            
            # Ethena의 ENA 토큰 찾기 (정확한 매칭)
            ethena_ena = None
            for token in ena_tokens:
                if (token['symbol'].lower() == 'ena' and 
                    'ethena' in token['name'].lower()):
                    ethena_ena = token
                    break
            
            if ethena_ena:
                print(f"\n🎯 Ethena ENA 토큰 발견: {ethena_ena['name']} ({ethena_ena['symbol'].upper()})")
                return ethena_ena['id']
            else:
                # ENA 심볼을 가진 토큰 찾기
                for token in ena_tokens:
                    if token['symbol'].lower() == 'ena':
                        print(f"\n💡 ENA 심볼 토큰 발견: {token['name']} ({token['symbol'].upper()})")
                        return token['id']
                
                # 첫 번째 ENA 관련 토큰 사용
                print(f"\n💡 첫 번째 ENA 관련 토큰 사용: {ena_tokens[0]['name']}")
                return ena_tokens[0]['id']
        else:
            print("❌ ENA 관련 토큰을 찾을 수 없습니다.")
            return None
            
    except Exception as e:
        print(f"❌ 검색 오류: {e}")
        return None

def get_ena_basic_info(token_id):
    """ENA 토큰의 기본 정보를 가져옵니다."""
    print(f"\n🔍 {token_id} 토큰 기본 정보 조회 중...")
    print("=" * 50)
    
    try:
        # CoinGecko API로 ENA 정보 가져오기
        url = f"https://api.coingecko.com/api/v3/coins/{token_id}"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"📊 토큰명: {data['name']} ({data['symbol'].upper()})")
        print(f"🏷️  ID: {data['id']}")
        print(f"💰 현재 가격: ${data['market_data']['current_price']['usd']:,.6f}")
        print(f"📈 24시간 변화: {data['market_data']['price_change_percentage_24h']:.2f}%")
        print(f"📊 24시간 거래량: ${data['market_data']['total_volume']['usd']:,.0f}")
        print(f"🏦 시가총액: ${data['market_data']['market_cap']['usd']:,.0f}")
        print(f"💎 순환 공급량: {data['market_data']['circulating_supply']:,.0f}")
        print(f"🌐 웹사이트: {data['links']['homepage'][0] if data['links']['homepage'] else 'N/A'}")
        
        # 기술적 정보
        if 'blockchain_platform' in data:
            print(f"⛓️  블록체인: {data['blockchain_platform']}")
        
        # 소셜 미디어
        if 'twitter_screen_name' in data['links']:
            print(f"🐦 Twitter: @{data['links']['twitter_screen_name']}")
        
        print("=" * 50)
        
        return data
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None

def get_ena_market_data(token_id):
    """ENA 시장 데이터를 가져옵니다."""
    print(f"\n📈 {token_id} 시장 데이터 조회 중...")
    print("=" * 50)
    
    try:
        # 간단한 가격 정보
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': token_id,
            'vs_currencies': 'usd,btc,eth',
            'include_24hr_change': 'true',
            'include_24hr_vol': 'true',
            'include_market_cap': 'true'
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        token_data = data[token_id]
        
        print(f"💵 USD 가격: ${token_data['usd']:.6f}")
        print(f"₿ BTC 가격: {token_data['btc']:.8f}")
        print(f"Ξ ETH 가격: {token_data['eth']:.8f}")
        print(f"📊 24시간 변화: {token_data['usd_24h_change']:.2f}%")
        print(f"💎 24시간 거래량: ${token_data['usd_24h_vol']:,.0f}")
        print(f"🏦 시가총액: ${token_data['usd_market_cap']:,.0f}")
        
        print("=" * 50)
        
        return token_data
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None

def get_ena_contract_info():
    """ENA 컨트랙트 정보를 표시합니다."""
    print("\n📋 ENA 컨트랙트 정보")
    print("=" * 50)
    
    # ENA 토큰 컨트랙트 주소 (Ethereum) - 실제 주소로 업데이트 필요
    ena_contract = "0x183015a9bA6Ff6D4A0c8C0c0c0c0c0c0c0c0c0c0c0"  # 예시 주소
    
    print(f"🔗 컨트랙트 주소: {ena_contract}")
    print(f"🌐 Etherscan: https://etherscan.io/token/{ena_contract}")
    print(f"📊 DexScreener: https://dexscreener.com/ethereum/{ena_contract}")
    print(f"💰 CoinGecko: https://www.coingecko.com/en/coins/ena")
    
    print("\n💡 온체인 유통량을 자세히 보려면:")
    print("   1. Etherscan API 키를 발급받으세요")
    print("   2. .env 파일에 ETHERSCAN_API_KEY를 설정하세요")
    print("   3. python3 ena_onchain_flow_monitor.py를 실행하세요")
    
    print("=" * 50)

def main():
    """메인 함수"""
    print("🚀 ENA 토큰 정보 확인 도구")
    print("=" * 50)
    
    # ENA 토큰 검색
    token_id = search_ena_token()
    
    if not token_id:
        print("❌ ENA 토큰을 찾을 수 없습니다.")
        return
    
    # 기본 정보
    basic_info = get_ena_basic_info(token_id)
    
    # 시장 데이터
    market_data = get_ena_market_data(token_id)
    
    # 컨트랙트 정보
    get_ena_contract_info()
    
    # 데이터 저장
    if basic_info or market_data:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ena_basic_info_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'token_id': token_id,
                    'basic_info': basic_info,
                    'market_data': market_data
                }, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 데이터가 {filename}에 저장되었습니다.")
            
        except Exception as e:
            print(f"❌ 파일 저장 오류: {e}")
    
    print("\n✅ ENA 토큰 정보 확인 완료!")

if __name__ == "__main__":
    main() 