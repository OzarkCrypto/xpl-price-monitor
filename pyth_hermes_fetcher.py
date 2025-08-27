import requests
import json
from typing import List, Dict
import time

class PythHermesFetcher:
    def __init__(self):
        self.base_url = "https://hermes.pyth.network"
    
    def explore_hermes_api(self):
        """
        Hermes API의 구조를 탐색합니다.
        """
        print("🔍 Hermes API 구조 탐색 중...\n")
        
        # 루트 경로에서 사용 가능한 엔드포인트 확인
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                endpoints = response.json()
                print(f"✅ 루트 엔드포인트에서 {len(endpoints)}개의 경로를 발견했습니다:")
                for endpoint in endpoints:
                    print(f"  - {endpoint}")
                
                return endpoints
        except Exception as e:
            print(f"❌ 루트 경로 접근 실패: {e}")
        
        return []
    
    def get_live_feeds(self):
        """
        /live 엔드포인트에서 실시간 피드 정보를 가져옵니다.
        """
        print("\n📡 실시간 피드 정보 가져오기...")
        
        try:
            response = requests.get(f"{self.base_url}/live", timeout=15)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 실시간 피드 데이터를 성공적으로 가져왔습니다!")
                return data
            else:
                print(f"❌ 상태 코드: {response.status_code}")
        except Exception as e:
            print(f"❌ 실시간 피드 가져오기 실패: {e}")
        
        return None
    
    def get_price_feeds(self):
        """
        /price_feeds 엔드포인트에서 가격 피드 정보를 가져옵니다.
        """
        print("\n💰 가격 피드 정보 가져오기...")
        
        try:
            response = requests.get(f"{self.base_url}/price_feeds", timeout=15)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 가격 피드 데이터를 성공적으로 가져왔습니다!")
                return data
            else:
                print(f"❌ 상태 코드: {response.status_code}")
        except Exception as e:
            print(f"❌ 가격 피드 가져오기 실패: {e}")
        
        return None
    
    def get_symbols_from_live_data(self, live_data):
        """
        실시간 데이터에서 심볼들을 추출합니다.
        """
        symbols = []
        
        if isinstance(live_data, dict):
            # 딕셔너리 형태의 응답 처리
            for key, value in live_data.items():
                if isinstance(value, dict):
                    # 심볼 정보가 있는지 확인
                    symbol = self.extract_symbol_from_item(value)
                    if symbol:
                        symbols.append(symbol)
                elif isinstance(value, list):
                    # 리스트 형태의 값 처리
                    for item in value:
                        if isinstance(item, dict):
                            symbol = self.extract_symbol_from_item(item)
                            if symbol:
                                symbols.append(symbol)
        
        elif isinstance(live_data, list):
            # 리스트 형태의 응답 처리
            for item in live_data:
                if isinstance(item, dict):
                    symbol = self.extract_symbol_from_item(item)
                    if symbol:
                        symbols.append(symbol)
        
        return list(set(symbols))  # 중복 제거
    
    def extract_symbol_from_item(self, item):
        """
        개별 항목에서 심볼을 추출합니다.
        """
        if not isinstance(item, dict):
            return None
        
        # 다양한 필드명에서 심볼 추출 시도
        symbol_fields = ['symbol', 'ticker', 'pair', 'name', 'id', 'feed_id']
        
        for field in symbol_fields:
            if field in item and item[field]:
                value = str(item[field])
                # 심볼 형태인지 확인
                if '/' in value or '-' in value:
                    if len(value) < 30:  # 너무 긴 값은 제외
                        return value
        
        # metadata 내부에서도 확인
        if 'metadata' in item and isinstance(item['metadata'], dict):
            for field in symbol_fields:
                if field in item['metadata'] and item['metadata'][field]:
                    value = str(item['metadata'][field])
                    if '/' in value or '-' in value:
                        if len(value) < 30:
                            return value
        
        return None
    
    def get_detailed_symbols(self):
        """
        심볼과 함께 상세 정보를 가져옵니다.
        """
        print("\n📊 상세 심볼 정보 가져오기...")
        
        # 여러 엔드포인트를 시도
        endpoints = ['/live', '/price_feeds', '/feeds']
        
        for endpoint in endpoints:
            try:
                print(f"시도 중: {endpoint}")
                response = requests.get(f"{self.base_url}{endpoint}", timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {endpoint}에서 데이터를 성공적으로 가져왔습니다!")
                    
                    # 데이터 구조 분석
                    print(f"데이터 타입: {type(data)}")
                    if isinstance(data, dict):
                        print(f"키들: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"리스트 길이: {len(data)}")
                        if len(data) > 0:
                            print(f"첫 번째 항목: {data[0]}")
                    
                    return data
                    
            except Exception as e:
                print(f"❌ {endpoint} 실패: {e}")
        
        return None

def main():
    """
    메인 실행 함수
    """
    print("🚀 Pyth Network Hermes API 데이터 가져오기\n")
    
    fetcher = PythHermesFetcher()
    
    # 1. API 구조 탐색
    print("=== 1단계: API 구조 탐색 ===")
    endpoints = fetcher.explore_hermes_api()
    
    print("\n" + "="*60)
    
    # 2. 실시간 피드 데이터 가져오기
    print("\n=== 2단계: 실시간 피드 데이터 ===")
    live_data = fetcher.get_live_feeds()
    
    if live_data:
        print(f"\n실시간 데이터 구조:")
        print(f"타입: {type(live_data)}")
        if isinstance(live_data, dict):
            print(f"키 개수: {len(live_data)}")
            for key in list(live_data.keys())[:5]:  # 처음 5개 키만 출력
                print(f"  - {key}")
        elif isinstance(live_data, list):
            print(f"항목 개수: {len(live_data)}")
            if len(live_data) > 0:
                print(f"첫 번째 항목: {live_data[0]}")
    
    print("\n" + "="*60)
    
    # 3. 가격 피드 데이터 가져오기
    print("\n=== 3단계: 가격 피드 데이터 ===")
    price_data = fetcher.get_price_feeds()
    
    if price_data:
        print(f"\n가격 피드 데이터 구조:")
        print(f"타입: {type(price_data)}")
        if isinstance(price_data, dict):
            print(f"키 개수: {len(price_data)}")
            for key in list(price_data.keys())[:5]:
                print(f"  - {key}")
        elif isinstance(price_data, list):
            print(f"항목 개수: {len(price_data)}")
            if len(price_data) > 0:
                print(f"첫 번째 항목: {price_data[0]}")
    
    print("\n" + "="*60)
    
    # 4. 심볼 추출
    print("\n=== 4단계: 심볼 추출 ===")
    
    all_symbols = []
    
    if live_data:
        live_symbols = fetcher.get_symbols_from_live_data(live_data)
        print(f"실시간 데이터에서 {len(live_symbols)}개의 심볼 추출:")
        for symbol in live_symbols:
            print(f"  - {symbol}")
        all_symbols.extend(live_symbols)
    
    if price_data:
        price_symbols = fetcher.get_symbols_from_live_data(price_data)
        print(f"\n가격 피드에서 {len(price_symbols)}개의 심볼 추출:")
        for symbol in price_symbols:
            print(f"  - {symbol}")
        all_symbols.extend(price_symbols)
    
    # 중복 제거
    unique_symbols = list(set(all_symbols))
    
    if unique_symbols:
        print(f"\n✅ 총 {len(unique_symbols)}개의 고유한 심볼을 찾았습니다!")
        print("\n전체 심볼 목록:")
        for i, symbol in enumerate(sorted(unique_symbols), 1):
            print(f"{i:3d}. {symbol}")
    else:
        print("\n❌ 심볼을 추출할 수 없었습니다.")
    
    print("\n" + "="*60)
    
    # 5. 상세 정보 가져오기
    print("\n=== 5단계: 상세 정보 ===")
    detailed_data = fetcher.get_detailed_symbols()
    
    if detailed_data:
        print(f"\n✅ 상세 데이터를 성공적으로 가져왔습니다!")
        print("데이터 샘플을 확인하려면 코드를 수정하여 더 자세한 분석을 수행할 수 있습니다.")

if __name__ == "__main__":
    main() 