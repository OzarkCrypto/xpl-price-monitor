#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
import base64
from typing import Dict, List, Any, Optional

class PythOfficialDocsApproach:
    def __init__(self):
        self.base_url = "https://hermes.pyth.network"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def get_all_price_feeds(self):
        """모든 가격 피드 가져오기"""
        print("🔍 모든 가격 피드 가져오기...")
        try:
            response = self.session.get(f"{self.base_url}/v2/price_feeds", timeout=30)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {len(data)}개의 가격 피드를 가져왔습니다.")
                return data
            else:
                print(f"❌ 실패! 상태코드: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ 오류: {str(e)}")
            return []
    
    def try_pyth_sdk_approach(self):
        """Pyth SDK 방식으로 접근"""
        print("\n🔍 Pyth SDK 방식으로 접근...")
        
        # Pyth SDK에서 사용하는 방식들
        sdk_endpoints = [
            "/v2/price_feeds",
            "/v2/updates/price/latest",
            "/api/latest_vaas"
        ]
        
        for endpoint in sdk_endpoints:
            print(f"  🔗 {endpoint} SDK 방식 시도...")
            
            # SDK에서 사용하는 파라미터들
            sdk_params = [
                {},  # 기본
                {"ids[]": ["5169491cd7e2a44c98353b779d5eb612e4ac32e073f5cc534303d86307c2f1bc"]},  # 특정 ID
                {"ids[]": ["5169491cd7e2a44c98353b779d5eb612e4ac32e073f5cc534303d86307c2f1bc", "12d65f1ff0624e4fe2cb450040cc7ba1db91914ad29e4c1a1d339494f078a92b"]}  # 여러 ID
            ]
            
            for params in sdk_params:
                try:
                    url = f"{self.base_url}{endpoint}"
                    response = self.session.get(url, params=params, timeout=15)
                    
                    if response.status_code == 200:
                        print(f"    ✅ 성공! 파라미터: {params}")
                        try:
                            data = response.json()
                            self.analyze_sdk_response(data, endpoint, params)
                        except:
                            print(f"    📊 JSON이 아닌 응답")
                    else:
                        print(f"    ❌ 실패! 파라미터: {params}, 상태코드: {response.status_code}")
                        
                except Exception as e:
                    print(f"    ❌ 오류: 파라미터: {params}, 오류: {str(e)[:30]}")
                
                time.sleep(0.5)
    
    def analyze_sdk_response(self, data, endpoint, params):
        """SDK 응답 분석"""
        print(f"    📊 응답 분석 ({endpoint}):")
        print(f"      타입: {type(data)}")
        
        if isinstance(data, dict):
            print(f"      키들: {list(data.keys())}")
            if 'binary' in data:
                print(f"      Binary 데이터 있음")
            if 'parsed' in data:
                print(f"      Parsed 데이터 있음")
                self.analyze_parsed_data(data['parsed'])
                
        elif isinstance(data, list):
            print(f"      리스트 길이: {len(data)}")
            if len(data) > 0:
                print(f"      첫 번째 항목 키들: {list(data[0].keys()) if isinstance(data[0], dict) else 'dict 아님'}")
    
    def analyze_parsed_data(self, parsed_data):
        """Parsed 데이터 분석"""
        if isinstance(parsed_data, list) and len(parsed_data) > 0:
            first_item = parsed_data[0]
            print(f"      첫 번째 parsed 항목 키들: {list(first_item.keys())}")
            
            # 퍼블리셔 관련 정보 검색
            publisher_info = self.search_publisher_in_parsed(first_item)
            if publisher_info:
                print(f"      🔍 퍼블리셔 정보 발견:")
                for info in publisher_info:
                    print(f"        • {info}")
    
    def search_publisher_in_parsed(self, item):
        """Parsed 항목에서 퍼블리셔 정보 검색"""
        publisher_info = []
        
        def search_recursive(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # 퍼블리셔 관련 키워드 검색
                    if any(keyword in key.lower() for keyword in ['publisher', 'pub', 'authority', 'validator', 'signer']):
                        publisher_info.append(f"{current_path}: {value}")
                    
                    # 값이 문자열이고 퍼블리셔 관련 키워드 포함
                    if isinstance(value, str) and any(keyword in value.lower() for keyword in ['amber', 'alphanonce', 'pyth']):
                        publisher_info.append(f"{current_path}: {value}")
                    
                    search_recursive(value, current_path)
                    
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]"
                    search_recursive(item, current_path)
        
        search_recursive(item)
        return publisher_info
    
    def try_blockchain_approach(self):
        """블록체인 데이터 접근 방법"""
        print("\n🔍 블록체인 데이터 접근 방법...")
        
        # Solana RPC 엔드포인트들
        solana_endpoints = [
            "https://api.mainnet-beta.solana.com",
            "https://solana-api.projectserum.com",
            "https://rpc.ankr.com/solana"
        ]
        
        for rpc_url in solana_endpoints:
            print(f"  🔗 {rpc_url} 시도...")
            try:
                # Pyth 프로그램 ID
                pyth_program_id = "FsJ3A3u2vn5cTVofAjvy6y5kwABJAqYWpe4975bi2epH"
                
                # Pyth 계정 정보 조회
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getAccountInfo",
                    "params": [
                        pyth_program_id,
                        {"encoding": "base64"}
                    ]
                }
                
                response = self.session.post(rpc_url, json=payload, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if 'result' in data and data['result']:
                        print(f"    ✅ Pyth 프로그램 계정 정보 조회 성공!")
                        print(f"    📊 계정 데이터 길이: {len(data['result']['value']['data'][0])}")
                    else:
                        print(f"    ❌ 계정 정보 없음")
                else:
                    print(f"    ❌ 실패! 상태코드: {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ 오류: {str(e)[:50]}")
            
            time.sleep(1)
    
    def try_pyth_governance_approach(self):
        """Pyth 거버넌스 접근 방법"""
        print("\n🔍 Pyth 거버넌스 접근 방법...")
        
        # Pyth 거버넌스 관련 엔드포인트들
        governance_endpoints = [
            "https://hermes.pyth.network/v2/governance",
            "https://hermes.pyth.network/api/governance",
            "https://hermes.pyth.network/v2/authorities",
            "https://hermes.pyth.network/api/authorities"
        ]
        
        for endpoint in governance_endpoints:
            try:
                print(f"  🔗 {endpoint} 시도...")
                response = self.session.get(endpoint, timeout=10)
                
                if response.status_code == 200:
                    print(f"    ✅ 성공!")
                    try:
                        data = response.json()
                        print(f"    📊 응답 타입: {type(data)}")
                        if isinstance(data, dict):
                            print(f"    📋 키들: {list(data.keys())}")
                        elif isinstance(data, list):
                            print(f"    📋 리스트 길이: {len(data)}")
                    except:
                        print(f"    📊 JSON이 아닌 응답")
                else:
                    print(f"    ❌ 실패! 상태코드: {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ 오류: {str(e)[:50]}")
            
            time.sleep(0.5)
    
    def try_pyth_network_website_approach(self):
        """Pyth Network 웹사이트 접근 방법"""
        print("\n🔍 Pyth Network 웹사이트 접근 방법...")
        
        # Pyth Network 웹사이트 API들
        website_endpoints = [
            "https://pyth.network/api/price_feeds",
            "https://pyth.network/api/publishers",
            "https://pyth.network/api/validators",
            "https://pyth.network/api/authorities",
            "https://pyth.network/api/feeds",
            "https://pyth.network/api/v2/price_feeds",
            "https://pyth.network/api/v2/publishers"
        ]
        
        for endpoint in website_endpoints:
            try:
                print(f"  🔗 {endpoint} 시도...")
                response = self.session.get(endpoint, timeout=10)
                
                if response.status_code == 200:
                    print(f"    ✅ 성공!")
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
    
    def try_pyth_documentation_links(self):
        """Pyth 문서 링크들 확인"""
        print("\n🔍 Pyth 문서 링크들 확인...")
        
        # Pyth 관련 문서 및 API 링크들
        doc_links = [
            "https://docs.pyth.network/",
            "https://docs.pyth.network/api",
            "https://docs.pyth.network/api/rest",
            "https://docs.pyth.network/api/websocket",
            "https://docs.pyth.network/pythnet-price-feeds",
            "https://docs.pyth.network/pythnet-price-feeds/api"
        ]
        
        for link in doc_links:
            try:
                print(f"  🔗 {link} 확인...")
                response = self.session.get(link, timeout=10)
                
                if response.status_code == 200:
                    print(f"    ✅ 문서 접근 가능!")
                    # 문서에서 퍼블리셔 관련 내용 검색
                    content = response.text.lower()
                    if 'publisher' in content:
                        print(f"    🔍 퍼블리셔 관련 내용 발견!")
                    if 'authority' in content:
                        print(f"    🔍 Authority 관련 내용 발견!")
                    if 'validator' in content:
                        print(f"    🔍 Validator 관련 내용 발견!")
                else:
                    print(f"    ❌ 접근 불가! 상태코드: {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ 오류: {str(e)[:50]}")
            
            time.sleep(0.5)
    
    def run_comprehensive_analysis(self):
        """종합적인 분석 실행"""
        print("🚀 Pyth Network 공식 문서 기반 퍼블리셔 정보 분석")
        print("=" * 70)
        
        # 1. 기본 가격 피드 가져오기
        price_feeds = self.get_all_price_feeds()
        
        # 2. Pyth SDK 방식 접근
        self.try_pyth_sdk_approach()
        
        # 3. 블록체인 데이터 접근
        self.try_blockchain_approach()
        
        # 4. Pyth 거버넌스 접근
        self.try_pyth_governance_approach()
        
        # 5. Pyth Network 웹사이트 접근
        self.try_pyth_network_website_approach()
        
        # 6. Pyth 문서 링크들 확인
        self.try_pyth_documentation_links()
        
        print("\n" + "=" * 70)
        print("📊 공식 문서 기반 분석 완료!")
        print(f"✅ 분석한 가격 피드 수: {len(price_feeds)}")

if __name__ == "__main__":
    analyzer = PythOfficialDocsApproach()
    analyzer.run_comprehensive_analysis() 