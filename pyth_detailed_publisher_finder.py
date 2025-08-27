import requests
import json
from typing import List, Dict
import time
import base64

class PythDetailedPublisherFinder:
    def __init__(self):
        self.base_url = "https://hermes.pyth.network"
    
    def get_all_price_feeds(self):
        """
        모든 가격 피드를 가져옵니다.
        """
        print("🔍 모든 가격 피드 가져오기...")
        
        try:
            url = f"{self.base_url}/v2/price_feeds"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {len(data)}개의 가격 피드를 가져왔습니다.")
                return data
            else:
                print(f"❌ 상태 코드: {response.status_code}")
        except Exception as e:
            print(f"❌ 오류: {e}")
        
        return []
    
    def get_detailed_price_info(self, feed_ids, limit=10):
        """
        특정 피드들의 상세 가격 정보를 가져옵니다.
        """
        print(f"💰 상세 가격 정보 가져오기 (최대 {limit}개)...")
        
        if not feed_ids:
            return []
        
        selected_ids = feed_ids[:limit]
        all_results = []
        
        for i, feed_id in enumerate(selected_ids, 1):
            print(f"  {i}/{len(selected_ids)}: {feed_id[:20]}...")
            
            try:
                # 다양한 파라미터로 시도
                params_list = [
                    {'ids[]': [feed_id]},
                    {'ids[]': [feed_id], 'verbose': 'true'},
                    {'ids[]': [feed_id], 'parsed': 'true'},
                    {'ids[]': [feed_id], 'encoding': 'hex'},
                    {'ids[]': [feed_id], 'encoding': 'base64'}
                ]
                
                for params in params_list:
                    try:
                        url = f"{self.base_url}/v2/updates/price/latest"
                        response = requests.get(url, params=params, timeout=10)
                        
                        if response.status_code == 200:
                            data = response.json()
                            print(f"    ✅ 성공 (파라미터: {params})")
                            
                            # 데이터 구조 자세히 분석
                            self.analyze_price_data_structure(data, feed_id)
                            
                            all_results.append({
                                'feed_id': feed_id,
                                'params': params,
                                'data': data
                            })
                            break
                        else:
                            print(f"    ❌ 실패 (파라미터: {params}) - {response.status_code}")
                            
                    except Exception as e:
                        print(f"    ❌ 오류 (파라미터: {params}): {e}")
                        continue
                
                time.sleep(0.5)  # API 요청 간격 조절
                
            except Exception as e:
                print(f"  ❌ 피드 {feed_id} 처리 오류: {e}")
                continue
        
        return all_results
    
    def analyze_price_data_structure(self, data, feed_id):
        """
        가격 데이터 구조를 자세히 분석합니다.
        """
        print(f"    📊 데이터 구조 분석:")
        print(f"      타입: {type(data)}")
        
        if isinstance(data, dict):
            print(f"      키들: {list(data.keys())}")
            
            # parsed 키 분석
            if 'parsed' in data:
                parsed_data = data['parsed']
                print(f"      Parsed 타입: {type(parsed_data)}")
                
                if isinstance(parsed_data, list) and len(parsed_data) > 0:
                    first_item = parsed_data[0]
                    print(f"      첫 번째 항목 키들: {list(first_item.keys()) if isinstance(first_item, dict) else 'N/A'}")
                    
                    # price_feed 구조 확인
                    if 'price_feed' in first_item:
                        price_feed = first_item['price_feed']
                        print(f"      Price Feed 키들: {list(price_feed.keys()) if isinstance(price_feed, dict) else 'N/A'}")
                        
                        # price_components 확인
                        if isinstance(price_feed, dict) and 'price_components' in price_feed:
                            components = price_feed['price_components']
                            print(f"      Price Components 타입: {type(components)}")
                            if isinstance(components, list):
                                print(f"      Components 개수: {len(components)}")
                                for j, component in enumerate(components[:3]):  # 처음 3개만
                                    print(f"        Component {j+1}: {component}")
            
            # binary 키 분석
            if 'binary' in data:
                binary_data = data['binary']
                print(f"      Binary 타입: {type(binary_data)}")
                if isinstance(binary_data, dict):
                    print(f"      Binary 키들: {list(binary_data.keys())}")
                    if 'data' in binary_data:
                        hex_data = binary_data['data']
                        print(f"      Hex 데이터 길이: {len(hex_data)}")
                        if isinstance(hex_data, list) and len(hex_data) > 0:
                            print(f"      Hex 샘플: {hex_data[0][:100]}...")
        
        elif isinstance(data, list):
            print(f"      리스트 길이: {len(data)}")
            if len(data) > 0:
                first_item = data[0]
                print(f"      첫 번째 항목 키들: {list(first_item.keys()) if isinstance(first_item, dict) else 'N/A'}")
    
    def search_publishers_in_data(self, data, feed_id):
        """
        데이터에서 퍼블리셔 정보를 상세히 검색합니다.
        """
        publishers = []
        
        def search_recursive(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # 퍼블리셔 관련 키 검색
                    if any(pub_key in key.lower() for pub_key in ['publisher', 'pub', 'authority', 'validator']):
                        print(f"🔍 퍼블리셔 관련 키 발견: {current_path} = {value}")
                        publishers.append((current_path, value))
                    
                    # 특정 퍼블리셔 이름 검색
                    if isinstance(value, str):
                        if any(pub_name in value.lower() for pub_name in ['amber', 'alphanonce', 'binance', 'coinbase']):
                            print(f"🔍 퍼블리셔 이름 발견: {current_path} = {value}")
                            publishers.append((current_path, value))
                    
                    # 재귀적으로 검색
                    if isinstance(value, (dict, list)):
                        search_recursive(value, current_path)
            
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]"
                    search_recursive(item, current_path)
        
        search_recursive(data)
        return publishers
    
    def try_vaa_parsing(self, feed_ids, limit=5):
        """
        VAA 파싱을 시도하여 퍼블리셔 정보를 찾습니다.
        """
        print(f"\n🔍 VAA 파싱 시도...")
        
        selected_ids = feed_ids[:limit]
        
        for i, feed_id in enumerate(selected_ids, 1):
            print(f"  {i}/{len(selected_ids)}: VAA 파싱 시도...")
            
            try:
                # VAA 데이터 가져오기
                url = f"{self.base_url}/api/latest_vaas"
                params = {'ids[]': [feed_id]}
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    vaa_data = response.json()
                    print(f"    ✅ VAA 데이터 가져옴")
                    
                    # VAA에서 퍼블리셔 검색
                    publishers = self.search_publishers_in_data(vaa_data, feed_id)
                    if publishers:
                        print(f"    ✅ VAA에서 퍼블리셔 발견: {len(publishers)}개")
                        for path, value in publishers:
                            print(f"      {path}: {value}")
                    else:
                        print(f"    ❌ VAA에서 퍼블리셔 정보 없음")
                        
                        # VAA 구조 분석
                        print(f"    📊 VAA 구조:")
                        if isinstance(vaa_data, list) and len(vaa_data) > 0:
                            first_vaa = vaa_data[0]
                            print(f"      VAA 타입: {type(first_vaa)}")
                            if isinstance(first_vaa, str):
                                print(f"      VAA 길이: {len(first_vaa)}")
                                print(f"      VAA 샘플: {first_vaa[:100]}...")
                                
                                # Base64 디코딩 시도
                                try:
                                    decoded = base64.b64decode(first_vaa)
                                    print(f"      디코딩된 길이: {len(decoded)} bytes")
                                    print(f"      디코딩된 샘플: {decoded[:50]}")
                                except:
                                    print(f"      Base64 디코딩 실패")
                else:
                    print(f"    ❌ VAA 가져오기 실패: {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ VAA 처리 오류: {e}")
    
    def try_stream_endpoint(self, feed_ids, limit=3):
        """
        Stream 엔드포인트를 시도합니다.
        """
        print(f"\n🔍 Stream 엔드포인트 시도...")
        
        selected_ids = feed_ids[:limit]
        
        for i, feed_id in enumerate(selected_ids, 1):
            print(f"  {i}/{len(selected_ids)}: Stream 시도...")
            
            try:
                url = f"{self.base_url}/v2/updates/price/stream"
                params = {
                    'ids[]': [feed_id],
                    'encoding': 'hex',
                    'parsed': 'true'
                }
                response = requests.get(url, params=params, timeout=5)
                
                print(f"    상태 코드: {response.status_code}")
                if response.status_code == 200:
                    print(f"    ✅ Stream 데이터 가져옴")
                    # Stream은 실시간 데이터이므로 짧게만 확인
                else:
                    print(f"    ❌ Stream 실패")
                    
            except Exception as e:
                print(f"    ❌ Stream 오류: {e}")

