#!/usr/bin/env python3
"""
ALKIMI 가격 디버깅 스크립트
CoinMarketCap 웹사이트의 HTML 구조를 분석합니다.
"""

import requests
import re
from bs4 import BeautifulSoup

def debug_coinmarketcap():
    """CoinMarketCap 웹사이트의 HTML 구조를 분석합니다."""
    url = "https://coinmarketcap.com/currencies/alkimiexchange/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"🔍 {url}에서 데이터를 가져오는 중...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("=" * 80)
        print("📊 HTML 구조 분석 결과")
        print("=" * 80)
        
        # 1. 가격 관련 요소들 찾기
        print("\n1️⃣ 가격 관련 요소들:")
        price_elements = soup.find_all(string=re.compile(r'\$[\d,]+\.?\d*'))
        for i, element in enumerate(price_elements[:10]):
            parent = element.parent
            print(f"  {i+1}. 가격: {element.strip()}")
            print(f"     부모 태그: {parent.name}")
            print(f"     부모 클래스: {parent.get('class', 'N/A')}")
            print(f"     부모 내용: {str(parent)[:200]}...")
            print()
        
        # 2. 24시간 변화율 찾기
        print("\n2️⃣ 24시간 변화율:")
        change_elements = soup.find_all(string=re.compile(r'[\+\-]?\d+\.?\d*%'))
        for i, element in enumerate(change_elements[:10]):
            parent = element.parent
            print(f"  {i+1}. 변화율: {element.strip()}")
            print(f"     부모 태그: {parent.name}")
            print(f"     부모 클래스: {parent.get('class', 'N/A')}")
            print(f"     부모 내용: {str(parent)[:200]}...")
            print()
        
        # 3. 시가총액 찾기
        print("\n3️⃣ 시가총액:")
        market_cap_elements = soup.find_all(string=re.compile(r'\$[\d,]+\.?\d*[MBK]'))
        for i, element in enumerate(market_cap_elements[:10]):
            parent = element.parent
            print(f"  {i+1}. 시가총액: {element.strip()}")
            print(f"     부모 태그: {parent.name}")
            print(f"     부모 클래스: {parent.get('class', 'N/A')}")
            print(f"     부모 내용: {str(parent)[:200]}...")
            print()
        
        # 4. 순위 찾기
        print("\n4️⃣ 순위:")
        rank_elements = soup.find_all(string=re.compile(r'#\d+'))
        for i, element in enumerate(rank_elements[:10]):
            parent = element.parent
            print(f"  {i+1}. 순위: {element.strip()}")
            print(f"     부모 태그: {parent.name}")
            print(f"     부모 클래스: {parent.get('class', 'N/A')}")
            print(f"     부모 내용: {str(parent)[:200]}...")
            print()
        
        # 5. JavaScript 데이터 찾기
        print("\n5️⃣ JavaScript 데이터:")
        script_tags = soup.find_all('script')
        for i, script in enumerate(script_tags):
            if script.string and ('price' in script.string.lower() or 'alkimi' in script.string.lower()):
                print(f"  {i+1}. 스크립트 내용 (일부):")
                script_content = script.string[:500]
                print(f"     {script_content}...")
                print()
        
        # 6. 특정 클래스나 ID를 가진 요소들 찾기
        print("\n6️⃣ 특정 클래스/ID를 가진 요소들:")
        important_classes = ['price', 'priceValue', 'sc-', 'cmc-', 'coin-price']
        for class_name in important_classes:
            elements = soup.find_all(class_=re.compile(class_name, re.IGNORECASE))
            if elements:
                print(f"  클래스 '{class_name}'을 가진 요소들:")
                for j, elem in enumerate(elements[:3]):
                    print(f"    {j+1}. {elem.name}: {elem.get('class', 'N/A')}")
                    print(f"       내용: {elem.get_text()[:100]}...")
                print()
        
        # 7. 전체 HTML에서 ALKIMI 관련 텍스트 찾기
        print("\n7️⃣ ALKIMI 관련 텍스트:")
        alkimi_elements = soup.find_all(string=re.compile(r'alkimi', re.IGNORECASE))
        for i, element in enumerate(alkimi_elements[:10]):
            parent = element.parent
            print(f"  {i+1}. ALKIMI 텍스트: {element.strip()}")
            print(f"     부모 태그: {parent.name}")
            print(f"     부모 클래스: {parent.get('class', 'N/A')}")
            print()
        
        print("=" * 80)
        print("✅ 분석 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    debug_coinmarketcap() 