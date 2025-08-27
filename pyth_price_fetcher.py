import requests
import json
from typing import Dict, List, Optional
import time

class PythPriceFetcher:
    def __init__(self):
        self.base_url = "https://xc-mainnet.pyth.network"
        self.api_url = "https://api.pyth.network"
        
    def get_all_price_feeds(self) -> List[Dict]:
        """
        Pyth Network에서 사용 가능한 모든 가격 피드(티커) 목록을 가져옵니다.
        """
        try:
            # Pyth API에서 모든 가격 피드 정보 가져오기
            url = f"{self.api_url}/api/price_feeds"
            response = requests.get(url)
            response.raise_for_status()
            
            price_feeds = response.json()
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
        try:
            url = f"{self.api_url}/api/price_feeds/{price_feed_id}/latest"
            response = requests.get(url)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"가격 정보 가져오기 오류 ({price_feed_id}): {e}")
            return None
    
    def get_bulk_latest_prices(self, price_feed_ids: List[str]) -> Dict[str, Dict]:
        """
        여러 가격 피드의 최신 가격 정보를 한 번에 가져옵니다.
        """
        try:
            url = f"{self.api_url}/api/latest_price_feeds"
            params = {'ids': ','.join(price_feed_ids)}
            
            response = requests.get(url, params=params)
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

def main():
    """
    메인 실행 함수
    """
    fetcher = PythPriceFetcher()
    
    # 1. 사용 가능한 모든 티커 출력
    fetcher.print_available_tickers()
    
    print("\n" + "="*50)
    
    # 2. 특정 자산 유형별 티커 가져오기
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
    
    # 3. 특정 티커의 최신 가격 정보 가져오기 (예시)
    print("\n" + "="*50)
    print("\n=== 특정 티커 가격 정보 ===")
    
    # BTC/USD 가격 정보 가져오기
    btc_price = fetcher.get_latest_price('e62df6c8b4c85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43')
    if btc_price:
        print(f"BTC/USD: ${btc_price.get('price', {}).get('price', 'N/A')}")
    
    # ETH/USD 가격 정보 가져오기
    eth_price = fetcher.get_latest_price('ff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace')
    if eth_price:
        print(f"ETH/USD: ${eth_price.get('price', {}).get('price', 'N/A')}")

if __name__ == "__main__":
    main() 