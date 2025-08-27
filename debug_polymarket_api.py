#!/usr/bin/env python3
"""
폴리마켓 API 디버깅 스크립트
"""

import requests
import json
from datetime import datetime

def debug_polymarket_api():
    """폴리마켓 API 구조 확인"""
    
    # 다양한 엔드포인트 테스트
    endpoints = [
        "https://clob.polymarket.com/markets",
        "https://gamma-api.polymarket.com/markets",
        "https://strapi-matic.poly.market/markets",
        "https://clob.polymarket.com/book"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    for url in endpoints:
        print(f"\n{'='*60}")
        print(f"테스트 URL: {url}")
        print(f"{'='*60}")
        
        try:
            # 기본 요청
            response = requests.get(url, headers=headers, timeout=30)
            print(f"상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"응답 데이터 타입: {type(data)}")
                    
                    if isinstance(data, dict):
                        print(f"응답 키들: {list(data.keys())}")
                        
                        # markets 키가 있는지 확인
                        if 'markets' in data:
                            markets = data['markets']
                            print(f"마켓 수: {len(markets) if isinstance(markets, list) else 'N/A'}")
                            
                            if isinstance(markets, list) and len(markets) > 0:
                                print("첫 번째 마켓 샘플:")
                                print(json.dumps(markets[0], indent=2, ensure_ascii=False)[:500] + "...")
                        
                        # 기타 키들 확인
                        for key, value in data.items():
                            if key != 'markets':
                                if isinstance(value, list):
                                    print(f"{key}: 리스트 (길이: {len(value)})")
                                elif isinstance(value, dict):
                                    print(f"{key}: 딕셔너리 (키: {list(value.keys())[:5]})")
                                else:
                                    print(f"{key}: {type(value)} - {str(value)[:100]}")
                    
                    elif isinstance(data, list):
                        print(f"리스트 길이: {len(data)}")
                        if len(data) > 0:
                            print("첫 번째 항목:")
                            print(json.dumps(data[0], indent=2, ensure_ascii=False)[:500] + "...")
                    
                except json.JSONDecodeError:
                    print("JSON 파싱 실패")
                    print(f"응답 텍스트 (처음 200자): {response.text[:200]}")
            else:
                print(f"오류 응답: {response.text[:200]}")
                
        except Exception as e:
            print(f"요청 실패: {e}")
    
    # 파라미터를 포함한 요청 테스트
    print(f"\n{'='*60}")
    print("파라미터 포함 요청 테스트")
    print(f"{'='*60}")
    
    test_params = [
        {"limit": 10},
        {"limit": 50, "offset": 0},
        {"active": True},
        {"status": "active"},
        {"fpmm": True}
    ]
    
    base_url = "https://clob.polymarket.com/markets"
    
    for params in test_params:
        try:
            print(f"\n파라미터: {params}")
            response = requests.get(base_url, headers=headers, params=params, timeout=30)
            print(f"상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'markets' in data:
                    markets = data['markets']
                    print(f"마켓 수: {len(markets) if isinstance(markets, list) else 'N/A'}")
                    if isinstance(markets, list) and len(markets) > 0:
                        print(f"첫 번째 마켓 제목: {markets[0].get('title', 'N/A')}")
            
        except Exception as e:
            print(f"요청 실패: {e}")

if __name__ == "__main__":
    debug_polymarket_api()