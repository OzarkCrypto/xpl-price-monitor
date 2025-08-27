#!/usr/bin/env python3
"""
Rootdata Hot Index Selenium 파서
JavaScript 기반 웹사이트에서 데이터를 추출합니다.
"""

import time
import json
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RootdataSeleniumParser:
    def __init__(self):
        """Selenium 파서 초기화"""
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
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 백그라운드 실행
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Chrome 드라이버 자동 설치 및 설정
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info("Chrome 드라이버 설정 완료")
            
        except Exception as e:
            logger.error(f"드라이버 설정 실패: {e}")
            raise

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

    def wait_for_page_load(self, timeout=30):
        """페이지 로딩 대기"""
        try:
            # Nuxt.js 앱이 로드될 때까지 대기
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.ID, "__nuxt"))
            )
            
            # 추가 대기 시간 (JavaScript 실행 완료)
            time.sleep(3)
            logger.info("페이지 로딩 완료")
            return True
            
        except Exception as e:
            logger.error(f"페이지 로딩 실패: {e}")
            return False

    def extract_hot_index_data(self):
        """Hot Index 데이터 추출"""
        try:
            logger.info("Rootdata Projects 페이지 접속 중...")
            self.driver.get("https://cn.rootdata.com/Projects")
            
            # 페이지 로딩 대기
            if not self.wait_for_page_load():
                return []
            
            # 여러 가지 방법으로 데이터 추출 시도
            data = []
            
            # 방법 1: 테이블에서 데이터 추출
            data.extend(self.extract_from_table())
            
            # 방법 2: 카드 형태에서 데이터 추출
            data.extend(self.extract_from_cards())
            
            # 방법 3: JavaScript 변수에서 데이터 추출
            data.extend(self.extract_from_javascript())
            
            # 중복 제거 및 정렬
            unique_data = self.remove_duplicates(data)
            
            logger.info(f"총 {len(unique_data)}개의 Hot Index 데이터 추출 완료")
            return unique_data
            
        except Exception as e:
            logger.error(f"데이터 추출 실패: {e}")
            return []

    def extract_from_table(self):
        """테이블에서 데이터 추출"""
        data = []
        try:
            # 테이블 요소 찾기
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            
            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 3:
                        try:
                            # 순위
                            rank_text = cells[0].text.strip()
                            rank = int(rank_text) if rank_text.isdigit() else 0
                            
                            # 프로젝트명
                            project_name = cells[2].text.strip()
                            if not project_name:
                                continue
                            
                            # 프로젝트명 정리
                            project_name = self.clean_project_name(project_name)
                            
                            # 프로젝트 링크
                            project_link = ""
                            link_elements = cells[2].find_elements(By.TAG_NAME, "a")
                            if link_elements:
                                href = link_elements[0].get_attribute("href")
                                if href:
                                    project_link = href
                            
                            # Hot Index 값
                            hot_index = 0
                            raw_text = ""
                            
                            # 셀 내용에서 hot index 관련 텍스트 찾기
                            cell_text = cells[2].text
                            if "Hot Index:" in cell_text:
                                import re
                                match = re.search(r'Hot Index:\s*(\d+(?:\.\d+)?)', cell_text)
                                if match:
                                    hot_index = float(match.group(1))
                                    raw_text = match.group(0)
                            
                            if hot_index > 0 and project_name:
                                data.append({
                                    'rank': rank,
                                    'project_name': project_name,
                                    'project_link': project_link,
                                    'hot_index': hot_index,
                                    'raw_text': raw_text
                                })
                                
                        except Exception as e:
                            logger.warning(f"테이블 행 파싱 실패: {e}")
                            continue
            
            logger.info(f"테이블에서 {len(data)}개 데이터 추출")
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
                '[data-v-*]',  # Vue.js 컴포넌트
                '.v-card',
                '.el-card'
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
                                    'h3, h4, .project-name, .title, .name')
                                
                                if name_elements:
                                    project_name = name_elements[0].text.strip()
                                    project_name = self.clean_project_name(project_name)
                                    
                                    # Hot Index 값
                                    hot_index = 0
                                    raw_text = ""
                                    
                                    # Hot Index 관련 텍스트 찾기
                                    hot_elements = card.find_elements(By.CSS_SELECTOR,
                                        '*[class*="hot"], *[class*="index"], *[class*="score"]')
                                    
                                    for element in hot_elements:
                                        text = element.text.strip()
                                        if any(keyword in text.lower() for keyword in ['hot', 'index', 'score']):
                                            import re
                                            match = re.search(r'(\d+(?:\.\d+)?)', text)
                                            if match:
                                                hot_index = float(match.group(1))
                                                raw_text = text
                                                break
                                    
                                    if hot_index > 0 and project_name:
                                        data.append({
                                            'rank': i + 1,
                                            'project_name': project_name,
                                            'project_link': "",
                                            'hot_index': hot_index,
                                            'raw_text': raw_text
                                        })
                                        
                            except Exception as e:
                                logger.warning(f"카드 파싱 실패: {e}")
                                continue
                        
                        if data:
                            break
                            
                except Exception as e:
                    logger.warning(f"카드 선택자 {selector} 실패: {e}")
                    continue
            
            logger.info(f"카드에서 {len(data)}개 데이터 추출")
            return data
            
        except Exception as e:
            logger.error(f"카드 파싱 실패: {e}")
            return []

    def extract_from_javascript(self):
        """JavaScript 변수에서 데이터 추출"""
        data = []
        try:
            # 페이지의 JavaScript 변수에서 데이터 추출
            script = """
            // 페이지의 전역 변수들 확인
            var data = {};
            
            // window 객체의 속성들 확인
            for (var key in window) {
                if (key.toLowerCase().includes('project') || 
                    key.toLowerCase().includes('data') || 
                    key.toLowerCase().includes('list')) {
                    try {
                        var value = window[key];
                        if (value && typeof value === 'object') {
                            data[key] = value;
                        }
                    } catch (e) {
                        // 접근 불가능한 속성 무시
                    }
                }
            }
            
            // document의 data 속성들 확인
            var elements = document.querySelectorAll('[data-*]');
            elements.forEach(function(el) {
                for (var attr of el.attributes) {
                    if (attr.name.startsWith('data-')) {
                        try {
                            var value = JSON.parse(attr.value);
                            if (value && typeof value === 'object') {
                                data[attr.name] = value;
                            }
                        } catch (e) {
                            data[attr.name] = attr.value;
                        }
                    }
                }
            });
            
            return JSON.stringify(data);
            """
            
            result = self.driver.execute_script(script)
            if result:
                js_data = json.loads(result)
                logger.info(f"JavaScript에서 {len(js_data)}개 변수 발견")
                
                # Hot Index 관련 데이터 찾기
                for key, value in js_data.items():
                    if isinstance(value, (list, dict)):
                        # 데이터 구조 분석
                        if self.analyze_js_data(value):
                            logger.info(f"유용한 데이터 구조 발견: {key}")
                            # 여기서 더 자세한 파싱 로직 추가 가능
            
            return data
            
        except Exception as e:
            logger.error(f"JavaScript 파싱 실패: {e}")
            return []

    def analyze_js_data(self, data):
        """JavaScript 데이터 구조 분석"""
        try:
            if isinstance(data, list) and len(data) > 0:
                first_item = data[0]
                if isinstance(first_item, dict):
                    # Hot Index 관련 키워드 확인
                    keys = first_item.keys()
                    hot_keywords = ['hot', 'index', 'score', 'rank', 'name', 'project']
                    
                    if any(keyword in str(keys).lower() for keyword in hot_keywords):
                        return True
            
            return False
            
        except Exception as e:
            return False

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
            logger.info("Chrome 드라이버 종료")

def main():
    """메인 함수"""
    parser = RootdataSeleniumParser()
    
    try:
        logger.info("Rootdata Hot Index 파싱 시작...")
        data = parser.extract_hot_index_data()
        
        if data:
            logger.info("파싱된 데이터:")
            for i, item in enumerate(data[:10], 1):
                logger.info(f"  {i}. {item['project_name']} - Hot Index: {item['hot_index']}")
            
            # JSON 파일로 저장
            with open('rootdata_parsed_data.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'data': data
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"데이터를 rootdata_parsed_data.json에 저장 완료")
        else:
            logger.warning("파싱된 데이터가 없습니다")
            
    except Exception as e:
        logger.error(f"파싱 실패: {e}")
    finally:
        parser.close()

if __name__ == "__main__":
    main() 