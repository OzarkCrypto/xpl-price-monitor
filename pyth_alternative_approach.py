#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
from typing import Dict, List, Any, Optional

class PythAlternativeApproach:
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
    
    def test_endpoints(self):
        """다양한 엔드포인트 테스트"""
        print("🔍 다양한 Pyth Network 엔드포인트 테스트...")
        
        endpoints_to_test = [
            "/v2/price_feeds",
            "/v2/updates/price/latest",
            "/api/latest_vaas",
            "/v2/price_feeds/current",
            "/v2/price_feeds/latest",
            "/api/price_feeds",
            "/api/feeds",
            "/v2/feeds",
            "/api/v2/price_feeds",
            "/api/v2/updates/price/latest"
        ]
        
        working_endpoints = []
        
        for base_url in self.base_urls:
            print(f"\n📍 {base_url} 테스트 중...")
            for endpoint in endpoints_to_test:
                try:
                    url = f"{base_url}{endpoint}"
                    print(f"  🔗 {endpoint} 시도...")
                    
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        print(f"    ✅ 성공! 상태코드: {response.status_code}")
                        working_endpoints.append((base_url, endpoint))
                        
                        # 응답 구조 분석
                        try:
                            data = response.json()
                            print(f"    📊 응답 타입: {type(data)}")
                            if isinstance(data, dict):
                                print(f"    📋 키들: {list(data.keys())[:10]}")
                            elif isinstance(data, list):
                                print(f"    📋 리스트 길이: {len(data)}")
                                if len(data) > 0:
                                    print(f"    📋 첫 번째 항목 타입: {type(data[0])}")
                        except:
                            print(f"    📊 JSON이 아닌 응답 (길이: {len(response.text)})")
                    else:
                        print(f"    ❌ 실패! 상태코드: {response.status_code}")
                        
                except Exception as e:
                    print(f"    ❌ 오류: {str(e)[:50]}")
                
                time.sleep(0.5)  # 요청 간격
        
        return working_endpoints
    
    def try_publisher_specific_endpoints(self):
        """퍼블리셔 관련 특정 엔드포인트 시도"""
        print("\n🔍 퍼블리셔 관련 특정 엔드포인트 시도...")
        
        publisher_endpoints = [
            "/v2/publishers",
            "/api/publishers", 
            "/v2/validators",
            "/api/validators",
            "/v2/authorities",
            "/api/authorities",
            "/v2/price_feeds/publishers",
            "/api/price_feeds/publishers",
            "/v2/updates/publishers",
            "/api/updates/publishers"
        ]
        
        for base_url in self.base_urls:
            print(f"\n📍 {base_url} 퍼블리셔 엔드포인트 테스트...")
            for endpoint in publisher_endpoints:
                try:
                    url = f"{base_url}{endpoint}"
                    print(f"  🔗 {endpoint} 시도...")
                    
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        print(f"    ✅ 성공! 상태코드: {response.status_code}")
                        try:
                            data = response.json()
                            print(f"    📊 응답 타입: {type(data)}")
                            if isinstance(data, dict):
                                print(f"    📋 키들: {list(data.keys())}")
                            elif isinstance(data, list):
                                print(f"    📋 리스트 길이: {len(data)}")
                                if len(data) > 0:
                                    print(f"    📋 첫 번째 항목: {data[0]}")
                        except:
                            print(f"    📊 JSON이 아닌 응답")
                    else:
                        print(f"    ❌ 실패! 상태코드: {response.status_code}")
                        
                except Exception as e:
                    print(f"    ❌ 오류: {str(e)[:50]}")
                
                time.sleep(0.5)
    
    def try_websocket_approach(self):
        """WebSocket 접근 방법 시도"""
        print("\n🔍 WebSocket 접근 방법 시도...")
        
        ws_endpoints = [
            "wss://hermes.pyth.network/ws",
            "wss://api.pyth.network/ws",
            "wss://xc-mainnet.pyth.network/ws"
        ]
        
        for ws_url in ws_endpoints:
            print(f"  🔗 {ws_url} 시도...")
            try:
                # WebSocket 연결 시도 (간단한 테스트)
                import websocket
                ws = websocket.create_connection(ws_url, timeout=5)
                print(f"    ✅ WebSocket 연결 성공!")
                ws.close()
            except ImportError:
                print(f"    ⚠️ websocket-client 라이브러리가 설치되지 않음")
                break
            except Exception as e:
                print(f"    ❌ WebSocket 연결 실패: {str(e)[:50]}")
    
    def try_graphql_approach(self):
        """GraphQL 접근 방법 시도"""
        print("\n🔍 GraphQL 접근 방법 시도...")
        
        graphql_endpoints = [
            "https://hermes.pyth.network/graphql",
            "https://api.pyth.network/graphql",
            "https://xc-mainnet.pyth.network/graphql"
        ]
        
        for gql_url in graphql_endpoints:
            print(f"  🔗 {gql_url} 시도...")
            try:
                # GraphQL introspection query
                query = {
                    "query": """
                    query IntrospectionQuery {
                        __schema {
                            types {
                                name
                                fields {
                                    name
                                    type {
                                        name
                                    }
                                }
                            }
                        }
                    }
                    """
                }
                
                response = self.session.post(gql_url, json=query, timeout=10)
                if response.status_code == 200:
                    print(f"    ✅ GraphQL 엔드포인트 발견!")
                    try:
                        data = response.json()
                        print(f"    📊 GraphQL 스키마 정보 확인")
                    except:
                        print(f"    📊 GraphQL 응답 확인")
                else:
                    print(f"    ❌ GraphQL 실패! 상태코드: {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ GraphQL 오류: {str(e)[:50]}")
    
    def try_documentation_approach(self):
        """문서화된 API 접근 방법 시도"""
        print("\n🔍 문서화된 API 접근 방법 시도...")
        
        # Pyth Network 공식 문서에서 확인한 엔드포인트들
        doc_endpoints = [
            ("https://hermes.pyth.network", "/v2/price_feeds"),
            ("https://hermes.pyth.network", "/v2/updates/price/latest"),
            ("https://hermes.pyth.network", "/api/latest_vaas"),
            ("https://hermes.pyth.network", "/v2/price_feeds/current"),
            ("https://hermes.pyth.network", "/v2/price_feeds/latest")
        ]
        
        for base_url, endpoint in doc_endpoints:
            try:
                url = f"{base_url}{endpoint}"
                print(f"  🔗 {url} 시도...")
                
                # 다양한 파라미터로 시도
                params_variations = [
                    {},
                    {"verbose": "true"},
                    {"parsed": "true"},
                    {"encoding": "hex"},
                    {"encoding": "base64"},
                    {"include_publishers": "true"},
                    {"include_validators": "true"},
                    {"include_metadata": "true"},
                    {"full": "true"},
                    {"detailed": "true"}
                ]
                
                for params in params_variations:
                    try:
                        response = self.session.get(url, params=params, timeout=10)
                        if response.status_code == 200:
                            print(f"    ✅ 성공! 파라미터: {params}")
                            try:
                                data = response.json()
                                # 퍼블리셔 관련 정보 검색
                                self.search_publisher_info_in_response(data, f"{url}?{params}")
                            except:
                                print(f"    📊 JSON이 아닌 응답")
                        else:
                            print(f"    ❌ 실패! 파라미터: {params}, 상태코드: {response.status_code}")
                    except Exception as e:
                        print(f"    ❌ 오류: 파라미터: {params}, 오류: {str(e)[:30]}")
                    
                    time.sleep(0.2)
                    
            except Exception as e:
                print(f"    ❌ 전체 오류: {str(e)[:50]}")
    
    def search_publisher_info_in_response(self, data, source):
        """응답에서 퍼블리셔 정보 검색"""
        publisher_keywords = [
            'publisher', 'publishers', 'pub', 'authority', 'authorities',
            'validator', 'validators', 'amber', 'alphanonce', 'pyth',
            'signature', 'signatures', 'signer', 'signers'
        ]
        
        found_info = []
        
        def search_recursive(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # 키에서 퍼블리셔 관련 키워드 검색
                    if any(keyword in key.lower() for keyword in publisher_keywords):
                        found_info.append(f"{current_path}: {value}")
                    
                    # 값에서도 검색
                    if isinstance(value, str) and any(keyword in value.lower() for keyword in publisher_keywords):
                        found_info.append(f"{current_path}: {value}")
                    
                    search_recursive(value, current_path)
                    
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]"
                    search_recursive(item, current_path)
        
        search_recursive(data)
        
        if found_info:
            print(f"    🔍 퍼블리셔 정보 발견 ({source}):")
            for info in found_info[:5]:  # 최대 5개만 표시
                print(f"      • {info}")
            if len(found_info) > 5:
                print(f"      • ... 및 {len(found_info) - 5}개 더")
        else:
            print(f"    ❌ 퍼블리셔 정보 없음 ({source})")
    
    def run_comprehensive_analysis(self):
        """종합적인 분석 실행"""
        print("🚀 Pyth Network 퍼블리셔 정보 종합 분석")
        print("=" * 60)
        
        # 1. 기본 엔드포인트 테스트
        working_endpoints = self.test_endpoints()
        
        # 2. 퍼블리셔 특정 엔드포인트 테스트
        self.try_publisher_specific_endpoints()
        
        # 3. WebSocket 접근 방법
        self.try_websocket_approach()
        
        # 4. GraphQL 접근 방법
        self.try_graphql_approach()
        
        # 5. 문서화된 API 접근 방법
        self.try_documentation_approach()
        
        print("\n" + "=" * 60)
        print("📊 종합 분석 완료!")
        print(f"✅ 작동하는 엔드포인트: {len(working_endpoints)}개")
        
        if working_endpoints:
            print("\n🏆 작동하는 엔드포인트 목록:")
            for base_url, endpoint in working_endpoints:
                print(f"  • {base_url}{endpoint}")

if __name__ == "__main__":
    analyzer = PythAlternativeApproach()
    analyzer.run_comprehensive_analysis() 