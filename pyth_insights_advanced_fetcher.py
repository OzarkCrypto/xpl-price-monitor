#!/usr/bin/env python3
"""
PYTH Insights 고급 퍼블리셔 정보 가져오기
React 앱의 실제 데이터 API를 찾아서 퍼블리셔 정보를 가져옵니다.
"""

import requests
import json
import time
import re
from typing import Dict, List, Optional

class PythInsightsAdvancedFetcher:
    def __init__(self):
        self.base_url = "https://insights.pyth.network"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://insights.pyth.network/',
            'Origin': 'https://insights.pyth.network',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Connection': 'keep-alive'
        })
    
    def get_webpage_content(self, page: int = 1) -> str:
        """웹페이지 내용을 가져옵니다."""
        url = f"{self.base_url}/publishers?page={page}"
        
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                return response.text
            else:
                print(f"❌ 페이지 {page} 로드 실패: HTTP {response.status_code}")
                return ""
        except requests.exceptions.RequestException as e:
            print(f"💥 페이지 {page} 연결 실패: {e}")
            return ""
    
    def find_data_in_html(self, html_content: str) -> List[Dict]:
        """HTML에서 퍼블리셔 데이터를 찾습니다."""
        publishers = []
        
        # 1. JSON 데이터가 포함된 스크립트 태그 찾기
        script_patterns = [
            r'<script[^>]*>.*?window\.__INITIAL_STATE__\s*=\s*({.*?});.*?</script>',
            r'<script[^>]*>.*?window\.__NEXT_DATA__\s*=\s*({.*?});.*?</script>',
            r'<script[^>]*>.*?window\.__PRELOADED_STATE__\s*=\s*({.*?});.*?</script>',
            r'<script[^>]*>.*?publishers\s*:\s*(\[.*?\])',
            r'<script[^>]*>.*?data\s*:\s*(\[.*?\])',
            r'<script[^>]*>.*?({.*?"publishers".*?})',
            r'<script[^>]*>.*?({.*?"ranking".*?})',
            r'<script[^>]*>.*?({.*?"active".*?})'
        ]
        
        for pattern in script_patterns:
            matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    data = json.loads(match)
                    if self._is_publisher_data(data):
                        publishers.extend(self._extract_publishers_from_data(data))
                except json.JSONDecodeError:
                    pass
        
        # 2. 인라인 JSON 데이터 찾기
        json_patterns = [
            r'publishers\s*:\s*(\[.*?\])',
            r'data\s*:\s*(\[.*?\])',
            r'ranking\s*:\s*(\[.*?\])',
            r'active\s*:\s*(\[.*?\])'
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    data = json.loads(match)
                    if isinstance(data, list) and data:
                        publishers.extend(self._extract_publishers_from_data(data))
                except json.JSONDecodeError:
                    pass
        
        # 3. 테이블 데이터 파싱
        table_publishers = self._parse_table_data(html_content)
        publishers.extend(table_publishers)
        
        return publishers
    
    def _parse_table_data(self, html_content: str) -> List[Dict]:
        """HTML 테이블에서 퍼블리셔 데이터를 파싱합니다."""
        publishers = []
        
        # 테이블 행 찾기
        table_row_pattern = r'<tr[^>]*>.*?</tr>'
        rows = re.findall(table_row_pattern, html_content, re.DOTALL | re.IGNORECASE)
        
        for row in rows:
            # 테이블 셀 데이터 추출
            cell_pattern = r'<td[^>]*>(.*?)</td>'
            cells = re.findall(cell_pattern, row, re.DOTALL | re.IGNORECASE)
            
            if len(cells) >= 5:  # 최소 5개 컬럼이 있어야 함
                try:
                    # HTML 태그 제거
                    clean_cells = []
                    for cell in cells:
                        clean_cell = re.sub(r'<[^>]+>', '', cell).strip()
                        clean_cells.append(clean_cell)
                    
                    # 퍼블리셔 정보 구성
                    if clean_cells[0] and clean_cells[0] != 'Loading':
                        publisher = {
                            'ranking': self._extract_number(clean_cells[0]),
                            'name': clean_cells[1] if len(clean_cells) > 1 else 'Unknown',
                            'permissioned_feeds': self._extract_number(clean_cells[2]) if len(clean_cells) > 2 else 0,
                            'active_feeds': self._extract_number(clean_cells[3]) if len(clean_cells) > 3 else 0,
                            'average_score': self._extract_float(clean_cells[4]) if len(clean_cells) > 4 else 0.0
                        }
                        publishers.append(publisher)
                        
                except Exception as e:
                    continue
        
        return publishers
    
    def _extract_number(self, text: str) -> int:
        """텍스트에서 숫자를 추출합니다."""
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else 0
    
    def _extract_float(self, text: str) -> float:
        """텍스트에서 소수점 숫자를 추출합니다."""
        numbers = re.findall(r'\d+\.?\d*', text)
        return float(numbers[0]) if numbers else 0.0
    
    def _is_publisher_data(self, data) -> bool:
        """데이터가 퍼블리셔 정보인지 확인합니다."""
        if isinstance(data, dict):
            publisher_keywords = ['publishers', 'publisher', 'ranking', 'active', 'permissioned', 'score']
            for key in data.keys():
                if any(keyword in str(key).lower() for keyword in publisher_keywords):
                    return True
        elif isinstance(data, list):
            if data and isinstance(data[0], dict):
                first_item = data[0]
                publisher_fields = ['name', 'id', 'ranking', 'active', 'permissioned', 'score']
                if any(field in first_item for field in publisher_fields):
                    return True
        return False
    
    def _extract_publishers_from_data(self, data) -> List[Dict]:
        """데이터에서 퍼블리셔 정보를 추출합니다."""
        publishers = []
        
        if isinstance(data, dict):
            # publishers 키가 있는 경우
            if 'publishers' in data:
                publishers.extend(self._extract_publishers_from_data(data['publishers']))
            # data 키가 있는 경우
            elif 'data' in data:
                publishers.extend(self._extract_publishers_from_data(data['data']))
            # 직접 퍼블리셔 정보인 경우
            elif self._is_publisher_data(data):
                publishers.append(data)
                
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    if self._is_publisher_data(item):
                        publishers.append(item)
                    else:
                        # 중첩된 데이터 검색
                        nested = self._extract_publishers_from_data(item)
                        publishers.extend(nested)
        
        return publishers
    
    def try_graphql_endpoint(self) -> List[Dict]:
        """GraphQL 엔드포인트를 시도합니다."""
        print("🔍 GraphQL 엔드포인트 시도 중...")
        
        graphql_endpoints = [
            "/graphql",
            "/api/graphql",
            "/v1/graphql",
            "/v2/graphql"
        ]
        
        for endpoint in graphql_endpoints:
            url = f"{self.base_url}{endpoint}"
            
            # GraphQL 쿼리
            query = """
            query GetPublishers {
                publishers {
                    id
                    name
                    ranking
                    activeFeeds
                    permissionedFeeds
                    averageScore
                    cluster
                    status
                }
            }
            """
            
            try:
                response = self.session.post(url, json={'query': query}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and 'publishers' in data['data']:
                        print(f"  ✅ GraphQL 데이터 발견: {endpoint}")
                        return data['data']['publishers']
            except Exception as e:
                print(f"  ❌ GraphQL 실패: {endpoint} - {e}")
        
        return []
    
    def try_rest_api_with_params(self) -> List[Dict]:
        """파라미터가 있는 REST API를 시도합니다."""
        print("🔍 REST API 파라미터 시도 중...")
        
        # 다양한 파라미터 조합 시도
        params_combinations = [
            {'page': 1, 'limit': 100},
            {'page': 1, 'size': 100},
            {'page': 1, 'per_page': 100},
            {'offset': 0, 'limit': 100},
            {'start': 0, 'count': 100},
            {'page': 1},
            {'limit': 100},
            {}
        ]
        
        # 가능한 엔드포인트들
        endpoints = [
            "/api/publishers",
            "/api/v1/publishers",
            "/api/v2/publishers",
            "/api/data/publishers",
            "/api/insights/publishers",
            "/api/stats/publishers"
        ]
        
        for endpoint in endpoints:
            for params in params_combinations:
                url = f"{self.base_url}{endpoint}"
                
                try:
                    response = self.session.get(url, params=params, timeout=10)
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            if self._is_publisher_data(data):
                                print(f"  ✅ REST API 데이터 발견: {endpoint} with {params}")
                                return self._extract_publishers_from_data(data)
                        except json.JSONDecodeError:
                            pass
                except Exception as e:
                    continue
        
        return []
    
    def fetch_all_publishers(self) -> Dict:
        """모든 방법을 시도하여 퍼블리셔 정보를 가져옵니다."""
        print("🚀 PYTH Insights에서 퍼블리셔 정보 가져오기 시작...")
        
        all_publishers = []
        
        # 1. GraphQL 시도
        graphql_publishers = self.try_graphql_endpoint()
        if graphql_publishers:
            all_publishers.extend(graphql_publishers)
            print(f"✅ GraphQL에서 {len(graphql_publishers)}개 퍼블리셔 발견")
        
        # 2. REST API 시도
        rest_publishers = self.try_rest_api_with_params()
        if rest_publishers:
            all_publishers.extend(rest_publishers)
            print(f"✅ REST API에서 {len(rest_publishers)}개 퍼블리셔 발견")
        
        # 3. 웹페이지 파싱 시도
        if not all_publishers:
            print("🌐 웹페이지 파싱 시도 중...")
            for page in range(1, 5):  # 4페이지까지 시도
                html_content = self.get_webpage_content(page)
                if html_content:
                    page_publishers = self.find_data_in_html(html_content)
                    if page_publishers:
                        all_publishers.extend(page_publishers)
                        print(f"  ✅ 페이지 {page}에서 {len(page_publishers)}개 퍼블리셔 발견")
                    else:
                        print(f"  ⚠️  페이지 {page}에서 퍼블리셔 정보 없음")
                        if page > 1:  # 첫 페이지가 아니면 중단
                            break
                else:
                    break
                
                time.sleep(1)
        
        # 중복 제거
        unique_publishers = []
        seen_ids = set()
        
        for pub in all_publishers:
            pub_id = pub.get('id', pub.get('name', ''))
            if pub_id not in seen_ids:
                seen_ids.add(pub_id)
                unique_publishers.append(pub)
        
        return {
            'publishers': unique_publishers,
            'total_count': len(unique_publishers),
            'source': 'multiple_sources',
            'raw_data': all_publishers
        }
    
    def save_results(self, data: Dict, filename: str = "pyth_insights_publishers_advanced.json"):
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
                        pub.get('active_feeds', pub.get('activeFeeds', '')),
                        pub.get('permissioned_feeds', pub.get('permissionedFeeds', '')),
                        pub.get('average_score', pub.get('averageScore', '')),
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
                print(f"    Active: {pub.get('active_feeds', pub.get('activeFeeds', 0))}, Permissioned: {pub.get('permissioned_feeds', pub.get('permissionedFeeds', 0))}")
                print(f"    Score: {pub.get('average_score', pub.get('averageScore', 0)):.2f}, Cluster: {pub.get('cluster', 'Unknown')}")
                print()
        else:
            print("❌ 퍼블리셔 정보를 가져올 수 없습니다.")

def main():
    fetcher = PythInsightsAdvancedFetcher()
    
    # 모든 방법으로 퍼블리셔 정보 가져오기
    publishers_data = fetcher.fetch_all_publishers()
    
    # 결과 출력
    fetcher.print_summary(publishers_data)
    
    # 결과 저장
    if publishers_data.get('publishers'):
        fetcher.save_results(publishers_data)
    else:
        print("❌ 저장할 데이터가 없습니다.")

if __name__ == "__main__":
    main() 