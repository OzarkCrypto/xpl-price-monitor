#!/usr/bin/env python3
"""
Rootdata Hot Index 새로운 웹사이트 파서
새로운 웹사이트 구조에 맞춰 데이터를 파싱합니다.
"""

import time
import json
import logging
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RootdataNewParser:
    def __init__(self):
        """새로운 Rootdata 파서 초기화"""
        self.driver = None
        self.setup_driver()
        
        # 프로젝트 이름 매핑 (긴 이름을 짧고 명확하게)
        self.project_name_mapping = {
            'Game developer platformOVERTAKE': 'OVERTAKE',
            'A Web3 Privacy Acceleration so...': 'Multiple Network',
            'Fantasy sports platformFootball.Fun': 'Football.Fun',
            'Crypto Lending PlatformWorld Liberty Financial': 'World Liberty Financial',
            'Meme CoinYZY MoneyYZY': 'YZY Money',
            'Connecting Bitcoin to DeFi with LBTCLombard': 'Lombard',
            'Layer 1 blockchainSuiSUI': 'SUI',
            'Intention-driven modular blockchainWarden Protocol': 'Warden Protocol',
            'Token launchpadheavenLIGHT': 'heaven',
            'Cross-platform play-and-earn d...': 'Xterio'
        }

    def setup_driver(self):
        """Chrome 드라이버 설정"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def clean_project_name(self, project_name):
        """프로젝트 이름을 읽기 쉽게 정리합니다."""
        if not project_name:
            return "Unknown Project"
        
        # 1. 매핑된 이름이 있으면 사용
        if project_name in self.project_name_mapping:
            return self.project_name_mapping[project_name]
        
        # 2. 일반적인 패턴 정리
        # "PlatformName" 형태를 "Name"으로 변환
        if 'platform' in project_name.lower():
            parts = project_name.split('platform')
            if len(parts) > 1 and parts[1]:
                project_name = parts[1]
        
        # "TypeName" 형태를 "Name"으로 변환
        if len(project_name) > 30:
            # 첫 번째 공백이나 특수문자 전까지만 사용
            separators = ['.', ' is ', ' is a ', ' - ', ' | ', ' / ']
            for sep in separators:
                if sep in project_name:
                    parts = project_name.split(sep)
                    if parts[0].strip():
                        project_name = parts[0].strip()
                        break
            
            # 길이 제한
            if len(project_name) > 30:
                project_name = project_name[:27] + "..."
        
        return project_name.strip()

    def extract_hot_index_data(self):
        """Hot Index 데이터 추출"""
        try:
            logger.info("새로운 Rootdata 웹사이트 접속 중...")
            self.driver.get("https://www.rootdata.com/")
            time.sleep(5)  # 페이지 로딩 대기
            
            # 페이지 제목 확인
            title = self.driver.title
            logger.info(f"페이지 제목: {title}")
            
            data = []
            
            # 방법 1: 테이블에서 데이터 추출 (주요 방법)
            table_data = self.extract_from_table()
            if table_data:
                data.extend(table_data)
                logger.info(f"테이블에서 {len(table_data)}개 데이터 추출")
            
            # 방법 2: 카드 형태에서 데이터 추출
            card_data = self.extract_from_cards()
            if card_data:
                data.extend(card_data)
                logger.info(f"카드에서 {len(card_data)}개 데이터 추출")
            
            # 중복 제거 및 정렬
            unique_data = self.remove_duplicates(data)
            logger.info(f"총 {len(unique_data)}개의 Hot Index 데이터 추출 완료")
            
            return unique_data
            
        except Exception as e:
            logger.error(f"데이터 추출 실패: {e}")
            return []

    def extract_from_table(self):
        """테이블에서 데이터 추출 (주요 방법)"""
        data = []
        try:
            # 테이블 요소 찾기
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            logger.info(f"테이블 {len(tables)}개 발견")
            
            for table_idx, table in enumerate(tables):
                logger.info(f"테이블 {table_idx + 1} 분석 중...")
                
                # 테이블 헤더 확인
                headers = table.find_elements(By.TAG_NAME, "th")
                if headers:
                    header_texts = [h.text.strip() for h in headers]
                    logger.info(f"테이블 헤더: {header_texts}")
                
                # 테이블 행 처리
                rows = table.find_elements(By.TAG_NAME, "tr")
                logger.info(f"테이블 행 {len(rows)}개 발견")
                
                for row_idx, row in enumerate(rows):
                    try:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 3:  # 최소 3개 셀이 있어야 함
                            
                            # 순위 추출
                            rank = 0
                            rank_cell = cells[0]
                            rank_text = rank_cell.text.strip()
                            
                            # 순위 텍스트에서 숫자 추출
                            rank_match = re.search(r'(\d+)', rank_text)
                            if rank_match:
                                rank = int(rank_match.group(1))
                            
                            # 프로젝트명 추출
                            project_name = ""
                            project_link = ""
                            
                            # 프로젝트명이 있는 셀 찾기 (보통 2번째 셀)
                            if len(cells) > 1:
                                project_cell = cells[1]
                                
                                # 링크가 있는 경우
                                links = project_cell.find_elements(By.TAG_NAME, "a")
                                if links:
                                    project_link = links[0].get_attribute("href") or ""
                                    project_name = links[0].text.strip()
                                else:
                                    project_name = project_cell.text.strip()
                            
                            # Hot Index 값 추출
                            hot_index = 0
                            hot_index_cell = None
                            
                            # Hot Index가 있는 셀 찾기
                            for i, cell in enumerate(cells):
                                cell_text = cell.text.strip()
                                if any(keyword in cell_text.lower() for keyword in ['hot', 'index', 'score']):
                                    hot_index_cell = cell
                                    break
                            
                            if hot_index_cell:
                                # 숫자 추출
                                hot_match = re.search(r'(\d+(?:\.\d+)?)', hot_index_cell.text)
                                if hot_match:
                                    hot_index = float(hot_match.group(1))
                            
                            # 태그 정보 추출
                            tags = []
                            for cell in cells:
                                cell_text = cell.text.strip()
                                if cell_text.startswith('#') or '#' in cell_text:
                                    # 태그 추출
                                    tag_matches = re.findall(r'#([^#\s]+)', cell_text)
                                    tags.extend(tag_matches)
                            
                            # 유효한 데이터인 경우 추가
                            if project_name and hot_index > 0:
                                # 프로젝트명 정리
                                clean_name = self.clean_project_name(project_name)
                                
                                data.append({
                                    'rank': rank,
                                    'project_name': clean_name,
                                    'project_link': project_link,
                                    'hot_index': hot_index,
                                    'tags': tags,
                                    'raw_text': f"Rank: {rank}, Hot Index: {hot_index}"
                                })
                                
                                logger.info(f"  {rank}. {clean_name} - Hot Index: {hot_index}")
                                
                    except Exception as e:
                        logger.warning(f"테이블 행 {row_idx + 1} 파싱 실패: {e}")
                        continue
            
            return data
            
        except Exception as e:
            logger.error(f"테이블 파싱 실패: {e}")
            return []

    def extract_from_cards(self):
        """카드 형태에서 데이터 추출"""
        data = []
        try:
            # 카드 형태의 프로젝트 요소 찾기
            card_selectors = [
                '.project-card',
                '.project-item',
                '.card',
                '.v-card',
                '.el-card',
                '[class*="card"]',
                '[class*="project"]'
            ]
            
            for selector in card_selectors:
                try:
                    cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if cards:
                        logger.info(f"카드 요소 {len(cards)}개 발견: {selector}")
                        
                        for i, card in enumerate(cards[:20]):  # 상위 20개만
                            try:
                                # 프로젝트명
                                name_elements = card.find_elements(By.CSS_SELECTOR, 
                                    'h3, h4, .project-name, .title, .name, a')
                                
                                if name_elements:
                                    project_name = name_elements[0].text.strip()
                                    project_name = self.clean_project_name(project_name)
                                    
                                    # Hot Index 값
                                    hot_index = 0
                                    
                                    # Hot Index 관련 텍스트 찾기
                                    hot_elements = card.find_elements(By.CSS_SELECTOR,
                                        '*[class*="hot"], *[class*="index"], *[class*="score"]')
                                    
                                    for element in hot_elements:
                                        text = element.text.strip()
                                        if any(keyword in text.lower() for keyword in ['hot', 'index', 'score']):
                                            match = re.search(r'(\d+(?:\.\d+)?)', text)
                                            if match:
                                                hot_index = float(match.group(1))
                                                break
                                    
                                    if hot_index > 0 and project_name:
                                        data.append({
                                            'rank': i + 1,
                                            'project_name': project_name,
                                            'project_link': "",
                                            'hot_index': hot_index,
                                            'tags': [],
                                            'raw_text': f"Hot Index: {hot_index}"
                                        })
                                        
                            except Exception as e:
                                logger.warning(f"카드 파싱 실패: {e}")
                                continue
                        
                        if data:
                            break
                            
                except Exception as e:
                    logger.warning(f"카드 선택자 {selector} 실패: {e}")
                    continue
            
            return data
            
        except Exception as e:
            logger.error(f"카드 파싱 실패: {e}")
            return []

    def remove_duplicates(self, data):
        """중복 데이터 제거"""
        seen = set()
        unique_data = []
        
        for item in data:
            # 프로젝트명과 Hot Index로 중복 판단
            key = (item['project_name'], item['hot_index'])
            if key not in seen:
                seen.add(key)
                unique_data.append(item)
        
        # Hot Index 순으로 정렬
        unique_data.sort(key=lambda x: x['hot_index'], reverse=True)
        
        return unique_data

    def close(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()

def main():
    """메인 함수"""
    parser = RootdataNewParser()
    
    try:
        logger.info("새로운 Rootdata 웹사이트 파싱 시작...")
        data = parser.extract_hot_index_data()
        
        if data:
            logger.info("파싱된 데이터:")
            for i, item in enumerate(data[:10], 1):
                logger.info(f"  {i}. {item['project_name']} - Hot Index: {item['hot_index']}")
            
            # JSON 파일로 저장
            with open('rootdata_new_parsed_data.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'data': data
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"데이터를 rootdata_new_parsed_data.json에 저장 완료")
        else:
            logger.warning("파싱된 데이터가 없습니다")
            
    except Exception as e:
        logger.error(f"파싱 실패: {e}")
    finally:
        parser.close()

if __name__ == "__main__":
    main() 