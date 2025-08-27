#!/usr/bin/env python3
"""
PYTH Insights 퍼블리셔 정보 가져오기
https://insights.pyth.network/publishers 에서 실제 퍼블리셔 정보를 가져옵니다.
"""

import requests
import json
import time
from typing import Dict, List, Optional

class PythInsightsPublisherFetcher:
    def __init__(self):
        self.base_url = "https://insights.pyth.network"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://insights.pyth.network/',
            'Origin': 'https://insights.pyth.network'
        })
    
    def get_publishers_api_endpoint(self) -> Optional[str]:
        """PYTH Insights의 퍼블리셔 API 엔드포인트를 찾습니다."""
        print("🔍 PYTH Insights API 엔드포인트 찾는 중...")
        
        # 가능한 API 엔드포인트들
        possible_endpoints = [
            "/api/publishers",
            "/api/v1/publishers", 
            "/api/v2/publishers",
            "/api/publishers/list",
            "/api/publishers/active",
            "/api/publishers/all",
            "/api/publishers/ranking",
            "/api/publishers/stats",
            "/api/publishers/details",
            "/api/publishers/metadata",
            "/api/publishers/summary",
            "/api/publishers/overview",
            "/api/publishers/feed",
            "/api/publishers/data",
            "/api/publishers/info"
        ]
        
        for endpoint in possible_endpoints:
            url = f"{self.base_url}{endpoint}"
            try:
                response = self.session.get(url, timeout=10)
                print(f"  테스트: {endpoint} - {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if self._is_publisher_data(data):
                            print(f"  ✅ 퍼블리셔 데이터 발견: {endpoint}")
                            return endpoint
                    except json.JSONDecodeError:
                        pass
                        
            except requests.exceptions.RequestException as e:
                print(f"  ❌ 연결 실패: {endpoint} - {e}")
        
        return None
    
    def _is_publisher_data(self, data) -> bool:
        """데이터가 퍼블리셔 정보인지 확인합니다."""
        if isinstance(data, dict):
            # 퍼블리셔 관련 키워드 확인
            publisher_keywords = ['publishers', 'publisher', 'ranking', 'active', 'permissioned', 'score']
            for key in data.keys():
                if any(keyword in key.lower() for keyword in publisher_keywords):
                    return True
            
            # 값에서도 확인
            for value in data.values():
                if self._is_publisher_data(value):
                    return True
                    
        elif isinstance(data, list):
            # 리스트의 첫 번째 항목이 퍼블리셔 정보인지 확인
            if data and isinstance(data[0], dict):
                first_item = data[0]
                publisher_fields = ['name', 'id', 'ranking', 'active', 'permissioned', 'score']
                if any(field in first_item for field in publisher_fields):
                    return True
        
        return False
    
    def get_publishers_from_insights(self) -> Dict:
        """PYTH Insights에서 퍼블리셔 정보를 가져옵니다."""
        print("📊 PYTH Insights에서 퍼블리셔 정보 가져오는 중...")
        
        # 1. API 엔드포인트 찾기
        api_endpoint = self.get_publishers_api_endpoint()
        
        if api_endpoint:
            return self._fetch_from_api(api_endpoint)
        else:
            print("⚠️  API 엔드포인트를 찾을 수 없습니다. 웹페이지 파싱을 시도합니다.")
            return self._parse_webpage()
    
    def _fetch_from_api(self, endpoint: str) -> Dict:
        """API에서 퍼블리셔 정보를 가져옵니다."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self._process_publisher_data(data)
            else:
                print(f"❌ API 호출 실패: HTTP {response.status_code}")
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ API 연결 실패: {e}")
            return {}
    
    def _parse_webpage(self) -> Dict:
        """웹페이지에서 퍼블리셔 정보를 파싱합니다."""
        print("🌐 웹페이지 파싱 시도 중...")
        
        # 여러 페이지 시도
        publishers_data = []
        
        for page in range(1, 10):  # 최대 10페이지까지 시도
            url = f"{self.base_url}/publishers?page={page}"
            
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"  📄 페이지 {page} 로드 성공")
                    
                    # 페이지에서 퍼블리셔 정보 추출 시도
                    page_data = self._extract_publishers_from_html(response.text)
                    if page_data:
                        publishers_data.extend(page_data)
                        print(f"  ✅ 페이지 {page}에서 {len(page_data)}개 퍼블리셔 발견")
                    else:
                        print(f"  ⚠️  페이지 {page}에서 퍼블리셔 정보 없음")
                        break  # 더 이상 데이터가 없으면 중단
                else:
                    print(f"  ❌ 페이지 {page} 로드 실패: HTTP {response.status_code}")
                    break
                    
            except requests.exceptions.RequestException as e:
                print(f"  💥 페이지 {page} 연결 실패: {e}")
                break
            
            time.sleep(1)  # 요청 간격 조절
        
        return {
            'publishers': publishers_data,
            'total_count': len(publishers_data),
            'source': 'webpage_parsing'
        }
    
    def _extract_publishers_from_html(self, html_content: str) -> List[Dict]:
        """HTML에서 퍼블리셔 정보를 추출합니다."""
        publishers = []
        
        # 간단한 텍스트 파싱 (실제로는 더 정교한 파싱이 필요할 수 있음)
        lines = html_content.split('\n')
        
        for line in lines:
            # 퍼블리셔 관련 정보가 포함된 라인 찾기
            if any(keyword in line.lower() for keyword in ['publisher', 'ranking', 'active', 'permissioned']):
                # JSON 형태의 데이터 찾기
                if '{' in line and '}' in line:
                    try:
                        # JSON 부분 추출
                        start = line.find('{')
                        end = line.rfind('}') + 1
                        json_str = line[start:end]
                        data = json.loads(json_str)
                        
                        if self._is_publisher_data(data):
                            if isinstance(data, list):
                                publishers.extend(data)
                            else:
                                publishers.append(data)
                                
                    except json.JSONDecodeError:
                        pass
        
        return publishers
    
    def _process_publisher_data(self, data) -> Dict:
        """퍼블리셔 데이터를 처리합니다."""
        if isinstance(data, dict):
            # 통계 정보가 포함된 경우
            if 'publishers' in data:
                publishers = data['publishers']
            elif 'data' in data:
                publishers = data['data']
            else:
                publishers = data
                
        elif isinstance(data, list):
            publishers = data
        else:
            publishers = []
        
        # 퍼블리셔 정보 정리
        processed_publishers = []
        
        for pub in publishers:
            if isinstance(pub, dict):
                processed_pub = {
                    'name': pub.get('name', pub.get('id', 'Unknown')),
                    'id': pub.get('id', pub.get('publisher_id', 'Unknown')),
                    'ranking': pub.get('ranking', pub.get('rank', 0)),
                    'active_feeds': pub.get('active', pub.get('active_feeds', 0)),
                    'permissioned_feeds': pub.get('permissioned', pub.get('permissioned_feeds', 0)),
                    'average_score': pub.get('average_score', pub.get('score', 0)),
                    'cluster': pub.get('cluster', 'Unknown'),
                    'status': pub.get('status', 'active')
                }
                processed_publishers.append(processed_pub)
        
        return {
            'publishers': processed_publishers,
            'total_count': len(processed_publishers),
            'source': 'api',
            'raw_data': data
        }
    
    def save_results(self, data: Dict, filename: str = "pyth_insights_publishers.json"):
        """결과를 파일로 저장합니다."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 결과가 {filename}에 저장되었습니다.")
        
        # CSV로도 저장
        if data.get('publishers'):
            csv_filename = filename.replace('.json', '.csv')
            import csv
            
            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Ranking', 'Name', 'ID', 'Active Feeds', 'Permissioned Feeds', 'Average Score', 'Cluster', 'Status'])
                
                for pub in data['publishers']:
                    writer.writerow([
                        pub.get('ranking', ''),
                        pub.get('name', ''),
                        pub.get('id', ''),
                        pub.get('active_feeds', ''),
                        pub.get('permissioned_feeds', ''),
                        pub.get('average_score', ''),
                        pub.get('cluster', ''),
                        pub.get('status', '')
                    ])
            
            print(f"📊 CSV 파일도 {csv_filename}에 저장되었습니다.")
    
    def print_summary(self, data: Dict):
        """결과 요약을 출력합니다."""
        print("\n=== PYTH Insights 퍼블리셔 정보 요약 ===")
        
        if data.get('publishers'):
            publishers = data['publishers']
            total_count = data.get('total_count', len(publishers))
            source = data.get('source', 'unknown')
            
            print(f"📊 총 퍼블리셔 수: {total_count}")
            print(f"🔗 데이터 소스: {source}")
            print(f"📅 검색 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            print(f"\n=== 상위 10개 퍼블리셔 ===")
            sorted_publishers = sorted(publishers, key=lambda x: x.get('ranking', 999))
            
            for i, pub in enumerate(sorted_publishers[:10]):
                print(f"{i+1:2d}. {pub.get('name', 'Unknown')} (Rank: {pub.get('ranking', 'N/A')})")
                print(f"    Active: {pub.get('active_feeds', 0)}, Permissioned: {pub.get('permissioned_feeds', 0)}")
                print(f"    Score: {pub.get('average_score', 0):.2f}, Cluster: {pub.get('cluster', 'Unknown')}")
                print()
        else:
            print("❌ 퍼블리셔 정보를 가져올 수 없습니다.")

def main():
    fetcher = PythInsightsPublisherFetcher()
    
    # PYTH Insights에서 퍼블리셔 정보 가져오기
    publishers_data = fetcher.get_publishers_from_insights()
    
    # 결과 출력
    fetcher.print_summary(publishers_data)
    
    # 결과 저장
    if publishers_data.get('publishers'):
        fetcher.save_results(publishers_data)
    else:
        print("❌ 저장할 데이터가 없습니다.")

if __name__ == "__main__":
    main() 