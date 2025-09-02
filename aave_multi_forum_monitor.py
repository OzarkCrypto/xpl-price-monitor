#!/usr/bin/env python3
"""
Aave 다중 거버넌스 포럼 모니터링 봇
여러 포럼의 새로운 댓글이나 활동을 감지하여 텔레그램으로 알림을 보냅니다.
"""

import requests
import json
import time
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import logging
import sqlite3
import os
from typing import List, Dict, Any

# 설정
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8253278813:AAH5I5cMlu6N7srGDNl8LkPnW2PUJRPPTTI")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1339285013")
CHECK_INTERVAL = 3600  # 1시간마다 체크
DB_FILE = "aave_multi_monitor.db"

# 모니터링할 포럼 목록
FORUMS = [
    {
        'name': 'USDe November expiry PT tokens',
        'url': 'https://governance.aave.com/t/direct-to-aip-onboard-usde-november-expiry-pt-tokens-on-aave-v3-core-instance/23013',
        'description': 'USDe November expiry PT tokens on Aave V3 Core Instance'
    },
    {
        'name': 'sUSDe November expiry PT tokens',
        'url': 'https://governance.aave.com/t/direct-to-aip-onboard-susde-november-expiry-pt-tokens-on-aave-v3-core-instance/22894',
        'description': 'sUSDe November expiry PT tokens on Aave V3 Core Instance'
    },
    {
        'name': 'tUSDe December expiry PT tokens',
        'url': 'https://governance.aave.com/t/temp-check-onboard-tusde-december-expiry-pt-tokens-on-aave-v3-core-instance/22850',
        'description': 'tUSDe December expiry PT tokens on Aave V3 Core Instance'
    }
]

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aave_multi_monitor.log'),
        logging.StreamHandler()
    ]
)

