#!/usr/bin/env python3
"""
Rootdata Hot Index 최종 파서
JavaScript 로딩 완료 후 테이블을 파싱합니다.
"""

import time
import json
import logging
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RootdataFinalParser:
    def __init__(self):
        """최종 Rootdata 파서 초기화"""
        self.driver = None
        self.setup_driver()

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

    def wait_for_table_load(self, timeout=60):
        """테이블이 로드될 때까지 대기"""
        try:
            logger.info("테이블 로딩 대기 중...")
            
            # 테이블이 나타날 때까지 대기
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            
            # 추가 대기 시간 (JavaScript 실행 완료)
            time.sleep(10)
            
            # 테이블에 실제 데이터가 있는지 확인
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            if tables:
                for table in tables:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    if len(rows) > 1:  # 헤더 + 데이터 행이 있어야 함
                        logger.info(f"테이블 로딩 완료: {len(rows)}개 행")
                        return True
            
            logger.warning("테이블에 데이터가 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"테이블 로딩 실패: {e}")
            return False

    def extract_hot_index_data(self):
        """Hot Index 데이터 추출"""
        try:
            logger.info("Rootdata 웹사이트 접속 중...")
            self.driver.get("https://www.rootdata.com/")
            
            # 페이지 제목 확인
            title = self.driver.title
            logger.info(f"페이지 제목: {title}")
            
            # 테이블 로딩 대기
            if not self.wait_for_table_load():
                logger.error("테이블 로딩 실패")
                return []
            
            # 테이블에서 데이터 추출
            data = self.extract_from_table()
            
            if data:
                logger.info(f"총 {len(data)}개의 Hot Index 데이터 추출 완료")
            else:
                logger.warning("데이터 추출 실패")
            
            return data
            
        except Exception as e:
            logger.error(f"데이터 추출 실패: {e}")
            return []

    def extract_from_table(self):
        """테이블에서 데이터 추출"""
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
                            
                            # 순위 추출 (첫 번째 셀)
                            rank = 0
                            rank_cell = cells[0]
                            rank_text = rank_cell.text.strip()
                            
                            # 순위 텍스트에서 숫자 추출
                            rank_match = re.search(r'(\d+)', rank_text)
                            if rank_match:
                                rank = int(rank_match.group(1))
                            
                            # 프로젝트명 추출 (두 번째 셀)
                            project_name = ""
                            project_link = ""
                            
                            if len(cells) > 1:
                                project_cell = cells[1]
                                
                                # 링크가 있는 경우
                                links = project_cell.find_elements(By.TAG_NAME, "a")
                                if links:
                                    project_link = links[0].get_attribute("href") or ""
                                    project_name = links[0].text.strip()
                                else:
                                    project_name = project_cell.text.strip()
                            
                            # Hot Index 값 추출 (다섯 번째 셀 - "Hot Index Trend (24h)")
                            hot_index = 0
                            
                            if len(cells) > 4:
                                hot_index_cell = cells[4]
                                hot_index_text = hot_index_cell.text.strip()
                                
                                # 숫자 추출
                                hot_match = re.search(r'(\d+(?:\.\d+)?)', hot_index_text)
                                if hot_match:
                                    hot_index = float(hot_match.group(1))
                                
                                logger.info(f"  Hot Index 셀 텍스트: '{hot_index_text}' -> 값: {hot_index}")
                            
                            # 태그 정보 추출 (네 번째 셀)
                            tags = []
                            if len(cells) > 3:
                                tags_cell = cells[3]
                                tags_text = tags_cell.text.strip()
                                
                                # 태그 추출
                                tag_matches = re.findall(r'#([^#\s]+)', tags_text)
                                tags.extend(tag_matches)
                            
                            # 유효한 데이터인 경우 추가
                            if project_name and hot_index > 0:
                                data.append({
                                    'rank': rank,
                                    'project_name': project_name,
                                    'project_link': project_link,
                                    'hot_index': hot_index,
                                    'tags': tags,
                                    'raw_text': f"Rank: {rank}, Hot Index: {hot_index}"
                                })
                                
                                logger.info(f"  {rank}. {project_name} - Hot Index: {hot_index}")
                                
                    except Exception as e:
                        logger.warning(f"테이블 행 {row_idx + 1} 파싱 실패: {e}")
                        continue
            
            return data
            
        except Exception as e:
            logger.error(f"테이블 파싱 실패: {e}")
            return []

    def close(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()

def main():
    """메인 함수"""
    parser = RootdataFinalParser()
    
    try:
        logger.info("Rootdata 최종 파싱 시작...")
        data = parser.extract_hot_index_data()
        
        if data:
            logger.info("파싱된 데이터:")
            for i, item in enumerate(data[:10], 1):
                logger.info(f"  {i}. {item['project_name']} - Hot Index: {item['hot_index']}")
            
            # JSON 파일로 저장
            with open('rootdata_final_parsed_data.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'data': data
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"데이터를 rootdata_final_parsed_data.json에 저장 완료")
        else:
            logger.warning("파싱된 데이터가 없습니다")
            
    except Exception as e:
        logger.error(f"파싱 실패: {e}")
    finally:
        parser.close()

if __name__ == "__main__":
    main() 