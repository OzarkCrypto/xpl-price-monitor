#!/usr/bin/env python3
"""
Rootdata 웹사이트 구조 분석기
실제 hot index 데이터가 어디에 있는지 파악하고 파싱 로직을 개발
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

class RootdataAnalyzer:
    def __init__(self):
        """Rootdata 분석기 초기화"""
        self.url = "https://www.rootdata.com/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def analyze_page_structure(self):
        """페이지 구조를 분석합니다."""
        try:
            print("🔍 Rootdata 웹사이트 구조 분석 중...")
            
            response = self.session.get(self.url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            print(f"📄 페이지 제목: {soup.title.string if soup.title else 'N/A'}")
            print(f"📊 페이지 크기: {len(response.content):,} bytes")
            
            # 1. 모든 테이블 분석
            self.analyze_tables(soup)
            
            # 2. 모든 div와 클래스 분석
            self.analyze_divs_and_classes(soup)
            
            # 3. JavaScript 데이터 분석
            self.analyze_javascript_data(soup)
            
            # 4. 특정 키워드 검색
            self.search_for_keywords(soup)
            
            # 5. 페이지 소스 저장
            self.save_page_source(response.text)
            
        except Exception as e:
            print(f"❌ 분석 중 오류: {e}")
    
    def analyze_tables(self, soup):
        """테이블 구조를 분석합니다."""
        print("\n📋 테이블 분석:")
        tables = soup.find_all('table')
        print(f"총 {len(tables)}개의 테이블 발견")
        
        for i, table in enumerate(tables):
            print(f"\n테이블 {i+1}:")
            rows = table.find_all('tr')
            print(f"  행 수: {len(rows)}")
            
            if rows:
                # 첫 번째 행의 헤더 분석
                headers = rows[0].find_all(['th', 'td'])
                header_texts = [h.get_text(strip=True) for h in headers]
                print(f"  헤더: {header_texts}")
                
                # 데이터 행 샘플
                if len(rows) > 1:
                    data_row = rows[1].find_all('td')
                    data_texts = [d.get_text(strip=True) for d in data_row]
                    print(f"  데이터 샘플: {data_texts}")
    
    def analyze_divs_and_classes(self, soup):
        """div와 클래스 구조를 분석합니다."""
        print("\n🏗️ div 및 클래스 분석:")
        
        # hot 관련 클래스 찾기
        hot_elements = soup.find_all(class_=lambda x: x and 'hot' in x.lower())
        print(f"hot 관련 클래스: {len(hot_elements)}개")
        
        for i, element in enumerate(hot_elements[:5]):  # 처음 5개만
            print(f"  {i+1}. 클래스: {element.get('class')}")
            print(f"     텍스트: {element.get_text(strip=True)[:100]}...")
        
        # index 관련 클래스 찾기
        index_elements = soup.find_all(class_=lambda x: x and 'index' in x.lower())
        print(f"index 관련 클래스: {len(index_elements)}개")
        
        # ranking 관련 클래스 찾기
        ranking_elements = soup.find_all(class_=lambda x: x and 'rank' in x.lower())
        print(f"ranking 관련 클래스: {len(ranking_elements)}개")
    
    def analyze_javascript_data(self, soup):
        """JavaScript 데이터를 분석합니다."""
        print("\n💻 JavaScript 데이터 분석:")
        
        scripts = soup.find_all('script')
        print(f"총 {len(scripts)}개의 script 태그 발견")
        
        for i, script in enumerate(scripts):
            if script.string:
                script_content = script.string
                
                # hot index 관련 데이터 찾기
                if 'hot' in script_content.lower() and 'index' in script_content.lower():
                    print(f"\n  Script {i+1}에서 hot index 관련 데이터 발견:")
                    print(f"    내용: {script_content[:200]}...")
                
                # JSON 데이터 찾기
                json_matches = re.findall(r'\{[^{}]*"hot"[^{}]*\}', script_content)
                if json_matches:
                    print(f"\n  Script {i+1}에서 JSON 데이터 발견:")
                    for match in json_matches[:3]:
                        print(f"    {match}")
                
                # 배열 데이터 찾기
                array_matches = re.findall(r'\[[^\[\]]*"hot"[^\[\]]*\]', script_content)
                if array_matches:
                    print(f"\n  Script {i+1}에서 배열 데이터 발견:")
                    for match in array_matches[:3]:
                        print(f"    {match}")
    
    def search_for_keywords(self, soup):
        """특정 키워드를 검색합니다."""
        print("\n🔍 키워드 검색:")
        
        keywords = ['hot', 'index', 'ranking', 'trend', 'popular', 'score']
        
        for keyword in keywords:
            elements = soup.find_all(string=re.compile(keyword, re.IGNORECASE))
            if elements:
                print(f"  '{keyword}' 키워드: {len(elements)}개 발견")
                for element in elements[:3]:
                    parent = element.parent
                    if parent:
                        print(f"    {parent.get_text(strip=True)[:100]}...")
    
    def save_page_source(self, html_content):
        """페이지 소스를 파일로 저장합니다."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"rootdata_source_{timestamp}.html"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"\n💾 페이지 소스가 {filename}에 저장되었습니다.")
        except Exception as e:
            print(f"❌ 파일 저장 실패: {e}")
    
    def test_parsing_methods(self):
        """다양한 파싱 방법을 테스트합니다."""
        print("\n🧪 파싱 방법 테스트:")
        
        try:
            response = self.session.get(self.url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 방법 1: 모든 텍스트에서 hot index 패턴 찾기
            print("\n1. 텍스트 패턴 검색:")
            all_text = soup.get_text()
            hot_patterns = re.findall(r'hot\s*index[:\s]*([\d,]+)', all_text, re.IGNORECASE)
            if hot_patterns:
                print(f"   발견된 hot index 값들: {hot_patterns[:10]}")
            
            # 방법 2: 특정 구조에서 데이터 찾기
            print("\n2. 구조적 데이터 검색:")
            data_elements = soup.find_all(['div', 'span', 'td'], class_=re.compile(r'data|value|score'))
            print(f"   데이터 관련 요소: {len(data_elements)}개")
            
            # 방법 3: API 엔드포인트 찾기
            print("\n3. API 엔드포인트 검색:")
            api_patterns = re.findall(r'https?://[^\s"\'<>]+api[^\s"\'<>]*', all_text)
            if api_patterns:
                print(f"   발견된 API URL들: {api_patterns[:5]}")
            
        except Exception as e:
            print(f"❌ 테스트 중 오류: {e}")

def main():
    """메인 함수"""
    print("🔍 Rootdata 웹사이트 구조 분석기")
    print("=" * 50)
    
    analyzer = RootdataAnalyzer()
    
    try:
        # 기본 구조 분석
        analyzer.analyze_page_structure()
        
        # 파싱 방법 테스트
        analyzer.test_parsing_methods()
        
        print("\n✅ 분석 완료!")
        print("\n💡 다음 단계:")
        print("1. 저장된 HTML 파일을 확인하여 실제 데이터 구조 파악")
        print("2. 발견된 패턴을 바탕으로 파싱 로직 개발")
        print("3. rootdata_hot_index_monitor.py의 parse_hot_index 메서드 업데이트")
        
    except Exception as e:
        print(f"❌ 분석 실패: {e}")

if __name__ == "__main__":
    main() 