class AaveMultiForumMonitor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.init_database()
        
    def init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # 포럼 테이블 생성
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS forums (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    forum_name TEXT UNIQUE,
                    forum_url TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 댓글 테이블 생성
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    forum_name TEXT,
                    comment_id TEXT,
                    author TEXT,
                    content TEXT,
                    timestamp TEXT,
                    url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(forum_name, comment_id)
                )
            ''')
            
            # 활동 테이블 생성
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    forum_name TEXT,
                    activity_type TEXT,
                    description TEXT,
                    timestamp TEXT,
                    url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 포럼 정보 삽입
            for forum in FORUMS:
                cursor.execute('''
                    INSERT OR IGNORE INTO forums (forum_name, forum_url, description)
                    VALUES (?, ?, ?)
                ''', (forum['name'], forum['url'], forum['description']))
            
            conn.commit()
            conn.close()
            logging.info("데이터베이스 초기화 완료")
            
        except Exception as e:
            logging.error(f"데이터베이스 초기화 오류: {e}")
    
    def fetch_page(self, url: str) -> str:
        """웹페이지 가져오기"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logging.error(f"페이지 가져오기 오류: {e}")
            return None
    
    def parse_comments(self, html_content: str, forum_name: str) -> List[Dict[str, Any]]:
        """댓글 파싱"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            comments = []
            
            # 댓글 요소들 찾기 (Discourse 포럼 구조에 맞게 조정)
            comment_elements = soup.find_all('div', class_='topic-body')
            
            for element in comment_elements:
                try:
                    # 댓글 ID 추출
                    comment_id = element.get('id', '')
                    if comment_id.startswith('post_'):
                        comment_id = comment_id.replace('post_', '')
                    
                    # 작성자 추출
                    author_element = element.find('span', class_='creator')
                    if author_element:
                        author_link = author_element.find('a')
                        author = author_link.get_text(strip=True) if author_link else "Unknown"
                    else:
                        author = "Unknown"
                    
                    # 내용 추출
                    content_element = element.find('div', class_='post')
                    content = content_element.get_text(strip=True) if content_element else ""
                    
                    # 시간 추출
                    time_element = element.find('time')
                    timestamp = time_element.get('datetime', '') if time_element else ""
                    
                    if comment_id and content:
                        comments.append({
                            'forum_name': forum_name,
                            'id': comment_id,
                            'author': author,
                            'content': content[:200] + "..." if len(content) > 200 else content,
                            'timestamp': timestamp,
                            'url': f"{element.get('data-url', '')}#post_{comment_id}"
                        })
                        
                except Exception as e:
                    logging.warning(f"댓글 파싱 오류: {e}")
                    continue
            
            return comments
            
        except Exception as e:
            logging.error(f"댓글 파싱 오류: {e}")
            return []
    
    def parse_activities(self, html_content: str, forum_name: str) -> List[Dict[str, Any]]:
        """활동 내역 파싱"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            activities = []
            
            # 활동 내역 요소들 찾기
            activity_elements = soup.find_all('div', class_='activity')
            
            for element in activity_elements:
                try:
                    activity_type = element.get('class', [''])[0] if element.get('class') else ""
                    description = element.get_text(strip=True)
                    timestamp = datetime.now().isoformat()
                    
                    if description:
                        activities.append({
                            'forum_name': forum_name,
                            'type': activity_type,
                            'description': description[:200] + "..." if len(description) > 200 else description,
                            'timestamp': timestamp,
                            'url': element.get('data-url', '')
                        })
                        
                except Exception as e:
                    logging.warning(f"활동 파싱 오류: {e}")
                    continue
            
            return activities
            
        except Exception as e:
            logging.error(f"활동 파싱 오류: {e}")
            return []
    
    def check_new_comments(self, current_comments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """새로운 댓글 확인"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            new_comments = []
            
            for comment in current_comments:
                # 기존 댓글인지 확인
                cursor.execute('''
                    SELECT id FROM comments 
                    WHERE forum_name = ? AND comment_id = ?
                ''', (comment['forum_name'], comment['id']))
                
                if not cursor.fetchone():
                    # 새 댓글 저장
                    cursor.execute('''
                        INSERT INTO comments (forum_name, comment_id, author, content, timestamp, url)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (comment['forum_name'], comment['id'], comment['author'], comment['content'], comment['timestamp'], comment['url']))
                    
                    new_comments.append(comment)
            
            conn.commit()
            conn.close()
            
            return new_comments
            
        except Exception as e:
            logging.error(f"새 댓글 확인 오류: {e}")
            return []
    
    def check_new_activities(self, current_activities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """새로운 활동 확인"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            new_activities = []
            
            for activity in current_activities:
                # 기존 활동인지 확인 (내용과 시간으로 비교)
                cursor.execute('''
                    SELECT id FROM activities 
                    WHERE forum_name = ? AND description = ? AND timestamp = ?
                ''', (activity['forum_name'], activity['description'], activity['timestamp']))
                
                if not cursor.fetchone():
                    # 새 활동 저장
                    cursor.execute('''
                        INSERT INTO activities (forum_name, activity_type, description, timestamp, url)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (activity['forum_name'], activity['type'], activity['description'], activity['timestamp'], activity['url']))
                    
                    new_activities.append(activity)
            
            conn.commit()
            conn.close()
            
            return new_activities
            
        except Exception as e:
            logging.error(f"새 활동 확인 오류: {e}")
            return []
    
    def send_telegram_message(self, message: str) -> bool:
        """텔레그램 메시지 전송"""
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            data = {
                'chat_id': CHAT_ID,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                logging.info("텔레그램 메시지 전송 성공")
                return True
            else:
                logging.error(f"텔레그램 메시지 전송 실패: {result}")
                return False
                
        except Exception as e:
            logging.error(f"텔레그램 메시지 전송 오류: {e}")
            return False
    
    def format_comment_message(self, comment: Dict[str, Any]) -> str:
        """댓글 메시지 포맷팅"""
        return f"""🔔 <b>새로운 댓글 발견!</b>

📋 <b>포럼:</b> {comment['forum_name']}
👤 <b>작성자:</b> {comment['author']}
💬 <b>내용:</b> {comment['content']}
⏰ <b>시간:</b> {comment['timestamp']}
🔗 <b>링크:</b> <a href="{comment['url']}">댓글 보기</a>

#Aave #Governance #PT #Token"""
    
    def format_activity_message(self, activity: Dict[str, Any]) -> str:
        """활동 메시지 포맷팅"""
        return f"""📢 <b>새로운 활동 발견!</b>

📋 <b>포럼:</b> {activity['forum_name']}
📝 <b>유형:</b> {activity['type']}
📄 <b>설명:</b> {activity['description']}
⏰ <b>시간:</b> {activity['timestamp']}
🔗 <b>링크:</b> <a href="{activity['url']}">포럼 보기</a>

#Aave #Governance #Activity"""
    
    def monitor_forum(self, forum: Dict[str, Any]) -> Dict[str, Any]:
        """개별 포럼 모니터링"""
        try:
            logging.info(f"포럼 모니터링 중: {forum['name']}")
            
            # 페이지 가져오기
            html_content = self.fetch_page(forum['url'])
            if not html_content:
                return {'comments': 0, 'activities': 0, 'new_comments': 0, 'new_activities': 0}
            
            # 댓글 파싱
            current_comments = self.parse_comments(html_content, forum['name'])
            logging.info(f"  현재 댓글 수: {len(current_comments)}")
            
            # 활동 파싱
            current_activities = self.parse_activities(html_content, forum['name'])
            logging.info(f"  현재 활동 수: {len(current_activities)}")
            
            # 새로운 댓글 확인
            new_comments = self.check_new_comments(current_comments)
            if new_comments:
                logging.info(f"  새로운 댓글 {len(new_comments)}개 발견")
                for comment in new_comments:
                    message = self.format_comment_message(comment)
                    self.send_telegram_message(message)
                    time.sleep(2)  # 메시지 간격
            
            # 새로운 활동 확인
            new_activities = self.check_new_activities(current_activities)
            if new_activities:
                logging.info(f"  새로운 활동 {len(new_activities)}개 발견")
                for activity in new_activities:
                    message = self.format_activity_message(activity)
                    self.send_telegram_message(message)
                    time.sleep(2)  # 메시지 간격
            
            return {
                'comments': len(current_comments),
                'activities': len(current_activities),
                'new_comments': len(new_comments),
                'new_activities': len(new_activities)
            }
            
        except Exception as e:
            logging.error(f"포럼 모니터링 오류 ({forum['name']}): {e}")
            return {'comments': 0, 'activities': 0, 'new_comments': 0, 'new_activities': 0}
    
    def monitor(self):
        """모니터링 시작"""
        logging.info(f"Aave 다중 포럼 모니터링 시작: {len(FORUMS)}개 포럼")
        
        # 시작 알림
        start_message = f"""🚀 <b>Aave 다중 포럼 모니터링 시작</b>

📋 <b>모니터링 대상:</b> {len(FORUMS)}개 포럼
⏰ <b>시작 시간:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

<b>포럼 목록:</b>"""
        
        for forum in FORUMS:
            start_message += f"\n• {forum['name']}"
        
        start_message += "\n\n#Aave #Governance #MultiMonitor #Start"
        
        self.send_telegram_message(start_message)
        
        # GitHub Actions에서는 한 번만 실행
        try:
            logging.info("=" * 50)
            logging.info("모니터링 사이클 시작")
            
            total_stats = {
                'total_comments': 0,
                'total_activities': 0,
                'total_new_comments': 0,
                'total_new_activities': 0
            }
            
            # 각 포럼 모니터링
            for forum in FORUMS:
                stats = self.monitor_forum(forum)
                
                total_stats['total_comments'] += stats['comments']
                total_stats['total_activities'] += stats['activities']
                total_stats['total_new_comments'] += stats['new_comments']
                total_stats['total_new_activities'] += stats['new_activities']
                
                time.sleep(5)  # 포럼 간 간격
            
            logging.info(f"전체 통계: 댓글 {total_stats['total_comments']}개, 활동 {total_stats['total_activities']}개")
            logging.info(f"새로운 항목: 댓글 {total_stats['total_new_comments']}개, 활동 {total_stats['total_new_activities']}개")
            
            # 완료 알림
            completion_message = f"""✅ <b>Aave 모니터링 완료</b>

📊 <b>모니터링 결과:</b>
• 총 댓글: {total_stats['total_comments']}개
• 총 활동: {total_stats['total_activities']}개
• 새로운 댓글: {total_stats['total_new_comments']}개
• 새로운 활동: {total_stats['total_new_activities']}개

⏰ <b>완료 시간:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#Aave #Governance #Monitor #Complete"""
            
            self.send_telegram_message(completion_message)
            
        except Exception as e:
            logging.error(f"모니터링 오류: {e}")
            error_message = f"""❌ <b>Aave 모니터링 오류</b>

🚨 <b>오류 내용:</b> {str(e)}
⏰ <b>발생 시간:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#Aave #Governance #Monitor #Error"""
            
            self.send_telegram_message(error_message)

def main():
    """메인 함수"""
    print("🚀 Aave 다중 포럼 모니터링 봇")
    print("=" * 50)
    print(f"📋 모니터링 대상: {len(FORUMS)}개 포럼")
    print(f"🤖 텔레그램 봇: {TELEGRAM_TOKEN}")
    print(f"💬 채팅 ID: {CHAT_ID}")
    print(f"⏰ 체크 간격: {CHECK_INTERVAL}초")
    print("\n📋 모니터링 포럼 목록:")
    
    for i, forum in enumerate(FORUMS, 1):
        print(f"  {i}. {forum['name']}")
        print(f"     {forum['description']}")
        print(f"     {forum['url']}")
        print()
    
    print("=" * 50)
    
    try:
        monitor = AaveMultiForumMonitor()
        monitor.monitor()
    except KeyboardInterrupt:
        print("\n👋 모니터링이 중단되었습니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
