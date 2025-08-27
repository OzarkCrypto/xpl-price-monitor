#!/usr/bin/env python3
"""
Rootdata Hot Index 모니터링 봇
매시간 정각에 hot index TOP 10을 텔레그램으로 전송
"""

import os
import sys
import time
import schedule
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import logging
import pickle
import json
import re

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rootdata_hot_index.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RootdataHotIndexMonitor:
    def __init__(self):
        """Rootdata Hot Index 모니터 초기화"""
        load_dotenv()
        
        # 텔레그램 설정 (Rootdata 전용)
        self.telegram_bot_token = os.getenv('ROOTDATA_BOT_TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
        
        # 메인 채널 ID
        self.telegram_chat_id = os.getenv('ROOTDATA_CHAT_ID') or os.getenv('TELEGRAM_CHAT_ID')
        
        # 추가 채널 ID (선택사항)
        self.extra_chat_id = os.getenv('ROOTDATA_EXTRA_CHAT_ID')
        
        if not self.telegram_bot_token or not self.telegram_chat_id:
            raise ValueError("ROOTDATA_BOT_TOKEN/ROOTDATA_CHAT_ID 또는 TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID 환경 변수가 필요합니다.")
        
        # 전송할 채널 목록 생성
        self.chat_ids = [self.telegram_chat_id]
        if self.extra_chat_id:
            self.chat_ids.append(self.extra_chat_id)

        # 이전 데이터 로드
        self.previous_data = self.load_previous_data()
        
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
            'Cross-platform play-and-earn d...': 'Xterio',
            'Decentralized identity platform': 'Identity Platform',
            'DeFi lending protocol': 'Lending Protocol',
            'NFT marketplace': 'NFT Market',
            'GameFi platform': 'GameFi',
            'DEX aggregator': 'DEX Aggregator',
            'Cross-chain bridge': 'Bridge',
            'Oracle network': 'Oracle',
            'Staking platform': 'Staking',
            'Yield farming': 'Yield Farm',
            'Governance token': 'Governance'
        }

    def clean_project_name(self, project_name):
        """
        프로젝트 이름을 읽기 쉽게 정리합니다.
        """
        if not project_name:
            return "Unknown Project"
        
        # 1. 매핑된 이름이 있으면 사용
        if project_name in self.project_name_mapping:
            return self.project_name_mapping[project_name]
        
        # 2. 일반적인 패턴 정리
        # "PlatformName" 형태를 "Name"으로 변환
        if re.search(r'platform[A-Z]', project_name):
            clean_name = re.sub(r'platform([A-Z][a-zA-Z]+)', r'\1', project_name)
            if clean_name:
                project_name = clean_name
        
        # "TypeName" 형태를 "Name"으로 변환  
        elif re.search(r'[A-Z][a-z]+[A-Z][a-zA-Z]+', project_name):
            # 첫 번째 대문자+소문자 조합을 제거
            clean_name = re.sub(r'^[A-Z][a-z]+', '', project_name)
            if clean_name:
                project_name = clean_name
        
        # 3. 특수 구분자로 분리
        separators = ['.', ' is ', ' is a ', ' - ', ' | ', ' / ']
        for sep in separators:
            if sep in project_name:
                parts = project_name.split(sep)
                if parts[0].strip():
                    project_name = parts[0].strip()
                    break
        
        # 4. 길이 제한 및 정리
        if len(project_name) > 40:
            # 마지막 단어가 완전하지 않으면 제거
            words = project_name.split()
            if len(words) > 1:
                # 마지막 단어가 너무 짧으면 제거
                if len(words[-1]) < 3:
                    words = words[:-1]
                project_name = ' '.join(words)
            
            # 여전히 길면 자르기
            if len(project_name) > 40:
                project_name = project_name[:37] + "..."
        
        # 5. 불필요한 공백 제거
        project_name = re.sub(r'\s+', ' ', project_name).strip()
        
        return project_name if project_name else "Unknown Project"

    def load_previous_data(self):
        """이전 데이터를 로드합니다."""
        try:
            if os.path.exists('rootdata_hot_index_history.json'):
                with open('rootdata_hot_index_history.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"이전 데이터 로드 완료: {len(data.get('data', []))}개 프로젝트")
                    return data
        except Exception as e:
            logger.warning(f"이전 데이터 로드 실패: {e}")
        
        return {'data': [], 'timestamp': None}

    def save_current_data(self, data):
        """현재 데이터를 저장합니다."""
        try:
            current_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            with open('rootdata_hot_index_history.json', 'w', encoding='utf-8') as f:
                json.dump(current_data, f, ensure_ascii=False, indent=2)
            logger.info(f"현재 데이터 저장 완료: {len(data)}개 프로젝트")
        except Exception as e:
            logger.error(f"데이터 저장 실패: {e}")

    def fetch_hot_index_data(self):
        """Rootdata에서 hot index 데이터를 가져옵니다."""
        try:
            logger.info("Rootdata hot index 데이터를 가져오는 중...")
            
            # Rootdata 웹사이트 URL
            url = "https://cn.rootdata.com/Projects"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # JavaScript에서 hot index 데이터 추출 시도
            script_tags = soup.find_all('script')
            hot_index_data = []
            
            for script in script_tags:
                if script.string and 'hotIndex' in script.string:
                    # JavaScript 코드에서 hot index 값 추출
                    script_content = script.string
                    # 간단한 정규식으로 hot index 값 찾기
                    hot_index_matches = re.findall(r'"hotIndex":\s*(\d+(?:\.\d+)?)', script_content)
                    if hot_index_matches:
                        logger.info(f"JavaScript에서 {len(hot_index_matches)}개의 hot index 값을 찾았습니다.")
                        # 여기서 더 정교한 파싱이 필요할 수 있습니다
            
            # HTML 테이블에서 데이터 추출
            logger.info("HTML 테이블과 JavaScript 데이터를 조합하여 hot index 정보를 찾는 중...")
            
            # 테이블에서 프로젝트 정보 추출
            table_data = []
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        try:
                            # 순위
                            rank_text = cells[0].get_text(strip=True)
                            rank = int(rank_text) if rank_text.isdigit() else 0
                            
                            # 프로젝트명
                            project_name = cells[2].get_text(strip=True)
                            if not project_name:
                                continue
                            
                            # 프로젝트명 정리 (긴 설명 제거)
                            project_name = self.clean_project_name(project_name)
                            
                            # 프로젝트 상세 페이지 링크 추출
                            project_link = ""
                            link_element = cells[2].find('a', href=True)
                            if link_element:
                                href = link_element.get('href')
                                if href.startswith('/Projects/detail/'):
                                    # 상대 경로를 절대 경로로 변환
                                    project_link = f"https://www.rootdata.com{href}"
                            
                            # Hot Index 값 추출 (JavaScript 데이터와 조합)
                            hot_index = 0
                            raw_text = ""
                            
                            # 셀 내용에서 hot index 관련 텍스트 찾기
                            cell_text = cells[2].get_text(strip=True)
                            hot_index_match = re.search(r'Hot Index:\s*(\d+(?:\.\d+)?)', cell_text)
                            if hot_index_match:
                                hot_index = float(hot_index_match.group(1))
                                raw_text = hot_index_match.group(0)
                            
                            if hot_index > 0 and project_name:
                                table_data.append({
                                    'rank': rank,
                                    'project_name': project_name,
                                    'project_link': project_link,
                                    'hot_index': hot_index,
                                    'raw_text': raw_text
                                })
                        except Exception as e:
                            logger.warning(f"행 파싱 실패: {e}")
                            continue
            
            # JavaScript 데이터와 테이블 데이터 조합
            if hot_index_data:
                # JavaScript 데이터를 우선으로 사용하고, 테이블 데이터와 병합
                combined_data = []
                for i, hot_index in enumerate(hot_index_data):
                    if i < len(table_data):
                        item = table_data[i].copy()
                        item['hot_index'] = float(hot_index)
                        combined_data.append(item)
                    else:
                        combined_data.append({
                            'rank': i + 1,
                            'project_name': f"Project {i + 1}",
                            'project_link': "",
                            'hot_index': float(hot_index),
                            'raw_text': f"Hot Index: {hot_index}"
                        })
                
                logger.info(f"테이블과 JavaScript 데이터를 조합하여 총 {len(combined_data)}개의 hot index 데이터를 파싱했습니다.")
                return combined_data
            else:
                # 테이블 데이터만 사용
                logger.info(f"테이블에서 {len(table_data)}개의 hot index 데이터를 파싱했습니다.")
                return table_data
                
        except Exception as e:
            logger.error(f"데이터 가져오기 실패: {e}")
            return []

    def calculate_changes(self, current_data):
        """이전 데이터와 비교하여 변화량을 계산합니다."""
        if not self.previous_data or not self.previous_data.get('data'):
            return current_data
        
        prev_data_dict = {item['project_name']: item for item in self.previous_data['data']}
        
        for item in current_data:
            project_name = item['project_name']
            if project_name in prev_data_dict:
                prev_hot_index = prev_data_dict[project_name]['hot_index']
                current_hot_index = item['hot_index']
                change = current_hot_index - prev_hot_index
                
                if change > 0:
                    item['change_type'] = 'increase'
                    item['change_value'] = abs(change)
                elif change < 0:
                    item['change_type'] = 'decrease'
                    item['change_value'] = abs(change)
                else:
                    item['change_type'] = 'no_change'
                    item['change_value'] = 0
            else:
                item['change_type'] = 'new'
                item['change_value'] = 0
        
        return current_data

    def format_telegram_message(self, data):
        """텔레그램 메시지를 포맷합니다."""
        if not data:
            return "❌ Hot index 데이터를 가져올 수 없습니다."
        
        # TOP 10만 선택
        top_data = sorted(data, key=lambda x: x.get('hot_index', 0), reverse=True)[:10]
        
        message = "🔥 Rootdata Hot Index TOP 10\n"
        message += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        message += "⏰ 매시간 정각 업데이트\n\n"
        
        for i, item in enumerate(top_data, 1):
            project_name = item['project_name']
            hot_index = item.get('hot_index', 0)
            project_link = item.get('project_link', '')
            change_type = item.get('change_type', 'no_change')
            change_value = item.get('change_value', 0)
            
            # 변화량 표시
            if change_type == 'increase':
                change_symbol = "📈"
                change_text = f"+{change_value:.1f}"
            elif change_type == 'decrease':
                change_symbol = "📉"
                change_text = f"-{change_value:.1f}"
            elif change_type == 'new':
                change_symbol = "🆕"
                change_text = "신규"
            else:
                change_symbol = "➖"
                change_text = "변화없음"
            
            # 프로젝트 링크가 있으면 하이퍼링크로 표시
            if project_link:
                project_display = f"<a href='{project_link}'>{project_name}</a>"
            else:
                project_display = project_name
            
            message += f"🏅 #{i}. {project_display}\n"
            message += f"    🔥 Hot Index: {hot_index:.1f} {change_symbol} {change_text}\n\n"
        
        return message

    def send_telegram_message(self, message):
        """텔레그램으로 메시지를 전송합니다."""
        if not self.telegram_bot_token:
            logger.error("텔레그램 봇 토큰이 설정되지 않았습니다.")
            return False
        
        success_count = 0
        total_channels = len(self.chat_ids)
        
        logger.info(f"총 {total_channels}개 채널에 메시지 전송")
        logger.info(f"채널 목록: {' + '.join(['메인', '추가채널'] if total_channels > 1 else ['메인'])}")
        
        for chat_id in self.chat_ids:
            try:
                url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
                data = {
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': 'HTML',
                    'disable_web_page_preview': True
                }
                
                response = requests.post(url, data=data, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                if result.get('ok'):
                    logger.info(f"텔레그램 메시지 전송 성공 (Chat ID: {chat_id})")
                    success_count += 1
                else:
                    logger.error(f"텔레그램 API 오류: {result.get('description', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"텔레그램 전송 실패 (Chat ID: {chat_id}): {e}")
        
        if success_count == total_channels:
            logger.info(f"모든 채널({total_channels}개)에 메시지 전송 완료")
            return True
        else:
            logger.warning(f"일부 채널 전송 실패: {success_count}/{total_channels}")
            return False

    def monitor_once(self):
        """한 번만 모니터링을 실행합니다."""
        logger.info("Hot index 모니터링 시작...")
        
        # 데이터 가져오기
        current_data = self.fetch_hot_index_data()
        
        if not current_data:
            logger.error("Hot index 데이터를 가져올 수 없습니다.")
            return
        
        # 변화량 계산
        current_data = self.calculate_changes(current_data)
        
        # TOP 5 로깅
        top_5 = sorted(current_data, key=lambda x: x.get('hot_index', 0), reverse=True)[:5]
        logger.info("상위 5개 프로젝트:")
        for i, item in enumerate(top_5):
            logger.info(f"  {i+1}. {item['project_name']} - Hot Index: {item['hot_index']}")
        
        logger.info(f"총 {len(current_data)}개의 hot index 데이터를 가져왔습니다.")
        
        # 텔레그램 메시지 전송
        message = self.format_telegram_message(current_data)
        if self.send_telegram_message(message):
            # 성공적으로 전송된 경우에만 데이터 저장
            self.save_current_data(current_data)
            logger.info("Hot index TOP 10 모니터링 완료")
        else:
            logger.error("텔레그램 전송 실패로 데이터 저장을 건너뜁니다.")

    def start_monitoring(self):
        """지속적인 모니터링을 시작합니다."""
        logger.info("Rootdata Hot Index 모니터가 초기화되었습니다.")
        
        # 매시간 정각에 실행
        schedule.every().hour.at(":00").do(self.monitor_once)
        
        # 즉시 한 번 실행
        self.monitor_once()
        
        logger.info("스케줄러 시작. 매시간 정각에 실행됩니다.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
        except KeyboardInterrupt:
            logger.info("모니터링이 중단되었습니다.")
        except Exception as e:
            logger.error(f"모니터링 중 오류 발생: {e}")

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Rootdata Hot Index 모니터')
    parser.add_argument('--once', action='store_true', help='한 번만 실행')
    
    args = parser.parse_args()
    
    try:
        monitor = RootdataHotIndexMonitor()
        
        if args.once:
            monitor.monitor_once()
        else:
            monitor.start_monitoring()
            
    except Exception as e:
        logger.error(f"모니터 초기화 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 