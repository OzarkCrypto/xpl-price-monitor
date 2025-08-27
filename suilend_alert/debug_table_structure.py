#!/usr/bin/env python3
"""
Rootdata 테이블 구조 디버그 스크립트
테이블의 실제 내용을 자세히 분석합니다.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def debug_table_structure():
    """테이블 구조를 자세히 분석합니다."""
    
    # Chrome 드라이버 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("🔍 Rootdata 테이블 구조 분석 시작...")
        
        # 페이지 접속
        driver.get("https://www.rootdata.com/")
        time.sleep(5)  # 페이지 로딩 대기
        
        print(f"📄 페이지 제목: {driver.title}")
        
        # 테이블 찾기
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"📊 테이블 {len(tables)}개 발견")
        
        for table_idx, table in enumerate(tables):
            print(f"\n📋 테이블 {table_idx + 1} 상세 분석:")
            
            # 테이블 헤더
            headers = table.find_elements(By.TAG_NAME, "th")
            if headers:
                print("  📌 헤더:")
                for i, header in enumerate(headers):
                    print(f"    {i+1:2d}. '{header.text.strip()}'")
            
            # 테이블 행 분석
            rows = table.find_elements(By.TAG_NAME, "tr")
            print(f"  📝 총 {len(rows)}개 행")
            
            # 처음 5개 행만 상세 분석
            for row_idx, row in enumerate(rows[:5]):
                print(f"\n    🚀 행 {row_idx + 1}:")
                
                cells = row.find_elements(By.TAG_NAME, "td")
                print(f"      셀 {len(cells)}개:")
                
                for cell_idx, cell in enumerate(cells):
                    cell_text = cell.text.strip()
                    
                    print(f"        {cell_idx+1:2d}. 텍스트: '{cell_text}'")
                    
                    # 링크가 있는지 확인
                    links = cell.find_elements(By.TAG_NAME, "a")
                    if links:
                        for link_idx, link in enumerate(links):
                            href = link.get_attribute("href")
                            link_text = link.text.strip()
                            print(f"          링크 {link_idx+1}: '{link_text}' -> {href}")
                    
                    # 이미지가 있는지 확인
                    images = cell.find_elements(By.TAG_NAME, "img")
                    if images:
                        for img_idx, img in enumerate(images):
                            src = img.get_attribute("src")
                            alt = img.get_attribute("alt")
                            print(f"          이미지 {img_idx+1}: {alt} -> {src}")
                    
                    # 클래스명 확인
                    class_name = cell.get_attribute("class")
                    if class_name:
                        print(f"          클래스: {class_name}")
            
            # 전체 테이블의 텍스트 내용 확인
            print(f"\n  📄 전체 테이블 텍스트 (처음 1000자):")
            table_text = table.text
            print(f"    {table_text[:1000]}...")
            
            # Hot Index 관련 텍스트 검색
            print(f"\n  🔥 Hot Index 관련 텍스트 검색:")
            hot_keywords = ['hot', 'index', 'score', 'rank', '75', '1', '17', '2', '8', '5']
            found_keywords = []
            
            for keyword in hot_keywords:
                if keyword in table_text.lower():
                    count = table_text.lower().count(keyword)
                    found_keywords.append((keyword, count))
            
            # 빈도순으로 정렬
            found_keywords.sort(key=lambda x: x[1], reverse=True)
            for keyword, count in found_keywords:
                print(f"    '{keyword}': {count}회 발견")
        
        # 페이지 소스에서 Hot Index 관련 내용 검색
        print(f"\n🔍 페이지 소스에서 Hot Index 검색:")
        page_source = driver.page_source
        
        hot_patterns = [
            r'"hot_index"\s*:\s*(\d+(?:\.\d+)?)',
            r'"hotIndex"\s*:\s*(\d+(?:\.\d+)?)',
            r'"score"\s*:\s*(\d+(?:\.\d+)?)',
            r'(\d+)\s*Hot Index',
            r'Hot Index\s*(\d+(?:\.\d+)?)'
        ]
        
        for pattern in hot_patterns:
            import re
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            if matches:
                print(f"  패턴 '{pattern}': {len(matches)}개 매치")
                for match in matches[:5]:  # 처음 5개만
                    print(f"    {match}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_table_structure() 