#!/usr/bin/env python3
"""
Rootdata Hot Score 모니터링 봇
매시간 정각에 hot score TOP 10을 텔레그램으로 전송
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
import json
import re

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rootdata_hot_score.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProjectNameCleaner:
    """프로젝트 이름을 정리하는 클래스"""
    
    def __init__(self):
        # 프로젝트 이름 매핑
        self.name_mapping = {
            'Game developer platformOVERTAKE': 'OVERTAKE',
            'A Web3 Privacy Acceleration so...': 'Privacy Protocol',
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

    def clean_name(self, project_name):
        """프로젝트 이름을 읽기 쉽게 정리합니다."""
        if not project_name:
            return "Unknown Project"
        
        # 1. 매핑된 이름이 있으면 사용
        if project_name in self.name_mapping:
            return self.name_mapping[project_name]
        
        # 2. 중국어 설명 제거 (한국어/영어만 남김)
        # 중국어 패턴: [\u4e00-\u9fff]+
        project_name = re.sub(r'[\u4e00-\u9fff]+.*$', '', project_name)
        
        # 3. 일반적인 패턴 정리
        # "PlatformName" 형태를 "Name"으로 변환
        if re.search(r'platform[A-Z]', project_name):
            clean_name = re.sub(r'platform([A-Z][a-zA-Z]+)', r'\1', project_name)
            if clean_name:
                project_name = clean_name
        
        # "TypeName" 형태를 "Name"으로 변환
        elif re.search(r'[A-Z][a-z]+[A-Z][a-zA-Z]+', project_name):
            clean_name = re.sub(r'^[A-Z][a-z]+', '', project_name)
            if clean_name:
                project_name = clean_name
        
        # 4. 특수 구분자로 분리
        separators = ['.', ' is ', ' is a ', ' - ', ' | ', ' / ', ' 是一个', ' 旨在', ' 提供']
        for sep in separators:
            if sep in project_name:
                parts = project_name.split(sep)
                if parts[0].strip():
                    project_name = parts[0].strip()
                    break
        
        # 5. 길이 제한 및 정리
        if len(project_name) > 30:
            words = project_name.split()
            if len(words) > 1:
                if len(words[-1]) < 3:
                    words = words[:-1]
                project_name = ' '.join(words)
            
            if len(project_name) > 30:
                project_name = project_name[:27] + "..."
        
        # 6. 불필요한 공백 제거
        project_name = re.sub(r'\s+', ' ', project_name).strip()
        
        # 7. 빈 문자열이면 원본 이름에서 첫 번째 단어만 사용
        if not project_name or len(project_name) < 2:
            original_words = re.sub(r'[\u4e00-\u9fff]+', '', project_name).split()
            if original_words:
                project_name = original_words[0]
        
        return project_name if project_name else "Unknown Project"

class RootdataHotScoreMonitor:
    def __init__(self):
        """Rootdata Hot Score 모니터 초기화"""
        # 현재 디렉토리의 .env 파일 로드
        current_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(current_dir, '.env')
        load_dotenv(env_path)
        
        logger.info(f"환경 변수 파일 경로: {env_path}")
        logger.info(f"환경 변수 파일 존재: {os.path.exists(env_path)}")
        
        # 환경 변수 디버깅
        logger.info("환경 변수 로딩 중...")
        logger.info(f"ROOTDATA_BOT_TOKEN: {os.getenv('ROOTDATA_BOT_TOKEN')}")
        logger.info(f"ROOTDATA_CHAT_ID: {os.getenv('ROOTDATA_CHAT_ID')}")
        logger.info(f"TELEGRAM_BOT_TOKEN: {os.getenv('TELEGRAM_BOT_TOKEN')}")
        logger.info(f"TELEGRAM_CHAT_ID: {os.getenv('TELEGRAM_CHAT_ID')}")
        
        # 텔레그램 설정 (Rootdata 전용 설정 우선, 없으면 일반 설정 사용)
        self.telegram_bot_token = os.getenv('ROOTDATA_BOT_TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('ROOTDATA_CHAT_ID') or os.getenv('TELEGRAM_CHAT_ID')
        
        # 추가 채널 ID (선택사항)
        self.extra_chat_id = os.getenv('ROOTDATA_EXTRA_CHAT_ID')
        
        logger.info(f"선택된 BOT_TOKEN: {self.telegram_bot_token}")
        logger.info(f"선택된 CHAT_ID: {self.telegram_chat_id}")
        
        if not self.telegram_bot_token or not self.telegram_chat_id:
            raise ValueError("ROOTDATA_BOT_TOKEN/ROOTDATA_CHAT_ID 또는 TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID 환경 변수가 필요합니다.")
        
        # 전송할 채널 목록 생성
        self.chat_ids = [self.telegram_chat_id]
        if self.extra_chat_id:
            self.chat_ids.append(self.extra_chat_id)
        
        # 이전 데이터 로드
        self.previous_data = self.load_previous_data()
        
        # 프로젝트 이름 정리 함수
        self.name_cleaner = ProjectNameCleaner()

    def create_project_url(self, original_name):
        """프로젝트명을 기반으로 Rootdata 영문 사이트 URL을 생성합니다."""
        try:
            if not original_name:
                return None
            
            # 중국어 설명 제거
            clean_name = re.sub(r'[\u4e00-\u9fff]+.*$', '', original_name)
            
            # 특수 문자 제거 및 공백을 하이픈으로 변환
            clean_name = re.sub(r'[^\w\s-]', '', clean_name)
            clean_name = re.sub(r'\s+', '-', clean_name).strip('-')
            
            # 소문자로 변환
            clean_name = clean_name.lower()
            
            # 빈 문자열이면 None 반환
            if not clean_name:
                return None
            
            # Rootdata 영문 사이트 URL 생성
            # 일반적으로 /Projects/[프로젝트명] 형태
            return f"https://rootdata.com/Projects/{clean_name}"
            
        except Exception as e:
            logger.warning(f"프로젝트 URL 생성 실패: {e}")
            return None

    def load_previous_data(self):
        """이전 데이터를 로드합니다."""
        try:
            if os.path.exists('rootdata_hot_score_history.json'):
                with open('rootdata_hot_score_history.json', 'r', encoding='utf-8') as f:
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
            with open('rootdata_hot_score_history.json', 'w', encoding='utf-8') as f:
                json.dump(current_data, f, ensure_ascii=False, indent=2)
            logger.info(f"현재 데이터 저장 완료: {len(data)}개 프로젝트")
        except Exception as e:
            logger.error(f"데이터 저장 실패: {e}")

    def fetch_hot_score_data(self):
        """Rootdata에서 hot score 데이터를 가져옵니다."""
        try:
            logger.info("Rootdata hot score 데이터를 가져오는 중...")
            
            # Rootdata 웹사이트 URL
            url = "https://cn.rootdata.com/Projects"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # JavaScript에서 hot score 데이터 추출
            hot_score_data = self.extract_hot_score_from_js(soup)
            
            if not hot_score_data:
                logger.warning("JavaScript에서 hot score 데이터를 찾을 수 없습니다. HTML 테이블에서 추출을 시도합니다.")
                hot_score_data = self.extract_hot_score_from_table(soup)
            
            if hot_score_data:
                # hot score로 정렬
                hot_score_data.sort(key=lambda x: x.get('hot_score', 0), reverse=True)
                # TOP 10만 선택
                hot_score_data = hot_score_data[:10]
                
                logger.info(f"Hot score 데이터 추출 완료: {len(hot_score_data)}개 프로젝트")
                return hot_score_data
            else:
                logger.error("Hot score 데이터를 추출할 수 없습니다.")
                return []
                
        except Exception as e:
            logger.error(f"Hot score 데이터 가져오기 실패: {e}")
            return []

    def extract_hot_score_from_js(self, soup):
        """JavaScript에서 hot score 데이터를 추출합니다."""
        try:
            script_tags = soup.find_all('script')
            
            for script in script_tags:
                if script.string and 'hotIndex' in script.string:
                    script_content = script.string
                    
                    # hotIndex와 프로젝트 정보를 함께 추출
                    # 패턴: "hotIndex": 숫자, "name": "프로젝트명"
                    pattern = r'"hotIndex":\s*(\d+(?:\.\d+)?).*?"name":\s*"([^"]+)"'
                    matches = re.findall(pattern, script_content, re.DOTALL)
                    
                    if matches:
                        hot_score_data = []
                        for hot_score, name in matches:
                            clean_name = self.name_cleaner.clean_name(name)
                            hot_score_data.append({
                                'name': clean_name,
                                'hot_score': float(hot_score),
                                'original_name': name
                            })
                        
                        logger.info(f"JavaScript에서 {len(hot_score_data)}개의 hot score 데이터를 추출했습니다.")
                        return hot_score_data
            
            return []
            
        except Exception as e:
            logger.error(f"JavaScript 데이터 추출 실패: {e}")
            return []

    def extract_hot_score_from_table(self, soup):
        """HTML 테이블에서 hot score 데이터를 추출합니다."""
        try:
            # 테이블에서 데이터 추출
            tables = soup.find_all('table')
            hot_score_data = []
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        # 프로젝트명과 hot score 컬럼 찾기
                        project_name = None
                        hot_score = None
                        
                        for i, cell in enumerate(cells):
                            cell_text = cell.get_text(strip=True)
                            
                            # 프로젝트명 컬럼 (보통 첫 번째 컬럼)
                            if i == 0 and cell_text and not cell_text.isdigit():
                                project_name = cell_text
                            
                            # hot score 컬럼 (숫자로 된 컬럼)
                            elif cell_text.replace('.', '').isdigit():
                                try:
                                    hot_score = float(cell_text)
                                except ValueError:
                                    continue
                        
                        if project_name and hot_score is not None:
                            clean_name = self.name_cleaner.clean_name(project_name)
                            hot_score_data.append({
                                'name': clean_name,
                                'hot_score': hot_score,
                                'original_name': project_name
                            })
            
            logger.info(f"HTML 테이블에서 {len(hot_score_data)}개의 hot score 데이터를 추출했습니다.")
            return hot_score_data
            
        except Exception as e:
            logger.error(f"HTML 테이블 데이터 추출 실패: {e}")
            return []

    def format_telegram_message(self, hot_score_data):
        """텔레그램 메시지를 포맷합니다."""
        if not hot_score_data:
            return "❌ Hot score 데이터를 가져올 수 없습니다."
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"🔥 <b>Rootdata Hot Score TOP 10</b> 🔥\n"
        message += f"📅 {timestamp}\n\n"
        
        for i, project in enumerate(hot_score_data, 1):
            name = project['name']
            hot_score = project['hot_score']
            original_name = project['original_name']
            
            # 프로젝트명을 URL 친화적으로 변환
            project_url = self.create_project_url(original_name)
            
            # 순위별 이모지
            if i == 1:
                rank_emoji = "🥇"
            elif i == 2:
                rank_emoji = "🥈"
            elif i == 3:
                rank_emoji = "🥉"
            else:
                rank_emoji = f"{i}️⃣"
            
            # 프로젝트명에 링크 추가
            if project_url:
                message += f"{rank_emoji} <b><a href='{project_url}'>{name}</a></b>\n"
            else:
                message += f"{rank_emoji} <b>{name}</b>\n"
            message += f"   🔥 Hot Score: {hot_score:,.1f}\n\n"
        
        message += "📊 <i>Rootdata에서 제공하는 프로젝트 인기도 지수입니다.</i>\n\n"
        message += "🔗 <a href='https://rootdata.com/Projects'>Rootdata Projects 바로가기</a>"
        
        return message

    def send_telegram_message(self, message):
        """텔레그램으로 메시지를 보냅니다."""
        success_count = 0
        total_count = len(self.chat_ids)
        
        for chat_id in self.chat_ids:
            try:
                url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": False
                }
                
                response = requests.post(url, json=payload, timeout=30)
                
                if response.status_code == 200:
                    logger.info(f"텔레그램 메시지 전송 성공 (chat_id: {chat_id})")
                    success_count += 1
                else:
                    logger.error(f"텔레그램 전송 실패 (chat_id: {chat_id}): {response.status_code} - {response.text}")
                    
            except Exception as e:
                logger.error(f"텔레그램 전송 오류 (chat_id: {chat_id}): {e}")
        
        if success_count > 0:
            logger.info(f"텔레그램 전송 완료: {success_count}/{total_count} 성공")
            return True
        else:
            logger.error("모든 채널에 텔레그램 전송 실패")
            return False

    def check_and_send_hot_score(self):
        """Hot score를 확인하고 텔레그램으로 전송합니다."""
        try:
            logger.info("Hot score 확인 및 전송 시작")
            
            # 현재 hot score 데이터 가져오기
            current_data = self.fetch_hot_score_data()
            
            if not current_data:
                logger.error("Hot score 데이터를 가져올 수 없습니다.")
                return
            
            # 이전 데이터와 비교하여 변경사항 확인
            has_changes = self.check_data_changes(current_data)
            
            if has_changes:
                # 텔레그램 메시지 포맷
                message = self.format_telegram_message(current_data)
                
                # 텔레그램으로 전송
                if self.send_telegram_message(message):
                    logger.info("Hot score 알림 전송 완료")
                    
                    # 현재 데이터 저장
                    self.save_current_data(current_data)
                    self.previous_data = {'data': current_data, 'timestamp': datetime.now().isoformat()}
                else:
                    logger.error("Hot score 알림 전송 실패")
            else:
                logger.info("Hot score 데이터에 변경사항이 없습니다.")
                
        except Exception as e:
            logger.error(f"Hot score 확인 및 전송 중 오류 발생: {e}")

    def check_data_changes(self, current_data):
        """데이터 변경사항을 확인합니다."""
        if not self.previous_data.get('data'):
            return True
        
        previous_data = self.previous_data['data']
        
        # TOP 3 프로젝트의 hot score 변경 확인
        for i in range(min(3, len(current_data), len(previous_data))):
            current = current_data[i]
            previous = previous_data[i]
            
            if (current['name'] != previous['name'] or 
                abs(current['hot_score'] - previous['hot_score']) > 0.1):
                return True
        
        return False

    def run_scheduler(self):
        """스케줄러를 실행합니다."""
        logger.info("Hot score 모니터링 스케줄러 시작")
        
        # 매시간 정각에 실행
        schedule.every().hour.at(":00").do(self.check_and_send_hot_score)
        
        # 시작 시 즉시 한 번 실행
        self.check_and_send_hot_score()
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
            except KeyboardInterrupt:
                logger.info("사용자에 의해 중단되었습니다.")
                break
            except Exception as e:
                logger.error(f"스케줄러 실행 중 오류: {e}")
                time.sleep(60)

    def run_once(self):
        """한 번만 실행합니다."""
        logger.info("Hot score 모니터링 한 번 실행")
        self.check_and_send_hot_score()


def main():
    """메인 함수"""
    print("🔥 Rootdata Hot Score 모니터링 봇")
    print("=" * 40)
    
    try:
        # 환경 변수 파일 로드
        current_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(current_dir, '.env')
        load_dotenv(env_path)
        
        print(f"환경 변수 파일 경로: {env_path}")
        print(f"환경 변수 파일 존재: {os.path.exists(env_path)}")
        
        # 환경 변수 확인
        rootdata_bot_token = os.getenv("ROOTDATA_BOT_TOKEN")
        rootdata_chat_id = os.getenv("ROOTDATA_CHAT_ID")
        telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        print(f"ROOTDATA_BOT_TOKEN: {rootdata_bot_token}")
        print(f"ROOTDATA_CHAT_ID: {rootdata_chat_id}")
        print(f"TELEGRAM_BOT_TOKEN: {telegram_bot_token}")
        print(f"TELEGRAM_CHAT_ID: {telegram_chat_id}")
        
        if not (rootdata_bot_token or telegram_bot_token):
            print("❌ ROOTDATA_BOT_TOKEN 또는 TELEGRAM_BOT_TOKEN 환경 변수가 설정되지 않았습니다.")
            return
        
        if not (rootdata_chat_id or telegram_chat_id):
            print("❌ ROOTDATA_CHAT_ID 또는 TELEGRAM_CHAT_ID 환경 변수가 설정되지 않았습니다.")
            return
        
        # 모니터 생성
        monitor = RootdataHotScoreMonitor()
        
        # 명령행 인수 확인
        if len(sys.argv) > 1 and sys.argv[1] == "--once":
            monitor.run_once()
        else:
            monitor.run_scheduler()
            
    except KeyboardInterrupt:
        print("\n👋 프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        logger.error(f"메인 함수 오류: {e}")


if __name__ == "__main__":
    main() 