#!/usr/bin/env python3
"""
폴리마켓 마켓 데이터 구조 확인
"""

import requests
import json

def check_market_structure():
    """마켓 데이터 구조 확인"""
    
    url = "https://clob.polymarket.com/markets"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    params = {'limit': 5}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get('data', [])
            
            print(f"총 {len(markets)}개 마켓 확인")
            
            if markets:
                print("\n첫 번째 마켓 데이터 구조:")
                print("=" * 60)
                first_market = markets[0]
                
                # 모든 키 출력
                for key, value in first_market.items():
                    print(f"{key}: {type(value)} - {str(value)[:100]}")
                
                print("\n" + "=" * 60)
                print("첫 번째 마켓 전체 JSON:")
                print(json.dumps(first_market, indent=2, ensure_ascii=False))
                
                # 두 번째 마켓도 확인
                if len(markets) > 1:
                    print("\n" + "=" * 60)
                    print("두 번째 마켓 주요 정보:")
                    second_market = markets[1]
                    for key in ['question', 'title', 'description', 'slug', 'end_date_iso', 'closed']:
                        if key in second_market:
                            print(f"{key}: {second_market[key]}")
            
        else:
            print(f"API 오류: {response.status_code}")
            
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    check_market_structure()