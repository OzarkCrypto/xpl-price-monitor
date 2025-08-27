#!/usr/bin/env python3
"""
Rootdata 웹사이트 구조 디버그 스크립트
실제 페이지 구조를 자세히 분석합니다.
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def debug_website_structure():
    """웹사이트 구조를 자세히 분석합니다."""
    
    # Chrome 드라이버 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("🔍 Rootdata 웹사이트 구조 분석 시작...")
        
        # 페이지 접속
        driver.get("https://cn.rootdata.com/Projects")
        time.sleep(5)  # 페이지 로딩 대기
        
        print(f"📄 페이지 제목: {driver.title}")
        print(f"🌐 현재 URL: {driver.current_url}")
        
        # 1. 모든 요소의 클래스명 확인
        print("\n📋 모든 요소의 클래스명:")
        elements = driver.find_elements(By.CSS_SELECTOR, "*")
        classes = set()
        for element in elements:
            class_name = element.get_attribute("class")
            if class_name:
                classes.update(class_name.split())
        
        # 클래스명을 정렬하여 출력
        sorted_classes = sorted(list(classes))
        for i, class_name in enumerate(sorted_classes[:50]):  # 상위 50개만
            print(f"  {i+1:2d}. {class_name}")
        
        if len(sorted_classes) > 50:
            print(f"  ... 및 {len(sorted_classes) - 50}개 더")
        
        # 2. 특정 키워드가 포함된 클래스 찾기
        print("\n🔍 Hot Index 관련 클래스:")
        hot_classes = [cls for cls in sorted_classes if any(keyword in cls.lower() for keyword in ['hot', 'index', 'score', 'rank', 'project'])]
        for i, class_name in enumerate(hot_classes):
            print(f"  {i+1:2d}. {class_name}")
        
        # 3. 페이지 소스에서 특정 키워드 검색
        print("\n🔍 페이지 소스에서 키워드 검색:")
        page_source = driver.page_source.lower()
        
        keywords = ['hot index', 'hotindex', 'hot_index', 'score', 'rank', 'project', 'data']
        for keyword in keywords:
            count = page_source.count(keyword)
            if count > 0:
                print(f"  '{keyword}': {count}회 발견")
        
        # 4. 특정 요소들의 텍스트 내용 확인
        print("\n📝 주요 요소들의 텍스트:")
        
        # 제목 요소들
        headings = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")
        print(f"  제목 요소: {len(headings)}개")
        for i, heading in enumerate(headings[:10]):
            text = heading.text.strip()
            if text:
                print(f"    {i+1:2d}. {text[:100]}")
        
        # 링크 요소들
        links = driver.find_elements(By.CSS_SELECTOR, "a")
        print(f"  링크 요소: {len(links)}개")
        for i, link in enumerate(links[:10]):
            text = link.text.strip()
            href = link.get_attribute("href")
            if text and href:
                print(f"    {i+1:2d}. {text[:50]} -> {href[:100]}")
        
        # 5. JavaScript 변수 확인
        print("\n💻 JavaScript 변수 확인:")
        js_vars = driver.execute_script("""
            var vars = {};
            for (var key in window) {
                try {
                    var value = window[key];
                    if (value && typeof value === 'object' && value !== null) {
                        if (Array.isArray(value) && value.length > 0) {
                            vars[key] = { type: 'array', length: value.length, sample: value[0] };
                        } else if (typeof value === 'object') {
                            vars[key] = { type: 'object', keys: Object.keys(value).slice(0, 5) };
                        }
                    }
                } catch (e) {
                    // 접근 불가능한 속성 무시
                }
            }
            return vars;
        """)
        
        for key, info in js_vars.items():
            print(f"  {key}: {info}")
        
        # 6. 페이지의 모든 텍스트에서 Hot Index 관련 내용 찾기
        print("\n🔍 Hot Index 관련 텍스트:")
        all_text = driver.find_element(By.TAG_NAME, "body").text
        lines = all_text.split('\n')
        
        hot_lines = []
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['hot', 'index', 'score', 'rank']):
                hot_lines.append(line)
        
        for i, line in enumerate(hot_lines[:20]):
            print(f"  {i+1:2d}. {line[:100]}")
        
        if len(hot_lines) > 20:
            print(f"  ... 및 {len(hot_lines) - 20}개 더")
        
        # 7. 페이지 구조를 JSON으로 저장
        structure_data = {
            'title': driver.title,
            'url': driver.current_url,
            'classes': sorted_classes,
            'hot_classes': hot_classes,
            'headings': [h.text.strip() for h in headings if h.text.strip()],
            'links': [{'text': l.text.strip(), 'href': l.get_attribute('href')} for l in links if l.text.strip() and l.get_attribute('href')],
            'js_vars': js_vars,
            'hot_text_lines': hot_lines
        }
        
        with open('website_structure_debug.json', 'w', encoding='utf-8') as f:
            json.dump(structure_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 웹사이트 구조 정보를 website_structure_debug.json에 저장 완료")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_website_structure() 