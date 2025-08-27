#!/usr/bin/env python3
"""
ALKIMI DexScreener 디버깅 스크립트
DexScreener 웹사이트의 HTML 구조를 분석합니다.
"""

import requests
import re
from bs4 import BeautifulSoup

def debug_dexscreener():
    """DexScreener 웹사이트의 HTML 구조를 분석합니다."""
    url = "https://dexscreener.com/sui/0x2ae42f340d32653cd079f3e80e2e6c2f9485cd8a91491bac0b47e93708c8f049"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"🔍 {url}에서 데이터를 가져오는 중...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("=" * 80)
        print("📊 DexScreener HTML 구조 분석 결과")
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
        
        # 2. 퍼센트 변화율 찾기
        print("\n2️⃣ 퍼센트 변화율:")
        change_elements = soup.find_all(string=re.compile(r'[\+\-]?\d+\.?\d*%'))
        for i, element in enumerate(change_elements[:10]):
            parent = element.parent
            print(f"  {i+1}. 변화율: {element.strip()}")
            print(f"     부모 태그: {parent.name}")
            print(f"     부모 클래스: {parent.get('class', 'N/A')}")
            print(f"     부모 내용: {str(parent)[:200]}...")
            print()
        
        # 3. 유동성 정보 찾기
        print("\n3️⃣ 유동성 정보:")
        liquidity_elements = soup.find_all(string=re.compile(r'[\d,]+\.?\d*[MBK]'))
        for i, element in enumerate(liquidity_elements[:10]):
            parent = element.parent
            print(f"  {i+1}. 유동성: {element.strip()}")
            print(f"     부모 태그: {parent.name}")
            print(f"     부모 클래스: {parent.get('class', 'N/A')}")
            print(f"     부모 내용: {str(parent)[:200]}...")
            print()
        
        # 4. 거래량 정보 찾기
        print("\n4️⃣ 거래량 정보:")
        volume_elements = soup.find_all(string=re.compile(r'[\d,]+\.?\d*[MBK]'))
        for i, element in enumerate(volume_elements[:10]):
            parent = element.parent
            vol_text = element.strip()
            if 'volume' in str(parent).lower() or '거래량' in str(parent):
                print(f"  {i+1}. 거래량: {vol_text}")
                print(f"     부모 태그: {parent.name}")
                print(f"     부모 클래스: {parent.get('class', 'N/A')}")
                print(f"     부모 내용: {str(parent)[:200]}...")
                print()
        
        # 5. JavaScript 데이터 찾기
        print("\n5️⃣ JavaScript 데이터:")
        script_tags = soup.find_all('script')
        for i, script in enumerate(script_tags):
            if script.string and ('price' in script.string.lower() or 'alkimi' in script.string.lower() or 'dex' in script.string.lower()):
                print(f"  {i+1}. 스크립트 내용 (일부):")
                script_content = script.string[:500]
                print(f"     {script_content}...")
                print()
        
        # 6. 특정 클래스나 ID를 가진 요소들 찾기
        print("\n6️⃣ 특정 클래스/ID를 가진 요소들:")
        important_classes = ['price', 'priceValue', 'dex', 'token', 'pair']
        for class_name in important_classes:
            elements = soup.find_all(class_=re.compile(class_name, re.IGNORECASE))
            if elements:
                print(f"  클래스 '{class_name}'을 가진 요소들:")
                for j, elem in enumerate(elements[:3]):
                    print(f"    {j+1}. {elem.name}: {elem.get('class', 'N/A')}")
                    print(f"       내용: {elem.get_text()[:100]}...")
                print()
        
        # 7. ALKIMI 관련 텍스트 찾기
        print("\n7️⃣ ALKIMI 관련 텍스트:")
        alkimi_elements = soup.find_all(string=re.compile(r'alkimi', re.IGNORECASE))
        for i, element in enumerate(alkimi_elements[:10]):
            parent = element.parent
            print(f"  {i+1}. ALKIMI 텍스트: {element.strip()}")
            print(f"     부모 태그: {parent.name}")
            print(f"     부모 클래스: {parent.get('class', 'N/A')}")
            print()
        
        # 8. 전체 HTML에서 주요 정보 찾기
        print("\n8️⃣ 주요 정보 요약:")
        main_content = soup.get_text()
        
        # 가격 패턴 찾기
        price_pattern = re.findall(r'\$([\d,]+\.?\d*)', main_content)
        if price_pattern:
            print(f"  발견된 가격들: {price_pattern[:5]}")
        
        # 퍼센트 패턴 찾기
        percent_pattern = re.findall(r'([\+\-]?\d+\.?\d*)%', main_content)
        if percent_pattern:
            print(f"  발견된 퍼센트들: {percent_pattern[:5]}")
        
        # 숫자 + 단위 패턴 찾기
        unit_pattern = re.findall(r'([\d,]+\.?\d*[MBK])', main_content)
        if unit_pattern:
            print(f"  발견된 단위 숫자들: {unit_pattern[:5]}")
        
        print("=" * 80)
        print("✅ DexScreener 분석 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    debug_dexscreener() 