def main():
    """
    메인 실행 함수
    """
    print("🚀 Pyth Network 퍼블리셔 정보 상세 분석\n")
    
    finder = PythDetailedPublisherFinder()
    
    # 1. 모든 가격 피드 가져오기
    print("=== 1단계: 모든 가격 피드 가져오기 ===")
    all_feeds = finder.get_all_price_feeds()
    
    if not all_feeds:
        print("❌ 가격 피드를 가져올 수 없었습니다.")
        return
    
    # 2. 피드 ID 추출
    feed_ids = [feed['id'] for feed in all_feeds if 'id' in feed]
    print(f"✅ {len(feed_ids)}개의 피드 ID를 추출했습니다.")
    
    # 3. 상세 가격 정보 분석
    print("\n=== 2단계: 상세 가격 정보 분석 ===")
    detailed_results = finder.get_detailed_price_info(feed_ids, limit=10)
    
    # 4. 퍼블리셔 정보 검색
    print("\n=== 3단계: 퍼블리셔 정보 검색 ===")
    all_publishers = []
    
    for result in detailed_results:
        feed_id = result['feed_id']
        data = result['data']
        
        print(f"\n🔍 피드 {feed_id[:20]}... 에서 퍼블리셔 검색:")
        publishers = finder.search_publishers_in_data(data, feed_id)
        
        if publishers:
            print(f"✅ {len(publishers)}개의 퍼블리셔 관련 정보 발견!")
            all_publishers.extend(publishers)
            for path, value in publishers:
                print(f"  {path}: {value}")
        else:
            print(f"❌ 퍼블리셔 정보 없음")
    
    # 5. VAA 파싱 시도
    print("\n=== 4단계: VAA 파싱 시도 ===")
    finder.try_vaa_parsing(feed_ids, limit=5)
    
    # 6. Stream 엔드포인트 시도
    print("\n=== 5단계: Stream 엔드포인트 시도 ===")
    finder.try_stream_endpoint(feed_ids, limit=3)
    
    # 7. 결과 요약
    print(f"\n" + "="*80)
    print(f"📊 분석 결과 요약:")
    print(f"  • 분석한 피드 수: {len(detailed_results)}")
    print(f"  • 발견한 퍼블리셔 관련 정보: {len(all_publishers)}개")
    
    if all_publishers:
        print(f"\n🏆 발견한 퍼블리셔 관련 정보:")
        for path, value in all_publishers:
            print(f"  {path}: {value}")
    else:
        print(f"\n❌ 퍼블리셔 정보를 찾을 수 없었습니다.")
        print(f"💡 다른 방법을 시도해야 할 것 같습니다.")
    
    print(f"\n✅ Pyth Network 퍼블리셔 정보 상세 분석 완료!")

if __name__ == "__main__":
    main() 