#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
from typing import Dict, List, Any, Optional

class PythDebugStructure:
    def __init__(self):
        self.base_url = "https://hermes.pyth.network"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def debug_api_response_structure(self):
        """API 응답 구조 디버깅"""
        print("🔍 API 응답 구조 디버깅...")
        
        # 샘플 피드 ID들
        sample_feed_ids = [
            "5169491cd7e2a44c98353b779d5eb612e4ac32e073f5cc534303d86307c2f1bc",
            "12d65f1ff0624e4fe2cb450040cc7ba1db91914ad29e4c1a1d339494f078a92b",
            "3622e381dbca2efd1859253763b1adc63f7f9abb8e76da1aa8e638a57ccde93e"
        ]
        
        for i, feed_id in enumerate(sample_feed_ids):
            print(f"\n📊 피드 {i+1} 분석: {feed_id[:20]}...")
            
            try:
                # /v2/updates/price/latest 엔드포인트 호출
                params = {"ids[]": [feed_id]}
                response = self.session.get(f"{self.base_url}/v2/updates/price/latest", params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ API 호출 성공!")
                    print(f"  📊 응답 타입: {type(data)}")
                    
                    if isinstance(data, dict):
                        print(f"  📋 최상위 키들: {list(data.keys())}")
                        
                        # binary 데이터 분석
                        if 'binary' in data:
                            binary_data = data['binary']
                            print(f"  🔍 Binary 데이터:")
                            print(f"    타입: {type(binary_data)}")
                            if isinstance(binary_data, dict):
                                print(f"    키들: {list(binary_data.keys())}")
                                if 'data' in binary_data:
                                    print(f"    데이터 길이: {len(binary_data['data'])}")
                                    print(f"    데이터 샘플: {binary_data['data'][:100]}...")
                        
                        # parsed 데이터 분석
                        if 'parsed' in data:
                            parsed_data = data['parsed']
                            print(f"  🔍 Parsed 데이터:")
                            print(f"    타입: {type(parsed_data)}")
                            
                            if isinstance(parsed_data, list) and len(parsed_data) > 0:
                                first_item = parsed_data[0]
                                print(f"    첫 번째 항목 타입: {type(first_item)}")
                                
                                if isinstance(first_item, dict):
                                    print(f"    첫 번째 항목 키들: {list(first_item.keys())}")
                                    
                                    # 각 키의 값 타입 확인
                                    for key, value in first_item.items():
                                        print(f"      {key}: {type(value)} = {str(value)[:100]}")
                                    
                                    # priceComponents 확인
                                    if 'priceComponents' in first_item:
                                        price_components = first_item['priceComponents']
                                        print(f"    🔍 PriceComponents:")
                                        print(f"      타입: {type(price_components)}")
                                        if isinstance(price_components, list):
                                            print(f"      길이: {len(price_components)}")
                                            for j, component in enumerate(price_components):
                                                print(f"      컴포넌트 {j+1}: {type(component)} = {component}")
                                        else:
                                            print(f"      값: {price_components}")
                                    
                                    # metadata 확인
                                    if 'metadata' in first_item:
                                        metadata = first_item['metadata']
                                        print(f"    🔍 Metadata:")
                                        print(f"      타입: {type(metadata)}")
                                        if isinstance(metadata, dict):
                                            print(f"      키들: {list(metadata.keys())}")
                                            for key, value in metadata.items():
                                                print(f"        {key}: {type(value)} = {value}")
                                        else:
                                            print(f"      값: {metadata}")
                                    
                                    # price 확인
                                    if 'price' in first_item:
                                        price = first_item['price']
                                        print(f"    🔍 Price:")
                                        print(f"      타입: {type(price)}")
                                        if isinstance(price, dict):
                                            print(f"      키들: {list(price.keys())}")
                                            for key, value in price.items():
                                                print(f"        {key}: {type(value)} = {value}")
                                        else:
                                            print(f"      값: {price}")
                                    
                                    # ema_price 확인
                                    if 'ema_price' in first_item:
                                        ema_price = first_item['ema_price']
                                        print(f"    🔍 EMA Price:")
                                        print(f"      타입: {type(ema_price)}")
                                        if isinstance(ema_price, dict):
                                            print(f"      키들: {list(ema_price.keys())}")
                                            for key, value in ema_price.items():
                                                print(f"        {key}: {type(value)} = {value}")
                                        else:
                                            print(f"      값: {ema_price}")
                                    
                                    # 전체 구조를 JSON으로 출력 (일부만)
                                    print(f"    📄 전체 구조 (일부):")
                                    print(json.dumps(first_item, indent=2, default=str)[:1000] + "...")
                                    
                                else:
                                    print(f"    첫 번째 항목: {first_item}")
                            else:
                                print(f"    Parsed 데이터: {parsed_data}")
                    else:
                        print(f"  📊 응답: {data}")
                        
                else:
                    print(f"  ❌ API 호출 실패! 상태코드: {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ 오류: {str(e)}")
            
            time.sleep(1)
    
    def search_for_publisher_keywords(self):
        """퍼블리셔 관련 키워드 검색"""
        print("\n🔍 퍼블리셔 관련 키워드 검색...")
        
        # 샘플 피드 ID
        feed_id = "5169491cd7e2a44c98353b779d5eb612e4ac32e073f5cc534303d86307c2f1bc"
        
        try:
            params = {"ids[]": [feed_id]}
            response = self.session.get(f"{self.base_url}/v2/updates/price/latest", params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # 재귀적으로 모든 키워드 검색
                def search_recursive(obj, path=""):
                    found_items = []
                    
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            current_path = f"{path}.{key}" if path else key
                            
                            # 키에서 검색
                            if any(keyword in key.lower() for keyword in ['publisher', 'pub', 'authority', 'validator', 'signer', 'amber', 'alphanonce']):
                                found_items.append(f"{current_path}: {value}")
                            
                            # 값에서 검색
                            if isinstance(value, str) and any(keyword in value.lower() for keyword in ['publisher', 'pub', 'authority', 'validator', 'signer', 'amber', 'alphanonce']):
                                found_items.append(f"{current_path}: {value}")
                            
                            # 재귀 검색
                            found_items.extend(search_recursive(value, current_path))
                            
                    elif isinstance(obj, list):
                        for i, item in enumerate(obj):
                            current_path = f"{path}[{i}]"
                            found_items.extend(search_recursive(item, current_path))
                    
                    return found_items
                
                found_items = search_recursive(data)
                
                if found_items:
                    print(f"  ✅ 퍼블리셔 관련 키워드 발견!")
                    for item in found_items:
                        print(f"    • {item}")
                else:
                    print(f"  ❌ 퍼블리셔 관련 키워드 없음")
                    
        except Exception as e:
            print(f"  ❌ 오류: {str(e)}")
    
    def run_debug_analysis(self):
        """디버그 분석 실행"""
        print("🚀 Pyth Network API 응답 구조 디버깅")
        print("=" * 60)
        
        # 1. API 응답 구조 디버깅
        self.debug_api_response_structure()
        
        # 2. 퍼블리셔 관련 키워드 검색
        self.search_for_publisher_keywords()
        
        print("\n" + "=" * 60)
        print("📊 디버그 분석 완료!")

if __name__ == "__main__":
    debugger = PythDebugStructure()
    debugger.run_debug_analysis() 