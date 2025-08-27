#!/usr/bin/env python3
"""
PYTH Network 퍼블리셔 리스트 API 확인
공식 API에서 퍼블리셔 정보를 직접 제공하는지 확인
"""

import requests
import json
import time
from typing import Dict, List, Optional

class PythPublisherAPIChecker:
    def __init__(self):
        self.base_urls = [
            "https://hermes.pyth.network",
            "https://api.pyth.network", 
            "https://xc-mainnet.pyth.network"
        ]
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def test_publisher_endpoints(self) -> Dict:
        """퍼블리셔 관련 API 엔드포인트들을 테스트합니다."""
        print("=== PYTH Network 퍼블리셔 API 엔드포인트 테스트 ===\n")
        
        results = {}
        
        # 테스트할 엔드포인트들
        endpoints_to_test = [
            # 기본 API 엔드포인트들
            "/v2/publishers",
            "/api/publishers", 
            "/publishers",
            "/v1/publishers",
            
            # 퍼블리셔 정보 관련
            "/v2/publisher/list",
            "/api/publisher/list",
            "/publisher/list",
            
            # 퍼블리셔 상세 정보
            "/v2/publishers/details",
            "/api/publishers/details",
            "/publishers/details",
            
            # 퍼블리셔 통계
            "/v2/publishers/stats",
            "/api/publishers/stats", 
            "/publishers/stats",
            
            # 퍼블리셔 피드 정보
            "/v2/publishers/feeds",
            "/api/publishers/feeds",
            "/publishers/feeds",
            
            # 퍼블리셔 메타데이터
            "/v2/publishers/metadata",
            "/api/publishers/metadata",
            "/publishers/metadata",
            
            # 퍼블리셔 검증
            "/v2/publishers/validators",
            "/api/publishers/validators",
            "/publishers/validators",
            
            # 퍼블리셔 상태
            "/v2/publishers/status",
            "/api/publishers/status",
            "/publishers/status",
            
            # 퍼블리셔 등록
            "/v2/publishers/registry",
            "/api/publishers/registry", 
            "/publishers/registry",
            
            # 퍼블리셔 권한
            "/v2/publishers/authority",
            "/api/publishers/authority",
            "/publishers/authority",
            
            # 퍼블리셔 설정
            "/v2/publishers/config",
            "/api/publishers/config",
            "/publishers/config",
            
            # 퍼블리셔 네트워크
            "/v2/publishers/network",
            "/api/publishers/network",
            "/publishers/network"
        ]
        
        for base_url in self.base_urls:
            print(f"🔍 {base_url} 테스트 중...")
            results[base_url] = {}
            
            for endpoint in endpoints_to_test:
                url = f"{base_url}{endpoint}"
                try:
                    response = self.session.get(url, timeout=10)
                    status = response.status_code
                    
                    if status == 200:
                        try:
                            data = response.json()
                            results[base_url][endpoint] = {
                                'status': status,
                                'data_type': type(data).__name__,
                                'data_preview': str(data)[:200] + "..." if len(str(data)) > 200 else str(data),
                                'has_publishers': self._check_for_publishers(data)
                            }
                            print(f"  ✅ {endpoint}: {status} - 퍼블리셔 정보 발견!")
                        except json.JSONDecodeError:
                            results[base_url][endpoint] = {
                                'status': status,
                                'data_type': 'text',
                                'data_preview': response.text[:200] + "..." if len(response.text) > 200 else response.text,
                                'has_publishers': False
                            }
                            print(f"  ⚠️  {endpoint}: {status} - JSON 아님")
                    else:
                        results[base_url][endpoint] = {
                            'status': status,
                            'data_type': 'error',
                            'data_preview': f"HTTP {status}",
                            'has_publishers': False
                        }
                        print(f"  ❌ {endpoint}: {status}")
                        
                except requests.exceptions.RequestException as e:
                    results[base_url][endpoint] = {
                        'status': 'error',
                        'data_type': 'exception',
                        'data_preview': str(e),
                        'has_publishers': False
                    }
                    print(f"  💥 {endpoint}: 연결 실패 - {e}")
                
                time.sleep(0.1)  # API 호출 간격 조절
            
            print()
        
        return results
    
    def _check_for_publishers(self, data) -> bool:
        """데이터에 퍼블리셔 정보가 포함되어 있는지 확인합니다."""
        if isinstance(data, dict):
            # 퍼블리셔 관련 키워드 검색
            publisher_keywords = ['publisher', 'publishers', 'authority', 'authorities', 'validator', 'validators']
            for key in data.keys():
                if any(keyword in key.lower() for keyword in publisher_keywords):
                    return True
            
            # 값에서도 검색
            for value in data.values():
                if self._check_for_publishers(value):
                    return True
                    
        elif isinstance(data, list):
            for item in data:
                if self._check_for_publishers(item):
                    return True
        
        return False
    
    def check_known_endpoints(self) -> Dict:
        """알려진 PYTH API 엔드포인트에서 퍼블리셔 정보를 찾습니다."""
        print("=== 알려진 PYTH API 엔드포인트에서 퍼블리셔 정보 검색 ===\n")
        
        known_endpoints = [
            "/v2/price_feeds",
            "/v2/updates/price/latest",
            "/api/latest_vaas",
            "/v2/price_feeds/current",
            "/v2/price_feeds/history",
            "/v2/price_feeds/aggregate",
            "/v2/price_feeds/status",
            "/v2/price_feeds/metadata",
            "/v2/price_feeds/config",
            "/v2/price_feeds/network",
            "/v2/price_feeds/validators",
            "/v2/price_feeds/authority",
            "/v2/price_feeds/publishers",
            "/v2/price_feeds/sources",
            "/v2/price_feeds/providers"
        ]
        
        results = {}
        
        for base_url in self.base_urls:
            print(f"🔍 {base_url} 알려진 엔드포인트 검색 중...")
            results[base_url] = {}
            
            for endpoint in known_endpoints:
                url = f"{base_url}{endpoint}"
                try:
                    response = self.session.get(url, timeout=10)
                    status = response.status_code
                    
                    if status == 200:
                        try:
                            data = response.json()
                            has_publishers = self._check_for_publishers(data)
                            results[base_url][endpoint] = {
                                'status': status,
                                'has_publishers': has_publishers,
                                'publisher_info': self._extract_publisher_info(data) if has_publishers else None
                            }
                            
                            if has_publishers:
                                print(f"  ✅ {endpoint}: 퍼블리셔 정보 발견!")
                            else:
                                print(f"  ⚠️  {endpoint}: 퍼블리셔 정보 없음")
                                
                        except json.JSONDecodeError:
                            results[base_url][endpoint] = {
                                'status': status,
                                'has_publishers': False,
                                'publisher_info': None
                            }
                            print(f"  ❌ {endpoint}: JSON 파싱 실패")
                    else:
                        results[base_url][endpoint] = {
                            'status': status,
                            'has_publishers': False,
                            'publisher_info': None
                        }
                        print(f"  ❌ {endpoint}: HTTP {status}")
                        
                except requests.exceptions.RequestException as e:
                    results[base_url][endpoint] = {
                        'status': 'error',
                        'has_publishers': False,
                        'publisher_info': None
                    }
                    print(f"  💥 {endpoint}: 연결 실패")
                
                time.sleep(0.1)
            
            print()
        
        return results
    
    def _extract_publisher_info(self, data) -> Dict:
        """데이터에서 퍼블리셔 정보를 추출합니다."""
        publisher_info = {
            'publishers': [],
            'publisher_count': 0,
            'publisher_keys': [],
            'publisher_names': []
        }
        
        if isinstance(data, dict):
            # 퍼블리셔 관련 키 찾기
            for key, value in data.items():
                if 'publisher' in key.lower():
                    if isinstance(value, list):
                        publisher_info['publishers'].extend(value)
                        publisher_info['publisher_count'] += len(value)
                    elif isinstance(value, dict):
                        publisher_info['publishers'].append(value)
                        publisher_info['publisher_count'] += 1
                    elif isinstance(value, str):
                        publisher_info['publisher_keys'].append(value)
                        publisher_info['publisher_count'] += 1
        
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    item_info = self._extract_publisher_info(item)
                    publisher_info['publishers'].extend(item_info['publishers'])
                    publisher_info['publisher_count'] += item_info['publisher_count']
                    publisher_info['publisher_keys'].extend(item_info['publisher_keys'])
        
        return publisher_info
    
    def check_documentation_apis(self) -> Dict:
        """PYTH 문서나 메타데이터 API를 확인합니다."""
        print("=== PYTH 문서 및 메타데이터 API 확인 ===\n")
        
        doc_endpoints = [
            "/docs",
            "/api/docs",
            "/v2/docs",
            "/swagger",
            "/api/swagger",
            "/v2/swagger",
            "/openapi",
            "/api/openapi",
            "/v2/openapi",
            "/metadata",
            "/api/metadata",
            "/v2/metadata",
            "/info",
            "/api/info",
            "/v2/info",
            "/health",
            "/api/health",
            "/v2/health",
            "/status",
            "/api/status",
            "/v2/status"
        ]
        
        results = {}
        
        for base_url in self.base_urls:
            print(f"🔍 {base_url} 문서 API 확인 중...")
            results[base_url] = {}
            
            for endpoint in doc_endpoints:
                url = f"{base_url}{endpoint}"
                try:
                    response = self.session.get(url, timeout=10)
                    status = response.status_code
                    
                    if status == 200:
                        content_type = response.headers.get('content-type', '')
                        
                        if 'json' in content_type:
                            try:
                                data = response.json()
                                results[base_url][endpoint] = {
                                    'status': status,
                                    'content_type': content_type,
                                    'has_publisher_info': self._check_for_publishers(data),
                                    'preview': str(data)[:300] + "..." if len(str(data)) > 300 else str(data)
                                }
                                print(f"  ✅ {endpoint}: JSON 응답")
                            except json.JSONDecodeError:
                                results[base_url][endpoint] = {
                                    'status': status,
                                    'content_type': content_type,
                                    'has_publisher_info': False,
                                    'preview': 'JSON 파싱 실패'
                                }
                                print(f"  ❌ {endpoint}: JSON 파싱 실패")
                        else:
                            results[base_url][endpoint] = {
                                'status': status,
                                'content_type': content_type,
                                'has_publisher_info': False,
                                'preview': response.text[:300] + "..." if len(response.text) > 300 else response.text
                            }
                            print(f"  📄 {endpoint}: {content_type}")
                    else:
                        results[base_url][endpoint] = {
                            'status': status,
                            'content_type': 'error',
                            'has_publisher_info': False,
                            'preview': f"HTTP {status}"
                        }
                        print(f"  ❌ {endpoint}: HTTP {status}")
                        
                except requests.exceptions.RequestException as e:
                    results[base_url][endpoint] = {
                        'status': 'error',
                        'content_type': 'exception',
                        'has_publisher_info': False,
                        'preview': str(e)
                    }
                    print(f"  💥 {endpoint}: 연결 실패")
                
                time.sleep(0.1)
            
            print()
        
        return results
    
    def print_summary(self, results: Dict):
        """결과 요약을 출력합니다."""
        print("=== API 검색 결과 요약 ===\n")
        
        publisher_apis_found = []
        
        for base_url, endpoints in results.items():
            print(f"🌐 {base_url}")
            
            for endpoint, info in endpoints.items():
                if info.get('has_publishers', False):
                    publisher_apis_found.append(f"{base_url}{endpoint}")
                    print(f"  ✅ {endpoint}: 퍼블리셔 정보 발견")
                elif info.get('status') == 200:
                    print(f"  ⚠️  {endpoint}: 응답 있음 (퍼블리셔 정보 없음)")
                else:
                    print(f"  ❌ {endpoint}: {info.get('status', 'error')}")
            
            print()
        
        if publisher_apis_found:
            print("🎉 퍼블리셔 정보를 제공하는 API 발견:")
            for api in publisher_apis_found:
                print(f"  📡 {api}")
        else:
            print("😞 퍼블리셔 정보를 직접 제공하는 공식 API를 찾을 수 없습니다.")
            print("💡 VAA 데이터를 파싱하는 것이 현재 유일한 방법입니다.")

def main():
    checker = PythPublisherAPIChecker()
    
    # 1. 퍼블리셔 전용 API 엔드포인트 테스트
    print("1단계: 퍼블리셔 전용 API 엔드포인트 테스트")
    publisher_endpoints = checker.test_publisher_endpoints()
    
    # 2. 알려진 API에서 퍼블리셔 정보 검색
    print("2단계: 알려진 API에서 퍼블리셔 정보 검색")
    known_endpoints = checker.check_known_endpoints()
    
    # 3. 문서 및 메타데이터 API 확인
    print("3단계: 문서 및 메타데이터 API 확인")
    doc_apis = checker.check_documentation_apis()
    
    # 4. 결과 요약
    print("4단계: 결과 요약")
    all_results = {
        'publisher_endpoints': publisher_endpoints,
        'known_endpoints': known_endpoints,
        'doc_apis': doc_apis
    }
    
    checker.print_summary(all_results)
    
    # 5. 결과 저장
    with open('pyth_publisher_api_check_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 상세 결과가 'pyth_publisher_api_check_results.json'에 저장되었습니다.")

if __name__ == "__main__":
    main() 