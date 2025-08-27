import requests
import json
from typing import Dict, List, Optional
import time

class PythPriceFetcherV2:
    def __init__(self):
        # Pyth Network의 최신 API 엔드포인트들
        self.api_urls = [
            "https://api.pyth.network",
            "https://xc-mainnet.pyth.network",
            "https://hermes.pyth.network"
        ]
        
    def test_connection(self) -> str:
        """
        사용 가능한 API 엔드포인트를 찾습니다.
        """
        for url in self.api_urls:
            try:
                print(f"연결 테스트 중: {url}")
                response = requests.get(f"{url}/api/price_feeds", timeout=10)
                if response.status_code == 200:
                    print(f"✅ 연결 성공: {url}")
                    return url
                else:
                    print(f"❌ 상태 코드 {response.status_code}: {url}")
            except Exception as e:
                print(f"❌ 연결 실패: {url} - {e}")
        
        return None
    
    def get_all_price_feeds(self) -> List[Dict]:
        """
        Pyth Network에서 사용 가능한 모든 가격 피드(티커) 목록을 가져옵니다.
        """
        working_url = self.test_connection()
        if not working_url:
            print("사용 가능한 API 엔드포인트를 찾을 수 없습니다.")
            return []
        
        try:
            # 먼저 Hermes API를 시도 (최신)
            url = f"{working_url}/api/price_feeds"
            print(f"가격 피드 정보 가져오는 중: {url}")
            
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            price_feeds = response.json()
            print(f"✅ {len(price_feeds)}개의 가격 피드를 성공적으로 가져왔습니다.")
            return price_feeds
            
        except requests.exceptions.RequestException as e:
            print(f"API 요청 중 오류 발생: {e}")
            return []
    
    def get_price_feed_ids(self) -> List[str]:
        """
        모든 가격 피드 ID(티커) 목록을 반환합니다.
        """
        price_feeds = self.get_all_price_feeds()
        feed_ids = []
        
        for feed in price_feeds:
            if 'id' in feed:
                feed_ids.append(feed['id'])
        
        return feed_ids
    
    def get_latest_price(self, price_feed_id: str) -> Optional[Dict]:
        """
        특정 가격 피드의 최신 가격 정보를 가져옵니다.
        """
        working_url = self.test_connection()
        if not working_url:
            return None
            
        try:
            url = f"{working_url}/api/price_feeds/{price_feed_id}/latest"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"가격 정보 가져오기 오류 ({price_feed_id}): {e}")
            return None
    
    def get_bulk_latest_prices(self, price_feed_ids: List[str]) -> Dict[str, Dict]:
        """
        여러 가격 피드의 최신 가격 정보를 한 번에 가져옵니다.
        """
        working_url = self.test_connection()
        if not working_url:
            return {}
            
        try:
            url = f"{working_url}/api/latest_price_feeds"
            params = {'ids': ','.join(price_feed_ids)}
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"대량 가격 정보 가져오기 오류: {e}")
            return {}
    
    def get_price_feeds_by_asset_type(self, asset_type: str = None) -> List[Dict]:
        """
        특정 자산 유형별로 가격 피드를 필터링합니다.
        """
        all_feeds = self.get_all_price_feeds()
        
        if asset_type:
            filtered_feeds = [
                feed for feed in all_feeds 
                if feed.get('metadata', {}).get('asset_type') == asset_type
            ]
            return filtered_feeds
        
        return all_feeds
    
    def print_available_tickers(self):
        """
        사용 가능한 모든 티커를 출력합니다.
        """
        print("=== Pyth Network 사용 가능한 가격 피드 목록 ===")
        
        price_feeds = self.get_all_price_feeds()
        
        if not price_feeds:
            print("가격 피드 정보를 가져올 수 없습니다.")
            return
        
        print(f"총 {len(price_feeds)}개의 가격 피드가 있습니다.\n")
        
        # 자산 유형별로 그룹화
        asset_types = {}
        for feed in price_feeds:
            asset_type = feed.get('metadata', {}).get('asset_type', 'Unknown')
            if asset_type not in asset_types:
                asset_types[asset_type] = []
            asset_types[asset_type].append(feed)
        
        for asset_type, feeds in asset_types.items():
            print(f"\n--- {asset_type} ({len(feeds)}개) ---")
            for feed in feeds[:10]:  # 각 유형별로 최대 10개만 표시
                symbol = feed.get('metadata', {}).get('symbol', 'Unknown')
                feed_id = feed.get('id', 'Unknown')
                print(f"  {symbol}: {feed_id}")
            
            if len(feeds) > 10:
                print(f"  ... 및 {len(feeds) - 10}개 더")
    
    def get_common_crypto_pairs(self) -> List[Dict]:
        """
        일반적인 암호화폐 페어들의 정보를 반환합니다.
        """
        common_pairs = [
            {'symbol': 'BTC/USD', 'id': 'e62df6c8b4c85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43'},
            {'symbol': 'ETH/USD', 'id': 'ff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace'},
            {'symbol': 'SOL/USD', 'id': 'ef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cfac8c280b56d'},
            {'symbol': 'USDC/USD', 'id': 'eaa020c61cc479712813461ce153894a96a6c00bdbed070c01c5fa5cde9fe4c5'},
            {'symbol': 'USDT/USD', 'id': '2b89b9dc8fdf9f34709a5b106b472f0f39bb6ca9ce04b0fd7f2e971688e2e53b'}
        ]
        return common_pairs

def main():
    """
    메인 실행 함수
    """
    print("🚀 Pyth Network 가격 데이터 가져오기 시작...\n")
    
    fetcher = PythPriceFetcherV2()
    
    # 1. 연결 테스트
    print("=== 연결 테스트 ===")
    working_url = fetcher.test_connection()
    if not working_url:
        print("❌ 사용 가능한 API 엔드포인트를 찾을 수 없습니다.")
        print("인터넷 연결을 확인하거나 나중에 다시 시도해주세요.")
        return
    
    print(f"\n✅ 사용 가능한 API: {working_url}\n")
    
    # 2. 사용 가능한 모든 티커 출력
    fetcher.print_available_tickers()
    
    print("\n" + "="*50)
    
    # 3. 특정 자산 유형별 티커 가져오기
    print("\n=== 암호화폐 가격 피드 ===")
    crypto_feeds = fetcher.get_price_feeds_by_asset_type('crypto')
    for feed in crypto_feeds[:5]:  # 처음 5개만 표시
        symbol = feed.get('metadata', {}).get('symbol', 'Unknown')
        print(f"  {symbol}")
    
    print("\n=== 주식 가격 피드 ===")
    equity_feeds = fetcher.get_price_feeds_by_asset_type('equity')
    for feed in equity_feeds[:5]:  # 처음 5개만 표시
        symbol = feed.get('metadata', {}).get('symbol', 'Unknown')
        print(f"  {symbol}")
    
    # 4. 일반적인 암호화폐 페어들의 가격 정보 가져오기
    print("\n" + "="*50)
    print("\n=== 주요 암호화폐 가격 정보 ===")
    
    common_pairs = fetcher.get_common_crypto_pairs()
    for pair in common_pairs:
        price_data = fetcher.get_latest_price(pair['id'])
        if price_data:
            price = price_data.get('price', {}).get('price', 'N/A')
            print(f"{pair['symbol']}: ${price}")
        else:
            print(f"{pair['symbol']}: 데이터 없음")
        time.sleep(0.5)  # API 요청 간격 조절

if __name__ == "__main__":
    main() 