#!/usr/bin/env python3
"""
Rootdata Hot Index 고급 JavaScript 파서
JavaScript 변수와 객체에서 데이터를 추출합니다.
"""

import time
import json
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedJSParser:
    def __init__(self):
        """고급 JavaScript 파서 초기화"""
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """Chrome 드라이버 설정"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def extract_hot_index_data(self):
        """Hot Index 데이터 추출"""
        try:
            logger.info("Rootdata Projects 페이지 접속 중...")
            self.driver.get("https://cn.rootdata.com/Projects")
            time.sleep(5)  # 페이지 로딩 대기
            
            data = []
            
            # 방법 1: __NUXT__ 객체에서 데이터 추출
            nuxt_data = self.extract_from_nuxt()
            if nuxt_data:
                data.extend(nuxt_data)
                logger.info(f"__NUXT__에서 {len(nuxt_data)}개 데이터 추출")
            
            # 방법 2: 전역 변수에서 데이터 추출
            global_data = self.extract_from_global_vars()
            if global_data:
                data.extend(global_data)
                logger.info(f"전역 변수에서 {len(global_data)}개 데이터 추출")
            
            # 방법 3: DOM 요소에서 데이터 추출
            dom_data = self.extract_from_dom()
            if dom_data:
                data.extend(dom_data)
                logger.info(f"DOM에서 {len(dom_data)}개 데이터 추출")
            
            # 방법 4: 페이지 소스에서 직접 추출
            source_data = self.extract_from_page_source()
            if source_data:
                data.extend(source_data)
                logger.info(f"페이지 소스에서 {len(source_data)}개 데이터 추출")
            
            # 중복 제거 및 정렬
            unique_data = self.remove_duplicates(data)
            logger.info(f"총 {len(unique_data)}개의 Hot Index 데이터 추출 완료")
            
            return unique_data
            
        except Exception as e:
            logger.error(f"데이터 추출 실패: {e}")
            return []

    def extract_from_nuxt(self):
        """__NUXT__ 객체에서 데이터 추출"""
        data = []
        try:
            script = """
            try {
                if (window.__NUXT__ && window.__NUXT__.state) {
                    var state = window.__NUXT__.state;
                    var result = [];
                    
                    // state 객체의 모든 속성 탐색
                    for (var key in state) {
                        var value = state[key];
                        if (value && typeof value === 'object') {
                            // 배열인 경우
                            if (Array.isArray(value)) {
                                for (var i = 0; i < value.length; i++) {
                                    var item = value[i];
                                    if (item && typeof item === 'object') {
                                        // Hot Index 관련 데이터 찾기
                                        if (item.hot_index || item.hotIndex || item.score || item.rank) {
                                            result.push({
                                                source: 'nuxt_state_' + key,
                                                data: item
                                            });
                                        }
                                    }
                                }
                            }
                            // 객체인 경우
                            else if (value.data && Array.isArray(value.data)) {
                                for (var i = 0; i < value.data.length; i++) {
                                    var item = value.data[i];
                                    if (item && typeof item === 'object') {
                                        if (item.hot_index || item.hotIndex || item.score || item.rank) {
                                            result.push({
                                                source: 'nuxt_state_' + key + '_data',
                                                data: item
                                            });
                                        }
                                    }
                                }
                            }
                        }
                    }
                    
                    return result;
                }
                return [];
            } catch (e) {
                return { error: e.message };
            }
            """
            
            result = self.driver.execute_script(script)
            if result and isinstance(result, list):
                for item in result:
                    if 'data' in item:
                        parsed_item = self.parse_js_item(item['data'])
                        if parsed_item:
                            data.append(parsed_item)
            
            return data
            
        except Exception as e:
            logger.error(f"__NUXT__ 파싱 실패: {e}")
            return []

    def extract_from_global_vars(self):
        """전역 변수에서 데이터 추출"""
        data = []
        try:
            script = """
            try {
                var result = [];
                
                // window 객체의 모든 속성 탐색
                for (var key in window) {
                    try {
                        var value = window[key];
                        
                        // 배열인 경우
                        if (Array.isArray(value) && value.length > 0) {
                            for (var i = 0; i < value.length; i++) {
                                var item = value[i];
                                if (item && typeof item === 'object') {
                                    if (item.hot_index || item.hotIndex || item.score || item.rank) {
                                        result.push({
                                            source: 'global_' + key,
                                            data: item
                                        });
                                    }
                                }
                            }
                        }
                        
                        // 객체인 경우
                        else if (value && typeof value === 'object' && value !== null) {
                            // data 속성이 있는 경우
                            if (value.data && Array.isArray(value.data)) {
                                for (var i = 0; i < value.data.length; i++) {
                                    var item = value.data[i];
                                    if (item && typeof item === 'object') {
                                        if (item.hot_index || item.hotIndex || item.score || item.rank) {
                                            result.push({
                                                source: 'global_' + key + '_data',
                                                data: item
                                            });
                                        }
                                    }
                                }
                            }
                            
                            // 직접 Hot Index 데이터가 있는 경우
                            if (value.hot_index || value.hotIndex || value.score || value.rank) {
                                result.push({
                                    source: 'global_' + key + '_direct',
                                    data: value
                                });
                            }
                        }
                        
                    } catch (e) {
                        // 개별 속성 접근 실패 무시
                    }
                }
                
                return result;
            } catch (e) {
                return { error: e.message };
            }
            """
            
            result = self.driver.execute_script(script)
            if result and isinstance(result, list):
                for item in result:
                    if 'data' in item:
                        parsed_item = self.parse_js_item(item['data'])
                        if parsed_item:
                            data.append(parsed_item)
            
            return data
            
        except Exception as e:
            logger.error(f"전역 변수 파싱 실패: {e}")
            return []

    def extract_from_dom(self):
        """DOM 요소에서 데이터 추출"""
        data = []
        try:
            # data 속성이 있는 요소들 찾기
            script = """
            try {
                var result = [];
                var elements = document.querySelectorAll('[data-*]');
                
                elements.forEach(function(el) {
                    for (var attr of el.attributes) {
                        if (attr.name.startsWith('data-')) {
                            try {
                                var value = JSON.parse(attr.value);
                                if (value && typeof value === 'object') {
                                    if (value.hot_index || value.hotIndex || value.score || value.rank) {
                                        result.push({
                                            source: 'dom_' + attr.name,
                                            data: value
                                        });
                                    }
                                }
                            } catch (e) {
                                // JSON 파싱 실패 무시
                            }
                        }
                    }
                });
                
                return result;
            } catch (e) {
                return { error: e.message };
            }
            """
            
            result = self.driver.execute_script(script)
            if result and isinstance(result, list):
                for item in result:
                    if 'data' in item:
                        parsed_item = self.parse_js_item(item['data'])
                        if parsed_item:
                            data.append(parsed_item)
            
            return data
            
        except Exception as e:
            logger.error(f"DOM 파싱 실패: {e}")
            return []

    def extract_from_page_source(self):
        """페이지 소스에서 직접 데이터 추출"""
        data = []
        try:
            # 페이지 소스에서 JSON 형태의 데이터 찾기
            script = """
            try {
                var result = [];
                var pageSource = document.documentElement.outerHTML;
                
                // JSON 형태의 데이터 패턴 찾기
                var patterns = [
                    /"hot_index"\s*:\s*(\d+(?:\.\d+)?)/g,
                    /"hotIndex"\s*:\s*(\d+(?:\.\d+)?)/g,
                    /"score"\s*:\s*(\d+(?:\.\d+)?)/g,
                    /"rank"\s*:\s*(\d+)/g
                ];
                
                patterns.forEach(function(pattern) {
                    var match;
                    while ((match = pattern.exec(pageSource)) !== null) {
                        result.push({
                            value: parseFloat(match[1]),
                            pattern: pattern.source,
                            index: match.index
                        });
                    }
                });
                
                return result;
            } catch (e) {
                return { error: e.message };
            }
            """
            
            result = self.driver.execute_script(script)
            if result and isinstance(result, list):
                for item in result:
                    if 'value' in item:
                        data.append({
                            'rank': 0,
                            'project_name': f"Project_{item['index']}",
                            'project_link': "",
                            'hot_index': item['value'],
                            'raw_text': f"Pattern: {item['pattern']}"
                        })
            
            return data
            
        except Exception as e:
            logger.error(f"페이지 소스 파싱 실패: {e}")
            return []

    def parse_js_item(self, item):
        """JavaScript 객체를 파싱 가능한 형태로 변환"""
        try:
            # Hot Index 값 추출
            hot_index = 0
            if 'hot_index' in item:
                hot_index = float(item['hot_index'])
            elif 'hotIndex' in item:
                hot_index = float(item['hotIndex'])
            elif 'score' in item:
                hot_index = float(item['score'])
            
            if hot_index <= 0:
                return None
            
            # 프로젝트명 추출
            project_name = "Unknown Project"
            if 'name' in item:
                project_name = str(item['name'])
            elif 'project_name' in item:
                project_name = str(item['project_name'])
            elif 'title' in item:
                project_name = str(item['title'])
            
            # 순위 추출
            rank = 0
            if 'rank' in item:
                rank = int(item['rank'])
            
            # 링크 추출
            project_link = ""
            if 'link' in item:
                project_link = str(item['link'])
            elif 'url' in item:
                project_link = str(item['url'])
            
            return {
                'rank': rank,
                'project_name': project_name,
                'project_link': project_link,
                'hot_index': hot_index,
                'raw_text': f"Hot Index: {hot_index}"
            }
            
        except Exception as e:
            logger.warning(f"JavaScript 객체 파싱 실패: {e}")
            return None

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
    parser = AdvancedJSParser()
    
    try:
        logger.info("고급 JavaScript 파싱 시작...")
        data = parser.extract_hot_index_data()
        
        if data:
            logger.info("파싱된 데이터:")
            for i, item in enumerate(data[:10], 1):
                logger.info(f"  {i}. {item['project_name']} - Hot Index: {item['hot_index']}")
            
            # JSON 파일로 저장
            with open('advanced_parsed_data.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'data': data
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"데이터를 advanced_parsed_data.json에 저장 완료")
        else:
            logger.warning("파싱된 데이터가 없습니다")
            
    except Exception as e:
        logger.error(f"파싱 실패: {e}")
    finally:
        parser.close()

if __name__ == "__main__":
    main() 