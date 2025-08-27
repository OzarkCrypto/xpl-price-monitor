import requests
import json
from typing import List, Dict
import time

class PythRealAPIFetcher:
    def __init__(self):
        # Pyth Network의 실제 API 엔드포인트들
        self.api_endpoints = [
            "https://hermes.pyth.network",
            "https://api.pyth.network",
            "https://xc-mainnet.pyth.network"
        ]
    
    def test_api_endpoints(self):
        """
        모든 API 엔드포인트를 테스트하고 응답을 확인합니다.
        """
        print("🔍 API 엔드포인트 테스트 중...\n")
        
        for endpoint in self.api_endpoints:
            print(f"테스트 중: {endpoint}")
            
            # 다양한 경로들을 시도
            test_paths = [
                "/",
                "/api",
                "/api/price_feeds",
                "/api/v1/price_feeds",
                "/price_feeds",
                "/api/feeds",
                "/api/v1/feeds"
            ]
            
            for path in test_paths:
                try:
                    url = f"{endpoint}{path}"
                    print(f"  시도: {url}")
                    
                    response = requests.get(url, timeout=10)
                    print(f"    상태 코드: {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            print(f"    응답 타입: {type(data)}")
                            if isinstance(data, list):
                                print(f"    리스트 길이: {len(data)}")
                                if len(data) > 0:
                                    print(f"    첫 번째 항목: {data[0]}")
                            elif isinstance(data, dict):
                                print(f"    키들: {list(data.keys())}")
                        except:
                            print(f"    텍스트 응답: {response.text[:100]}...")
                    
                    print()
                    
                except Exception as e:
                    print(f"    오류: {str(e)[:50]}...")
                    print()
    
    def get_real_symbols_from_api(self) -> List[str]:
        """
        실제 API에서 심볼들을 가져옵니다.
        """
        print("🚀 실제 API에서 심볼 데이터 가져오기 시도...\n")
        
        for endpoint in self.api_endpoints:
            print(f"엔드포인트 시도: {endpoint}")
            
            # 다양한 API 경로들을 시도
            api_paths = [
                "/api/price_feeds",
                "/api/v1/price_feeds", 
                "/price_feeds",
                "/api/feeds",
                "/api/v1/feeds"
            ]
            
            for path in api_paths:
                try:
                    url = f"{endpoint}{path}"
                    print(f"  경로 시도: {path}")
                    
                    response = requests.get(url, timeout=15)
                    
                    if response.status_code == 200:
                        print(f"  ✅ 성공! 응답 분석 중...")
                        
                        data = response.json()
                        symbols = self.parse_api_response(data)
                        
                        if symbols:
                            print(f"  ✅ {len(symbols)}개의 심볼을 성공적으로 파싱했습니다!")
                            return symbols
                        else:
                            print(f"  ⚠️ 응답에서 심볼을 추출할 수 없습니다.")
                    else:
                        print(f"  ❌ 상태 코드: {response.status_code}")
                        
                except requests.exceptions.RequestException as e:
                    print(f"  ❌ 요청 오류: {str(e)[:50]}...")
                except json.JSONDecodeError as e:
                    print(f"  ❌ JSON 파싱 오류: {str(e)[:50]}...")
                except Exception as e:
                    print(f"  ❌ 기타 오류: {str(e)[:50]}...")
        
        print("❌ 모든 API 엔드포인트에서 데이터를 가져올 수 없었습니다.")
        return []
    
    def parse_api_response(self, data) -> List[str]:
        """
        API 응답에서 심볼들을 파싱합니다.
        """
        symbols = []
        
        print(f"  응답 데이터 타입: {type(data)}")
        
        if isinstance(data, list):
            print(f"  리스트 길이: {len(data)}")
            for i, item in enumerate(data[:3]):  # 처음 3개만 출력
                print(f"  항목 {i}: {item}")
            
            for item in data:
                symbol = self.extract_symbol_from_item(item)
                if symbol:
                    symbols.append(symbol)
                    
        elif isinstance(data, dict):
            print(f"  딕셔너리 키들: {list(data.keys())}")
            
            # data 키가 있는 경우
            if 'data' in data and isinstance(data['data'], list):
                for item in data['data']:
                    symbol = self.extract_symbol_from_item(item)
                    if symbol:
                        symbols.append(symbol)
            
            # feeds 키가 있는 경우
            elif 'feeds' in data and isinstance(data['feeds'], list):
                for item in data['feeds']:
                    symbol = self.extract_symbol_from_item(item)
                    if symbol:
                        symbols.append(symbol)
            
            # price_feeds 키가 있는 경우
            elif 'price_feeds' in data and isinstance(data['price_feeds'], list):
                for item in data['price_feeds']:
                    symbol = self.extract_symbol_from_item(item)
                    if symbol:
                        symbols.append(symbol)
        
        return list(set(symbols))  # 중복 제거
    
    def extract_symbol_from_item(self, item) -> str:
        """
        개별 항목에서 심볼을 추출합니다.
        """
        if not isinstance(item, dict):
            return None
        
        # 다양한 필드명에서 심볼 추출 시도
        symbol_fields = ['symbol', 'ticker', 'pair', 'name', 'id']
        
        for field in symbol_fields:
            if field in item and item[field]:
                value = str(item[field])
                # 심볼 형태인지 확인 (예: BTC/USD, ETH-USD 등)
                if '/' in value or '-' in value:
                    if len(value) < 20:  # 너무 긴 값은 제외
                        return value
        
        # metadata 내부에서도 확인
        if 'metadata' in item and isinstance(item['metadata'], dict):
            for field in symbol_fields:
                if field in item['metadata'] and item['metadata'][field]:
                    value = str(item['metadata'][field])
                    if '/' in value or '-' in value:
                        if len(value) < 20:
                            return value
        
        return None
    
    def get_symbols_with_details(self) -> List[Dict]:
        """
        심볼과 함께 상세 정보를 가져옵니다.
        """
        print("📊 심볼 상세 정보 가져오기...\n")
        
        for endpoint in self.api_endpoints:
            try:
                url = f"{endpoint}/api/price_feeds"
                response = requests.get(url, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    return self.parse_detailed_response(data)
                    
            except Exception as e:
                print(f"엔드포인트 {endpoint} 실패: {e}")
                continue
        
        return []
    
    def parse_detailed_response(self, data) -> List[Dict]:
        """
        상세 응답을 파싱합니다.
        """
        details = []
        
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    detail = {
                        'symbol': self.extract_symbol_from_item(item),
                        'id': item.get('id'),
                        'metadata': item.get('metadata', {}),
                        'raw_data': item
                    }
                    if detail['symbol']:
                        details.append(detail)
        
        return details

def main():
    """
    메인 실행 함수
    """
    print("🔍 Pyth Network 실제 API 데이터 가져오기\n")
    
    fetcher = PythRealAPIFetcher()
    
    # 1. API 엔드포인트 테스트
    print("=== 1단계: API 엔드포인트 테스트 ===")
    fetcher.test_api_endpoints()
    
    print("\n" + "="*60)
    
    # 2. 실제 심볼 데이터 가져오기
    print("\n=== 2단계: 실제 심볼 데이터 가져오기 ===")
    symbols = fetcher.get_real_symbols_from_api()
    
    if symbols:
        print(f"\n✅ 성공! 총 {len(symbols)}개의 실제 심볼을 가져왔습니다:\n")
        for i, symbol in enumerate(symbols, 1):
            print(f"{i:3d}. {symbol}")
    else:
        print("\n❌ 실제 API에서 심볼을 가져올 수 없었습니다.")
    
    print("\n" + "="*60)
    
    # 3. 상세 정보 가져오기
    print("\n=== 3단계: 상세 정보 가져오기 ===")
    details = fetcher.get_symbols_with_details()
    
    if details:
        print(f"\n✅ {len(details)}개의 상세 정보를 가져왔습니다:\n")
        for i, detail in enumerate(details[:5], 1):  # 처음 5개만 출력
            print(f"{i}. 심볼: {detail['symbol']}")
            print(f"   ID: {detail['id']}")
            print(f"   메타데이터: {detail['metadata']}")
            print()
    else:
        print("\n❌ 상세 정보를 가져올 수 없었습니다.")

if __name__ == "__main__":
    main() 