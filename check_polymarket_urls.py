#!/usr/bin/env python3
"""
폴리마켓 URL 구조 확인
"""

import requests
import json

def check_polymarket_urls():
    """폴리마켓의 실제 URL 구조를 확인합니다."""
    
    print("🔍 폴리마켓 URL 구조 확인 중...")
    
    # 방법 1: 실제 폴리마켓 웹사이트 접근
    print("\n1️⃣ 폴리마켓 웹사이트 URL 구조 확인")
    
    test_urls = [
        "https://polymarket.com",
        "https://polymarket.com/event",
        "https://polymarket.com/markets",
        "https://polymarket.com/event/test",
        "https://polymarket.com/markets/test"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"   {url}: {response.status_code}")
        except Exception as e:
            print(f"   {url}: 오류 - {e}")
    
    # 방법 2: API에서 받은 마켓 데이터로 실제 URL 확인
    print("\n2️⃣ API 데이터로 실제 URL 구조 확인")
    
    url = "https://clob.polymarket.com/markets"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    params = {'limit': 10}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get('data', [])
            
            print(f"   ✅ {len(markets)}개 마켓 데이터 수신")
            
            for i, market in enumerate(markets[:5], 1):
                question = market.get('question', 'Unknown')
                market_slug = market.get('market_slug', '')
                condition_id = market.get('condition_id', '')
                question_id = market.get('question_id', '')
                
                print(f"\n   마켓 {i}: {question[:50]}...")
                print(f"     market_slug: {market_slug}")
                print(f"     condition_id: {condition_id}")
                print(f"     question_id: {question_id}")
                
                # 다양한 URL 형식 시도
                url_formats = [
                    f"https://polymarket.com/event/{market_slug}" if market_slug else None,
                    f"https://polymarket.com/markets/{market_slug}" if market_slug else None,
                    f"https://polymarket.com/event/{condition_id}" if condition_id else None,
                    f"https://polymarket.com/markets/{condition_id}" if condition_id else None,
                    f"https://polymarket.com/event/{question_id}" if question_id else None,
                    f"https://polymarket.com/markets/{question_id}" if question_id else None
                ]
                
                print("     URL 테스트:")
                for url_format in url_formats:
                    if url_format:
                        try:
                            test_response = requests.get(url_format, timeout=10)
                            status = "✅" if test_response.status_code == 200 else f"❌ {test_response.status_code}"
                            print(f"       {url_format}: {status}")
                        except Exception as e:
                            print(f"       {url_format}: ❌ 오류")
                
        else:
            print(f"   ❌ API 오류: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 오류: {e}")
    
    # 방법 3: 폴리마켓 공식 문서나 예시 확인
    print("\n3️⃣ 폴리마켓 공식 예시 확인")
    
    # 실제 폴리마켓에서 알려진 마켓 URL들
    known_markets = [
        "https://polymarket.com/event/will-donald-trump-win-the-2024-presidential-election",
        "https://polymarket.com/event/will-bitcoin-reach-100k-in-2024",
        "https://polymarket.com/event/2024-us-presidential-election-winner"
    ]
    
    for url in known_markets:
        try:
            response = requests.get(url, timeout=10)
            print(f"   {url}: {response.status_code}")
        except Exception as e:
            print(f"   {url}: 오류 - {e}")

def test_url_generation():
    """URL 생성 로직 테스트"""
    print("\n4️⃣ URL 생성 로직 테스트")
    
    # 테스트 데이터
    test_markets = [
        {
            'question': 'Will Bitcoin reach $100k in 2024?',
            'market_slug': 'will-bitcoin-reach-100k-in-2024',
            'condition_id': '0x1234567890abcdef',
            'question_id': '0xfedcba0987654321'
        },
        {
            'question': '2024 US Presidential Election Winner',
            'market_slug': '2024-us-presidential-election-winner',
            'condition_id': '0xabcdef1234567890',
            'question_id': '0x0987654321fedcba'
        }
    ]
    
    for i, market in enumerate(test_markets, 1):
        print(f"\n   테스트 마켓 {i}: {market['question']}")
        
        # 다양한 URL 생성 방법
        url_methods = [
            f"https://polymarket.com/event/{market['market_slug']}",
            f"https://polymarket.com/markets/{market['market_slug']}",
            f"https://polymarket.com/event/{market['condition_id']}",
            f"https://polymarket.com/markets/{market['condition_id']}",
            f"https://polymarket.com/event/{market['question_id']}",
            f"https://polymarket.com/markets/{market['question_id']}"
        ]
        
        print("     생성된 URL들:")
        for url in url_methods:
            print(f"       {url}")
        
        # 실제 접근 테스트
        print("     실제 접근 테스트:")
        for url in url_methods:
            try:
                response = requests.get(url, timeout=10)
                status = "✅" if response.status_code == 200 else f"❌ {response.status_code}"
                print(f"       {url}: {status}")
            except Exception as e:
                print(f"       {url}: ❌ 오류")

if __name__ == "__main__":
    check_polymarket_urls()
    test_url_generation()
    
    print("\n" + "=" * 60)
    print("🎯 URL 구조 분석 완료!")
    print("위 결과를 바탕으로 올바른 URL 생성 로직을 수정하세요.") 