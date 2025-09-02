#!/usr/bin/env python3
"""
Aave 포럼 HTML 구조 디버깅 스크립트
"""

import requests
from bs4 import BeautifulSoup

def debug_forum_structure():
    """포럼 HTML 구조 디버깅"""
    url = "https://governance.aave.com/c/governance/4"
    
    # User-Agent 설정
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"🔍 {url} 접속 중...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"✅ 응답 상태: {response.status_code}")
        print(f"📏 응답 크기: {len(response.text)} bytes")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print("\n🔍 HTML 구조 분석:")
        print("=" * 50)
        
        # 토픽 테이블 찾기
        print("1. 토픽 테이블 검색:")
        topic_table = soup.find('table', class_='topic-list')
        if topic_table:
            print("   ✅ topic-list 테이블 발견")
            
            # 테이블 행들 찾기
            rows = topic_table.find_all('tr', class_='topic-list-item')
            print(f"   📊 topic-list-item 행 수: {len(rows)}")
            
            # 첫 번째 행의 구조 분석
            if len(rows) > 0:
                first_row = rows[0]
                print(f"   🔍 첫 번째 데이터 행 클래스: {first_row.get('class', 'No class')}")
                
                # 각 셀 분석
                cells = first_row.find_all('td')
                print(f"   📋 셀 수: {len(cells)}")
                
                for i, cell in enumerate(cells):
                    cell_class = cell.get('class', 'No class')
                    cell_text = cell.get_text(strip=True)[:100]
                    print(f"     셀 {i}: 클래스={cell_class}, 내용={cell_text}")
                    
                    # 링크가 있는지 확인
                    links = cell.find_all('a')
                    if links:
                        for j, link in enumerate(links):
                            href = link.get('href', 'No href')
                            text = link.get_text(strip=True)[:50]
                            print(f"       링크 {j}: href={href}, text={text}")
                
                # 마지막 셀 (활동 시간) 자세히 분석
                if len(cells) >= 5:
                    last_cell = cells[4]
                    print(f"\n   🔍 마지막 셀 (활동 시간) 상세 분석:")
                    print(f"     클래스: {last_cell.get('class', 'No class')}")
                    print(f"     내용: {last_cell.get_text(strip=True)}")
                    print(f"     HTML: {last_cell}")
                    
                    # 시간 관련 요소 찾기
                    time_elements = last_cell.find_all(['time', 'span', 'div'])
                    print(f"     시간 요소 수: {len(time_elements)}")
                    for elem in time_elements:
                        print(f"       요소: {elem.name}, 클래스: {elem.get('class', 'No class')}, 내용: {elem.get_text(strip=True)}")
        
        # 토픽 관련 요소들 찾기
        print("\n2. 토픽 관련 요소 검색:")
        
        # topic-list-item 클래스
        topic_items = soup.find_all(class_='topic-list-item')
        print(f"   📋 topic-list-item: {len(topic_items)}개")
        
        # 다른 가능한 클래스들
        possible_classes = ['topic', 'thread', 'post', 'item']
        for class_name in possible_classes:
            elements = soup.find_all(class_=class_name)
            print(f"   📋 {class_name}: {len(elements)}개")
        
        # 링크 패턴 분석
        print("\n3. 링크 패턴 분석:")
        links = soup.find_all('a', href=True)
        topic_links = [link for link in links if '/t/' in link.get('href', '')]
        print(f"   🔗 /t/ 패턴 링크: {len(topic_links)}개")
        
        if topic_links:
            print("   📋 첫 번째 토픽 링크들:")
            for i, link in enumerate(topic_links[:5]):
                href = link.get('href', '')
                text = link.get_text(strip=True)[:100]
                print(f"     {i+1}: {href} - {text}")
        
        # 활동 시간 관련 요소
        print("\n4. 활동 시간 요소 검색:")
        time_elements = soup.find_all(['time', 'span', 'div'], class_=lambda x: x and 'time' in x.lower() if x else False)
        print(f"   ⏰ 시간 관련 요소: {len(time_elements)}개")
        
        # 활동 관련 요소
        activity_elements = soup.find_all(['span', 'div'], class_=lambda x: x and 'activity' in x.lower() if x else False)
        print(f"   📊 활동 관련 요소: {len(activity_elements)}개")
        
        # num 클래스 요소들 (통계 정보)
        num_elements = soup.find_all(class_='num')
        print(f"   📊 num 클래스 요소: {len(num_elements)}개")
        for i, elem in enumerate(num_elements[:10]):
            print(f"     {i+1}: 클래스={elem.get('class', 'No class')}, 내용={elem.get_text(strip=True)}")
        
        # HTML 샘플 출력
        print("\n5. HTML 샘플 (처음 1000자):")
        print("=" * 50)
        print(response.text[:1000])
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    debug_forum_structure()
