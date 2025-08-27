#!/usr/bin/env python3
"""
PYTH Insights 디버그 - 실제 HTML 구조 분석
"""

import requests
import json
import re

def debug_insights_page():
    """PYTH Insights 페이지의 실제 구조를 분석합니다."""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    url = "https://insights.pyth.network/publishers?page=1"
    
    try:
        print("🔍 PYTH Insights 페이지 분석 중...")
        response = session.get(url, timeout=15)
        
        if response.status_code == 200:
            html_content = response.text
            
            print(f"✅ 페이지 로드 성공 (크기: {len(html_content)} bytes)")
            
            # 1. 페이지 제목 확인
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE)
            if title_match:
                print(f"📄 페이지 제목: {title_match.group(1)}")
            
            # 2. 스크립트 태그 분석
            script_tags = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL | re.IGNORECASE)
            print(f"📜 스크립트 태그 수: {len(script_tags)}")
            
            # 3. JSON 데이터가 포함된 스크립트 찾기
            json_scripts = []
            for i, script in enumerate(script_tags):
                if any(keyword in script.lower() for keyword in ['publisher', 'ranking', 'active', 'permissioned', 'score']):
                    json_scripts.append((i, script))
            
            print(f"🔍 퍼블리셔 관련 스크립트: {len(json_scripts)}개")
            
            # 4. 테이블 구조 분석
            table_pattern = r'<table[^>]*>(.*?)</table>'
            tables = re.findall(table_pattern, html_content, re.DOTALL | re.IGNORECASE)
            print(f"📊 테이블 수: {len(tables)}")
            
            # 5. Loading 텍스트 확인
            loading_count = html_content.lower().count('loading')
            print(f"⏳ 'Loading' 텍스트 수: {loading_count}")
            
            # 6. React 관련 정보 확인
            react_keywords = ['react', 'next', 'vue', 'angular', 'spa']
            for keyword in react_keywords:
                count = html_content.lower().count(keyword)
                if count > 0:
                    print(f"⚛️  '{keyword}' 키워드: {count}개")
            
            # 7. API 호출 패턴 찾기
            api_patterns = [
                r'fetch\(["\']([^"\']*publisher[^"\']*)["\']',
                r'axios\.get\(["\']([^"\']*publisher[^"\']*)["\']',
                r'api/publishers',
                r'/api/',
                r'graphql'
            ]
            
            for pattern in api_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    print(f"🔗 API 패턴 '{pattern}' 발견: {matches[:3]}")  # 처음 3개만 출력
            
            # 8. 실제 데이터가 있는지 확인
            data_keywords = ['72', 'publishers', 'ranking', 'active', 'permissioned']
            for keyword in data_keywords:
                count = html_content.count(keyword)
                if count > 0:
                    print(f"📊 '{keyword}' 키워드: {count}개")
            
            # 9. HTML 구조 저장
            with open('pyth_insights_debug.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("📄 HTML 구조가 'pyth_insights_debug.html'에 저장되었습니다.")
            
            # 10. 간단한 텍스트 추출
            print("\n=== 페이지에서 발견된 주요 텍스트 ===")
            lines = html_content.split('\n')
            for line in lines:
                line = line.strip()
                if any(keyword in line.lower() for keyword in ['publisher', '72', 'active', 'ranking', 'permissioned']):
                    if len(line) < 200:  # 너무 긴 라인은 제외
                        print(f"  {line}")
            
            return html_content
        else:
            print(f"❌ 페이지 로드 실패: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"💥 오류 발생: {e}")
        return None

def analyze_network_requests():
    """네트워크 요청 패턴을 분석합니다."""
    print("\n🔍 네트워크 요청 패턴 분석...")
    
    # 일반적인 API 엔드포인트들 시도
    base_url = "https://insights.pyth.network"
    endpoints = [
        "/api/publishers",
        "/api/v1/publishers", 
        "/api/v2/publishers",
        "/api/data/publishers",
        "/api/insights/publishers",
        "/api/stats/publishers",
        "/graphql",
        "/api/graphql",
        "/_next/data/publishers",
        "/_next/static/chunks/publishers"
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://insights.pyth.network/publishers'
    })
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = session.get(url, timeout=10)
            print(f"  {endpoint}: {response.status_code} ({len(response.text)} bytes)")
            
            if response.status_code == 200 and len(response.text) > 100:
                # JSON 응답인지 확인
                try:
                    data = response.json()
                    if isinstance(data, dict) or isinstance(data, list):
                        print(f"    ✅ JSON 응답 발견!")
                        # 데이터 구조 확인
                        if isinstance(data, dict):
                            print(f"    📊 키: {list(data.keys())[:5]}")
                        elif isinstance(data, list) and data:
                            print(f"    📊 첫 번째 항목: {list(data[0].keys())[:5] if isinstance(data[0], dict) else 'not dict'}")
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            print(f"  {endpoint}: 연결 실패 - {e}")

def main():
    print("🚀 PYTH Insights 디버그 시작...\n")
    
    # 1. 페이지 구조 분석
    html_content = debug_insights_page()
    
    # 2. 네트워크 요청 분석
    analyze_network_requests()
    
    print("\n✅ 디버그 완료!")

if __name__ == "__main__":
    main() 