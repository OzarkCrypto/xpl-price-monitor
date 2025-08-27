#!/usr/bin/env python3
"""
ENA 토큰 컨트랙트 주소 찾기
실제 ENA 토큰의 컨트랙트 주소를 찾아서 온체인 모니터링에 사용할 수 있도록 합니다.
"""

import requests
import json
from datetime import datetime

def get_ena_contract_address():
    """ENA 토큰의 실제 컨트랙트 주소를 찾습니다."""
    print("🔍 ENA 토큰 컨트랙트 주소 찾기")
    print("=" * 50)
    
    try:
        # CoinGecko API로 ENA 상세 정보 가져오기
        url = "https://api.coingecko.com/api/v3/coins/ethena"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"📊 토큰명: {data['name']} ({data['symbol'].upper()})")
        print(f"🏷️  ID: {data['id']}")
        
        # 컨트랙트 주소들 찾기
        contract_addresses = {}
        
        # 플랫폼별 컨트랙트 주소
        if 'platforms' in data:
            print(f"\n🔗 플랫폼별 컨트랙트 주소:")
            for platform, address in data['platforms'].items():
                if address:
                    contract_addresses[platform] = address
                    print(f"  {platform}: {address}")
        
        # 블록체인 플랫폼 정보
        if 'blockchain_platform' in data:
            print(f"⛓️  블록체인: {data['blockchain_platform']}")
        
        # 웹사이트 및 소셜
        if 'links' in data:
            if 'homepage' in data['links'] and data['links']['homepage']:
                print(f"🌐 웹사이트: {data['links']['homepage'][0]}")
            if 'twitter_screen_name' in data['links']:
                print(f"🐦 Twitter: @{data['links']['twitter_screen_name']}")
        
        # 시장 데이터
        if 'market_data' in data:
            market = data['market_data']
            print(f"\n💰 시장 데이터:")
            print(f"  현재 가격: ${market['current_price']['usd']:,.6f}")
            print(f"  24시간 변화: {market['price_change_percentage_24h']:.2f}%")
            print(f"  24시간 거래량: ${market['total_volume']['usd']:,.0f}")
            print(f"  시가총액: ${market['market_cap']['usd']:,.0f}")
        
        # 기술적 정보
        if 'description' in data and 'en' in data['description']:
            desc = data['description']['en']
            if len(desc) > 200:
                desc = desc[:200] + "..."
            print(f"\n📝 설명: {desc}")
        
        print("=" * 50)
        
        return contract_addresses, data
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None, None

def get_ena_etherscan_info(contract_address):
    """Etherscan에서 ENA 컨트랙트 정보를 가져옵니다."""
    print(f"\n🔍 Etherscan 컨트랙트 정보: {contract_address}")
    print("=" * 50)
    
    try:
        # Etherscan API로 컨트랙트 정보 가져오기 (API 키 없이도 기본 정보 가능)
        url = f"https://api.etherscan.io/api"
        params = {
            'module': 'contract',
            'action': 'getabi',
            'address': contract_address
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        if data['status'] == '1':
            print("✅ 컨트랙트 ABI 확인됨")
            print(f"📊 ABI 길이: {len(data['result'])} 라인")
        else:
            print(f"⚠️  ABI 조회 실패: {data.get('message', 'Unknown error')}")
        
        # 토큰 정보
        token_url = f"https://api.etherscan.io/api"
        token_params = {
            'module': 'token',
            'action': 'tokeninfo',
            'contractaddress': contract_address
        }
        
        token_response = requests.get(url, params=token_params, timeout=15)
        token_response.raise_for_status()
        
        token_data = token_response.json()
        
        if token_data['status'] == '1' and token_data['result']:
            result = token_data['result'][0]
            print(f"\n📋 토큰 정보:")
            print(f"  이름: {result.get('tokenName', 'N/A')}")
            print(f"  심볼: {result.get('tokenSymbol', 'N/A')}")
            print(f"  소수점: {result.get('decimals', 'N/A')}")
            print(f"  총 공급량: {result.get('totalSupply', 'N/A')}")
        else:
            print(f"⚠️  토큰 정보 조회 실패: {token_data.get('message', 'Unknown error')}")
        
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Etherscan 조회 오류: {e}")

def main():
    """메인 함수"""
    print("🚀 ENA 토큰 컨트랙트 주소 찾기")
    print("=" * 50)
    
    # ENA 컨트랙트 주소 찾기
    contract_addresses, token_data = get_ena_contract_address()
    
    if not contract_addresses:
        print("❌ 컨트랙트 주소를 찾을 수 없습니다.")
        return
    
    # Ethereum 주소가 있다면 Etherscan 정보 조회
    if 'ethereum' in contract_addresses:
        eth_address = contract_addresses['ethereum']
        get_ena_etherscan_info(eth_address)
        
        print(f"\n💡 온체인 모니터링 설정:")
        print(f"   ENA 컨트랙트 주소: {eth_address}")
        print(f"   Etherscan: https://etherscan.io/token/{eth_address}")
        print(f"   DexScreener: https://dexscreener.com/ethereum/{eth_address}")
        
        # .env 파일 생성 가이드
        print(f"\n📝 .env 파일 설정:")
        print(f"   ETHERSCAN_API_KEY=your_api_key_here")
        print(f"   ENA_CONTRACT_ADDRESS={eth_address}")
        print(f"   ENA_MONITORING_INTERVAL=300")
        print(f"   ENA_BLOCK_RANGE=1000")
    
    # 데이터 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ena_contract_info_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'contract_addresses': contract_addresses,
                'token_data': token_data
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 데이터가 {filename}에 저장되었습니다.")
        
    except Exception as e:
        print(f"❌ 파일 저장 오류: {e}")
    
    print("\n✅ ENA 컨트랙트 주소 찾기 완료!")

if __name__ == "__main__":
    main() 