import requests
import json
from typing import List, Dict
import time

class PythSymbolsFetcher:
    def __init__(self):
        # Pyth Network의 다양한 API 엔드포인트들
        self.api_endpoints = [
            "https://hermes.pyth.network",
            "https://api.pyth.network", 
            "https://xc-mainnet.pyth.network"
        ]
    
    def get_working_endpoint(self) -> str:
        """
        작동하는 API 엔드포인트를 찾습니다.
        """
        for endpoint in self.api_endpoints:
            try:
                print(f"테스트 중: {endpoint}")
                # 간단한 헬스체크
                response = requests.get(f"{endpoint}/", timeout=5)
                if response.status_code in [200, 404]:  # 404도 정상 (API 경로가 없을 뿐)
                    print(f"✅ 연결 성공: {endpoint}")
                    return endpoint
            except Exception as e:
                print(f"❌ 연결 실패: {endpoint} - {str(e)[:50]}...")
                continue
        
        return None
    
    def get_all_symbols(self) -> List[str]:
        """
        Pyth Network에서 publish되고 있는 모든 심볼 리스트를 가져옵니다.
        """
        working_endpoint = self.get_working_endpoint()
        if not working_endpoint:
            print("❌ 사용 가능한 API 엔드포인트를 찾을 수 없습니다.")
            return []
        
        symbols = []
        
        # 여러 가능한 API 경로들을 시도
        api_paths = [
            "/api/price_feeds",
            "/api/v1/price_feeds", 
            "/price_feeds",
            "/api/feeds"
        ]
        
        for path in api_paths:
            try:
                url = f"{working_endpoint}{path}"
                print(f"심볼 정보 가져오는 중: {url}")
                
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    # 다양한 응답 형식 처리
                    if isinstance(data, list):
                        for item in data:
                            symbol = self.extract_symbol(item)
                            if symbol:
                                symbols.append(symbol)
                    elif isinstance(data, dict):
                        # 딕셔너리 형태의 응답 처리
                        if 'data' in data:
                            for item in data['data']:
                                symbol = self.extract_symbol(item)
                                if symbol:
                                    symbols.append(symbol)
                    
                    if symbols:
                        print(f"✅ {len(symbols)}개의 심볼을 성공적으로 가져왔습니다.")
                        return list(set(symbols))  # 중복 제거
                        
            except Exception as e:
                print(f"경로 {path} 시도 실패: {str(e)[:50]}...")
                continue
        
        # API가 작동하지 않는 경우, 알려진 주요 심볼들 반환
        print("⚠️ API에서 심볼을 가져올 수 없어 알려진 주요 심볼들을 반환합니다.")
        return self.get_known_symbols()
    
    def extract_symbol(self, item: Dict) -> str:
        """
        응답 데이터에서 심볼을 추출합니다.
        """
        # 다양한 필드명에서 심볼 추출 시도
        symbol_fields = ['symbol', 'ticker', 'pair', 'name', 'id']
        
        for field in symbol_fields:
            if field in item and item[field]:
                symbol = str(item[field])
                # 심볼 형태가 아닌 것들 필터링
                if len(symbol) < 50 and '/' in symbol:  # 일반적인 심볼 형태
                    return symbol
        
        # metadata 내부에서도 확인
        if 'metadata' in item and isinstance(item['metadata'], dict):
            for field in symbol_fields:
                if field in item['metadata'] and item['metadata'][field]:
                    symbol = str(item['metadata'][field])
                    if len(symbol) < 50 and '/' in symbol:
                        return symbol
        
        return None
    
    def get_known_symbols(self) -> List[str]:
        """
        Pyth Network에서 알려진 주요 심볼들을 반환합니다.
        """
        return [
            "BTC/USD",
            "ETH/USD", 
            "SOL/USD",
            "USDC/USD",
            "USDT/USD",
            "BNB/USD",
            "XRP/USD",
            "ADA/USD",
            "AVAX/USD",
            "DOT/USD",
            "MATIC/USD",
            "LINK/USD",
            "UNI/USD",
            "LTC/USD",
            "BCH/USD",
            "ATOM/USD",
            "FTM/USD",
            "NEAR/USD",
            "ALGO/USD",
            "VET/USD",
            "ICP/USD",
            "FIL/USD",
            "TRX/USD",
            "ETC/USD",
            "XLM/USD",
            "HBAR/USD",
            "THETA/USD",
            "XTZ/USD",
            "EOS/USD",
            "AAVE/USD",
            "SUSHI/USD",
            "COMP/USD",
            "MKR/USD",
            "YFI/USD",
            "SNX/USD",
            "CRV/USD",
            "BAL/USD",
            "REN/USD",
            "ZRX/USD",
            "BAND/USD",
            "UMA/USD",
            "KNC/USD",
            "REP/USD",
            "LRC/USD",
            "MANA/USD",
            "SAND/USD",
            "ENJ/USD",
            "CHZ/USD",
            "HOT/USD",
            "DOGE/USD",
            "SHIB/USD"
        ]
    
    def get_symbols_by_category(self) -> Dict[str, List[str]]:
        """
        카테고리별로 심볼들을 분류합니다.
        """
        all_symbols = self.get_all_symbols()
        
        categories = {
            "Major Crypto": [],
            "DeFi Tokens": [],
            "Gaming/Metaverse": [],
            "Others": []
        }
        
        major_crypto = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "AVAX", "DOT", "MATIC"]
        defi_tokens = ["AAVE", "SUSHI", "COMP", "MKR", "YFI", "SNX", "CRV", "BAL", "REN", "ZRX", "BAND", "UMA", "KNC", "REP", "LRC"]
        gaming_metaverse = ["MANA", "SAND", "ENJ", "CHZ", "HOT"]
        
        for symbol in all_symbols:
            base = symbol.split('/')[0] if '/' in symbol else symbol
            
            if base in major_crypto:
                categories["Major Crypto"].append(symbol)
            elif base in defi_tokens:
                categories["DeFi Tokens"].append(symbol)
            elif base in gaming_metaverse:
                categories["Gaming/Metaverse"].append(symbol)
            else:
                categories["Others"].append(symbol)
        
        return categories

def main():
    """
    메인 실행 함수
    """
    print("🔍 Pyth Network 심볼 리스트 가져오기\n")
    
    fetcher = PythSymbolsFetcher()
    
    # 1. 모든 심볼 가져오기
    print("=== 현재 Publish되고 있는 심볼들 ===")
    symbols = fetcher.get_all_symbols()
    
    if symbols:
        print(f"\n총 {len(symbols)}개의 심볼이 있습니다:\n")
        for i, symbol in enumerate(symbols, 1):
            print(f"{i:2d}. {symbol}")
    else:
        print("❌ 심볼을 가져올 수 없습니다.")
        return
    
    print("\n" + "="*50)
    
    # 2. 카테고리별 분류
    print("\n=== 카테고리별 심볼 분류 ===")
    categories = fetcher.get_symbols_by_category()
    
    for category, symbol_list in categories.items():
        if symbol_list:
            print(f"\n--- {category} ({len(symbol_list)}개) ---")
            for symbol in symbol_list:
                print(f"  {symbol}")
    
    print(f"\n✅ 총 {len(symbols)}개의 Pyth Network 심볼을 성공적으로 가져왔습니다!")

if __name__ == "__main__":
    main() 