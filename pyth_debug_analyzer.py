import requests
import json
from typing import List, Dict
import time

class PythDebugAnalyzer:
    def __init__(self):
        self.base_url = "https://hermes.pyth.network"
    
    def get_sample_price_data(self, limit=5):
        """
        샘플 가격 데이터를 가져와서 구조를 분석합니다.
        """
        print("🔍 샘플 가격 데이터 구조 분석...")
        
        # 먼저 피드 목록 가져오기
        try:
            url = f"{self.base_url}/v2/price_feeds"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                feeds = response.json()
                print(f"✅ {len(feeds)}개의 피드를 가져왔습니다.")
                
                # 처음 몇 개의 피드 ID만 사용
                sample_feed_ids = [feed['id'] for feed in feeds[:limit]]
                
                # 샘플 가격 데이터 가져오기
                url = f"{self.base_url}/v2/updates/price/latest"
                params = {'ids[]': sample_feed_ids}
                response = requests.get(url, params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ 샘플 가격 데이터를 가져왔습니다.")
                    return feeds[:limit], data
                else:
                    print(f"❌ 가격 데이터 가져오기 실패: {response.status_code}")
            else:
                print(f"❌ 피드 목록 가져오기 실패: {response.status_code}")
        except Exception as e:
            print(f"❌ 오류: {e}")
        
        return [], None
    
    def analyze_data_structure(self, feeds, price_data):
        """
        데이터 구조를 자세히 분석합니다.
        """
        print("\n📊 데이터 구조 분석:")
        print("="*60)
        
        print(f"\n1. 피드 데이터 구조 (첫 번째 피드):")
        if feeds:
            first_feed = feeds[0]
            print(f"피드 ID: {first_feed.get('id')}")
            print(f"Attributes: {json.dumps(first_feed.get('attributes', {}), indent=2)}")
        
        print(f"\n2. 가격 데이터 구조:")
        print(f"타입: {type(price_data)}")
        
        if isinstance(price_data, dict):
            print(f"키들: {list(price_data.keys())}")
            
            # parsed 키가 있는지 확인
            if 'parsed' in price_data:
                parsed_data = price_data['parsed']
                print(f"\n3. Parsed 데이터 구조:")
                print(f"타입: {type(parsed_data)}")
                
                if isinstance(parsed_data, list):
                    print(f"리스트 길이: {len(parsed_data)}")
                    if len(parsed_data) > 0:
                        first_item = parsed_data[0]
                        print(f"첫 번째 항목 타입: {type(first_item)}")
                        print(f"첫 번째 항목 키들: {list(first_item.keys()) if isinstance(first_item, dict) else 'N/A'}")
                        print(f"첫 번째 항목: {json.dumps(first_item, indent=2) if isinstance(first_item, dict) else first_item}")
                
                elif isinstance(parsed_data, dict):
                    print(f"키들: {list(parsed_data.keys())}")
                    print(f"전체 데이터: {json.dumps(parsed_data, indent=2)}")
            
            # binary 키가 있는지 확인
            if 'binary' in price_data:
                print(f"\n4. Binary 데이터 존재: {len(price_data['binary'])} bytes")
        
        elif isinstance(price_data, list):
            print(f"리스트 길이: {len(price_data)}")
            if len(price_data) > 0:
                first_item = price_data[0]
                print(f"첫 번째 항목 타입: {type(first_item)}")
                print(f"첫 번째 항목 키들: {list(first_item.keys()) if isinstance(first_item, dict) else 'N/A'}")
                print(f"첫 번째 항목: {json.dumps(first_item, indent=2) if isinstance(first_item, dict) else first_item}")
    
    def search_publisher_info(self, data, path=""):
        """
        데이터에서 퍼블리셔 정보를 재귀적으로 검색합니다.
        """
        publishers = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                # 퍼블리셔 관련 키 검색
                if 'publisher' in key.lower():
                    print(f"🔍 퍼블리셔 관련 키 발견: {current_path} = {value}")
                    publishers.append((current_path, value))
                
                # 재귀적으로 검색
                if isinstance(value, (dict, list)):
                    publishers.extend(self.search_publisher_info(value, current_path))
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                publishers.extend(self.search_publisher_info(item, current_path))
        
        return publishers
    
    def analyze_publisher_structure(self, price_data):
        """
        가격 데이터에서 퍼블리셔 구조를 분석합니다.
        """
        print(f"\n🔍 퍼블리셔 정보 검색:")
        print("="*60)
        
        publishers = self.search_publisher_info(price_data)
        
        if publishers:
            print(f"\n✅ {len(publishers)}개의 퍼블리셔 관련 정보를 발견했습니다:")
            for path, value in publishers:
                print(f"  {path}: {value}")
        else:
            print(f"\n❌ 퍼블리셔 관련 정보를 찾을 수 없었습니다.")
        
        return publishers
    
    def get_detailed_price_info(self, feed_id):
        """
        특정 피드 ID에 대한 상세 가격 정보를 가져옵니다.
        """
        print(f"\n🔍 피드 ID {feed_id}의 상세 정보:")
        print("="*60)
        
        try:
            # 최신 가격 정보
            url = f"{self.base_url}/v2/updates/price/latest"
            params = {'ids[]': [feed_id]}
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"최신 가격 정보:")
                print(json.dumps(data, indent=2))
                
                # 퍼블리셔 정보 검색
                publishers = self.search_publisher_info(data)
                if publishers:
                    print(f"\n퍼블리셔 정보:")
                    for path, value in publishers:
                        print(f"  {path}: {value}")
                else:
                    print(f"\n퍼블리셔 정보를 찾을 수 없습니다.")
            else:
                print(f"❌ 상세 정보 가져오기 실패: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 오류: {e}")

def main():
    """
    메인 실행 함수
    """
    print("🚀 Pyth Network 데이터 구조 디버깅\n")
    
    analyzer = PythDebugAnalyzer()
    
    # 1. 샘플 데이터 가져오기
    print("=== 1단계: 샘플 데이터 가져오기 ===")
    feeds, price_data = analyzer.get_sample_price_data(limit=3)
    
    if not feeds or not price_data:
        print("❌ 샘플 데이터를 가져올 수 없었습니다.")
        return
    
    # 2. 데이터 구조 분석
    print("\n=== 2단계: 데이터 구조 분석 ===")
    analyzer.analyze_data_structure(feeds, price_data)
    
    # 3. 퍼블리셔 정보 검색
    print("\n=== 3단계: 퍼블리셔 정보 검색 ===")
    publishers = analyzer.analyze_publisher_structure(price_data)
    
    # 4. 특정 피드의 상세 정보
    if feeds:
        print("\n=== 4단계: 특정 피드 상세 정보 ===")
        first_feed_id = feeds[0]['id']
        analyzer.get_detailed_price_info(first_feed_id)
    
    print(f"\n✅ 데이터 구조 분석 완료!")

if __name__ == "__main__":
    main() 