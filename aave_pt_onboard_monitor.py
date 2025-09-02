#!/usr/bin/env python3
"""
Aave 거버넌스 포럼 PT/Onboard 모니터링 봇
"Onboard"와 "PT" 단어가 포함된 새로운 글과 댓글을 감지하여 텔레그램으로 알림을 보냅니다.
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
TELEGRAM_TOKEN = "8253278813:AAH5I5cMlu6N7srGDNl8LkPnW2PUJRPPTTI"
CHAT_ID = "1339285013"
CHECK_INTERVAL = 3600  # 1시간마다 체크
DB_FILE = "aave_pt_onboard_monitor.db"

# 모니터링할 포럼 URL
FORUM_URL = "https://governance.aave.com/c/governance/4"
FORUM_BASE_URL = "https://governance.aave.com"

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aave_pt_onboard_monitor.log'),
        logging.StreamHandler()
    ]
)

class AavePTOndboardMonitor:
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
            
            # 토픽 테이블 생성
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic_id TEXT UNIQUE,
                    title TEXT,
                    author TEXT,
                    content TEXT,
                    url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 댓글 테이블 생성
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic_id TEXT,
                    comment_id TEXT,
                    author TEXT,
                    content TEXT,
                    timestamp TEXT,
                    url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(topic_id, comment_id)
                )
            ''')
            
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
    
    def is_pt_onboard_topic(self, title: str, content: str) -> bool:
        """제목에 PT와 Onboard 단어가 모두 포함된 토픽인지 확인"""
        title_lower = title.lower()
        
        # 제목에만 PT와 onboard가 모두 포함되어야 함
        has_pt = 'pt' in title_lower
        has_onboard = 'onboard' in title_lower
        
        return has_pt and has_onboard
    
    def is_within_two_weeks(self, activity_text: str) -> bool:
        """활동 시간이 2주 내인지 확인"""
        try:
            # 현재 시간
            now = datetime.now()
            
            # 활동 시간 텍스트 파싱
            activity_text = activity_text.lower().strip()
            
            if 'today' in activity_text or 'yesterday' in activity_text:
                return True
            
            # "X days ago" 형식 파싱
            if 'days ago' in activity_text:
                days_match = re.search(r'(\d+)\s*days?\s*ago', activity_text)
                if days_match:
                    days = int(days_match.group(1))
                    return days <= 14  # 14일 이내
            
            # "X hours ago" 형식 파싱
            if 'hours ago' in activity_text:
                hours_match = re.search(r'(\d+)\s*hours?\s*ago', activity_text)
                if hours_match:
                    hours = int(hours_match.group(1))
                    return hours <= 336  # 14일 * 24시간 = 336시간 이내
            
            # "X minutes ago" 형식 파싱
            if 'minutes ago' in activity_text:
                minutes_match = re.search(r'(\d+)\s*minutes?\s*ago', activity_text)
                if minutes_match:
                    minutes = int(minutes_match.group(1))
                    return minutes <= 20160  # 14일 * 24시간 * 60분 = 20160분 이내
            
            # 구체적인 날짜 형식 (예: "August 15, 2025")
            date_patterns = [
                r'(\w+)\s+(\d+),\s+(\d{4})',  # "August 15, 2025"
                r'(\d+)\s+(\w+)\s+(\d{4})',   # "15 August 2025"
            ]
            
            for pattern in date_patterns:
                date_match = re.search(pattern, activity_text)
                if date_match:
                    try:
                        if len(date_match.groups()) == 3:
                            if pattern == r'(\w+)\s+(\d+),\s+(\d{4})':
                                month_str, day_str, year_str = date_match.groups()
                                month_map = {
                                    'january': 1, 'february': 2, 'march': 3, 'april': 4,
                                    'may': 5, 'june': 6, 'july': 7, 'august': 8,
                                    'september': 9, 'october': 10, 'november': 11, 'december': 12
                                }
                                month = month_map.get(month_str.lower(), 1)
                                day = int(day_str)
                                year = int(year_str)
                            else:
                                day_str, month_str, year_str = date_match.groups()
                                month_map = {
                                    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
                                    'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
                                    'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                                }
                                day = int(day_str)
                                month = month_map.get(month_str.lower(), 1)
                                year = int(year_str)
                            
                            activity_date = datetime(year, month, day)
                            days_diff = (now - activity_date).days
                            return days_diff <= 14
                    except:
                        continue
            
            # 파싱할 수 없는 경우 기본적으로 포함 (안전장치)
            logging.warning(f"활동 시간을 파싱할 수 없음: {activity_text}")
            return True
            
        except Exception as e:
            logging.error(f"활동 시간 파싱 오류: {e}")
            return True  # 오류 시 기본적으로 포함
    
    def parse_topics(self, html_content: str) -> List[Dict[str, Any]]:
        """토픽 목록 파싱 (최근 2주 내)"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            topics = []
            
            # 토픽 테이블 행들 찾기
            topic_rows = soup.find_all('tr', class_='topic-list-item')
            
            # 2주 전 날짜 계산
            two_weeks_ago = datetime.now() - timedelta(weeks=2)
            
            for row in topic_rows:
                try:
                    # 제목과 링크 추출
                    title_element = row.find('td', class_='main-link')
                    if not title_element:
                        continue
                        
                    title_link = title_element.find('a')
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    href = title_link.get('href', '')
                    # 상대 URL인 경우 절대 URL로 변환
                    if href.startswith('/'):
                        topic_url = FORUM_BASE_URL + href
                    else:
                        topic_url = href
                    topic_id = topic_url.split('/')[-1] if topic_url else ''
                    
                    # 작성자 추출
                    author_element = row.find('td', class_='creator')
                    author = "Unknown"
                    if author_element:
                        author_link = author_element.find('a')
                        if author_link:
                            author = author_link.get_text(strip=True)
                    
                    # 활동 시간 추출 (마지막 활동 시간) - 마지막 셀
                    if len(row.find_all('td')) >= 5:
                        activity_element = row.find_all('td')[4]  # 마지막 셀
                        if activity_element:
                            activity_text = activity_element.get_text(strip=True)
                            # 활동 시간을 파싱하여 2주 내인지 확인
                            if self.is_within_two_weeks(activity_text):
                                # 간단한 내용 추출 (제목 기반)
                                content = title
                                
                                if topic_id and title:
                                    topics.append({
                                        'id': topic_id,
                                        'title': title,
                                        'author': author,
                                        'content': content,
                                        'url': topic_url,
                                        'last_activity': activity_text
                                    })
                        
                except Exception as e:
                    logging.warning(f"토픽 파싱 오류: {e}")
                    continue
            
            return topics
            
        except Exception as e:
            logging.error(f"토픽 파싱 오류: {e}")
            return []
    
    def fetch_topic_content(self, topic_url: str) -> str:
        """토픽 상세 내용 가져오기"""
        try:
            html_content = self.fetch_page(topic_url)
            if not html_content:
                return ""
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 첫 번째 포스트 내용 추출
            first_post = soup.find('div', class_='topic-body')
            if first_post:
                content_element = first_post.find('div', class_='post')
                if content_element:
                    return content_element.get_text(strip=True)
            
            return ""
            
        except Exception as e:
            logging.error(f"토픽 내용 가져오기 오류: {e}")
            return ""
    
    def parse_comments(self, html_content: str, topic_id: str, topic_url: str) -> List[Dict[str, Any]]:
        """댓글 파싱"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            comments = []
            
            # 댓글 요소들 찾기 (첫 번째 포스트 제외)
            comment_elements = soup.find_all('div', class_='topic-body')[1:]
            
            for element in comment_elements:
                try:
                    # 댓글 ID 추출
                    comment_id = element.get('id', '')
                    if comment_id.startswith('post_'):
                        comment_id = comment_id.replace('post_', '')
                    
                    # 작성자 추출
                    author_element = element.find('span', class_='creator')
                    author = "Unknown"
                    if author_element:
                        author_link = author_element.find('a')
                        if author_link:
                            author = author_link.get_text(strip=True)
                    
                    # 내용 추출
                    content_element = element.find('div', class_='post')
                    content = ""
                    if content_element:
                        content = content_element.get_text(strip=True)
                    
                    # 시간 추출
                    time_element = element.find('time')
                    timestamp = time_element.get('datetime', '') if time_element else ""
                    
                    if comment_id and content:
                        # 댓글 URL 생성
                        comment_url = f"{topic_url}#post_{comment_id}"
                        comments.append({
                            'topic_id': topic_id,
                            'id': comment_id,
                            'author': author,
                            'content': content[:300] + "..." if len(content) > 300 else content,
                            'timestamp': timestamp,
                            'url': comment_url
                        })
                        
                except Exception as e:
                    logging.warning(f"댓글 파싱 오류: {e}")
                    continue
            
            return comments
            
        except Exception as e:
            logging.error(f"댓글 파싱 오류: {e}")
            return []
    
    def check_new_topics(self, current_topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """새로운 PT/Onboard 토픽 확인"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            new_topics = []
            
            for topic in current_topics:
                # 기존 토픽인지 확인
                cursor.execute('SELECT id FROM topics WHERE topic_id = ?', (topic['id'],))
                if not cursor.fetchone():
                    # 토픽 내용 가져오기
                    full_content = self.fetch_topic_content(topic['url'])
                    topic['content'] = full_content
                    
                    # PT와 Onboard가 모두 포함된 토픽인지 확인
                    if self.is_pt_onboard_topic(topic['title'], topic['content']):
                        # 새 토픽 저장
                        cursor.execute('''
                            INSERT INTO topics (topic_id, title, author, content, url)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (topic['id'], topic['title'], topic['author'], topic['content'], topic['url']))
                        
                        new_topics.append(topic)
                        logging.info(f"새로운 PT/Onboard 토픽 발견: {topic['title']}")
            
            conn.commit()
            conn.close()
            
            return new_topics
            
        except Exception as e:
            logging.error(f"새 토픽 확인 오류: {e}")
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
                    WHERE topic_id = ? AND comment_id = ?
                ''', (comment['topic_id'], comment['id']))
                
                if not cursor.fetchone():
                    # 새 댓글 저장
                    cursor.execute('''
                        INSERT INTO comments (topic_id, comment_id, author, content, timestamp, url)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (comment['topic_id'], comment['id'], comment['author'], comment['content'], comment['timestamp'], comment['url']))
                    
                    new_comments.append(comment)
            
            conn.commit()
            conn.close()
            
            return new_comments
            
        except Exception as e:
            logging.error(f"새 댓글 확인 오류: {e}")
            return []
    
    def send_telegram_message(self, message: str) -> bool:
        """텔레그램 메시지 전송"""
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            data = {
                'chat_id': CHAT_ID,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': False
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
    
    def format_topic_message(self, topic: Dict[str, Any]) -> str:
        """토픽 메시지 포맷팅"""
        last_activity = topic.get('last_activity', 'Unknown')
        return f"""🚨 <b>새로운 PT/Onboard 토픽 발견!</b>

📋 <b>제목:</b> {topic['title']}
👤 <b>작성자:</b> {topic['author']}
💬 <b>내용:</b> {topic['content'][:200] + "..." if len(topic['content']) > 200 else topic['content']}
⏰ <b>마지막 활동:</b> {last_activity}

🔗 <b>바로가기:</b> <a href="{topic['url']}">👉 토픽 읽기</a>

#Aave #Governance #PT #Onboard #NewTopic"""
    
    def format_comment_message(self, comment: Dict[str, Any]) -> str:
        """댓글 메시지 포맷팅"""
        return f"""💬 <b>새로운 댓글 발견!</b>

📋 <b>토픽 ID:</b> {comment['topic_id']}
👤 <b>작성자:</b> {comment['author']}
💬 <b>내용:</b> {comment['content']}
⏰ <b>시간:</b> {comment['timestamp']}

🔗 <b>바로가기:</b> <a href="{comment['url']}">👉 댓글 읽기</a>

#Aave #Governance #PT #Onboard #NewComment"""
    
    def monitor(self):
        """모니터링 시작"""
        logging.info(f"Aave PT/Onboard 모니터링 시작: {FORUM_URL}")
        
        # 시작 알림
        start_message = f"""🚀 <b>Aave PT/Onboard 모니터링 시작</b>

📋 <b>모니터링 대상:</b> 제목에 "PT"와 "onboard"가 동시에 포함된 토픽
🔗 <b>포럼:</b> <a href="{FORUM_URL}">👉 Aave Governance 바로가기</a>
⏰ <b>탐색 범위:</b> 최근 2주 내 활동
⏰ <b>시작 시간:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#Aave #Governance #PT #Onboard #Monitor #Start"""
        
        self.send_telegram_message(start_message)
        
        try:
            logging.info("=" * 50)
            logging.info("모니터링 사이클 시작")
            
            # 포럼 메인 페이지 가져오기
            html_content = self.fetch_page(FORUM_URL)
            if not html_content:
                logging.error("포럼 페이지를 가져올 수 없습니다.")
                return
            
            # 토픽 목록 파싱
            current_topics = self.parse_topics(html_content)
            logging.info(f"현재 토픽 수: {len(current_topics)}")
            
            # 새로운 PT/Onboard 토픽 확인
            new_topics = self.check_new_topics(current_topics)
            if new_topics:
                logging.info(f"새로운 PT/Onboard 토픽 {len(new_topics)}개 발견")
                for topic in new_topics:
                    message = self.format_topic_message(topic)
                    self.send_telegram_message(message)
                    time.sleep(2)  # 메시지 간격
            
            # PT/Onboard 토픽의 댓글만 확인
            total_new_comments = 0
            pt_onboard_topics = [topic for topic in current_topics if self.is_pt_onboard_topic(topic['title'], topic['content'])]
            
            logging.info(f"PT/Onboard 토픽 {len(pt_onboard_topics)}개에서 댓글 모니터링 시작")
            
            for topic in pt_onboard_topics:
                try:
                    # 토픽 상세 페이지 가져오기
                    topic_html = self.fetch_page(topic['url'])
                    if topic_html:
                        # 댓글 파싱
                        current_comments = self.parse_comments(topic_html, topic['id'], topic['url'])
                        
                        # 새로운 댓글 확인
                        new_comments = self.check_new_comments(current_comments)
                        if new_comments:
                            logging.info(f"PT/Onboard 토픽 {topic['id']}에서 새로운 댓글 {len(new_comments)}개 발견")
                            for comment in new_comments:
                                message = self.format_comment_message(comment)
                                self.send_telegram_message(message)
                                time.sleep(2)  # 메시지 간격
                            
                            total_new_comments += len(new_comments)
                    
                    time.sleep(1)  # 토픽 간 간격
                    
                except Exception as e:
                    logging.error(f"PT/Onboard 토픽 {topic['id']} 모니터링 오류: {e}")
                    continue
            
            # 완료 알림
            completion_message = f"""✅ <b>Aave PT/Onboard 모니터링 완료</b>

📊 <b>모니터링 결과:</b>
• 총 토픽: {len(current_topics)}개
• PT/Onboard 토픽: {len(pt_onboard_topics)}개
• 새로운 PT/Onboard 토픽: {len(new_topics)}개
• 새로운 댓글: {total_new_comments}개

⏰ <b>완료 시간:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#Aave #Governance #PT #Onboard #Monitor #Complete"""
            
            self.send_telegram_message(completion_message)
            
        except Exception as e:
            logging.error(f"모니터링 오류: {e}")
            error_message = f"""❌ <b>Aave PT/Onboard 모니터링 오류</b>

🚨 <b>오류 내용:</b> {str(e)}
⏰ <b>발생 시간:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#Aave #Governance #PT #Onboard #Monitor #Error"""
            
            self.send_telegram_message(error_message)

def main():
    """메인 함수"""
    print("🚀 Aave PT/Onboard 모니터링 봇")
    print("=" * 50)
    print(f"📋 모니터링 대상: 제목에 'PT'와 'onboard'가 동시에 포함된 토픽")
    print(f"🔗 포럼: {FORUM_URL}")
    print(f"⏰ 탐색 범위: 최근 2주 내 활동")
    print(f"🤖 텔레그램 봇: {TELEGRAM_TOKEN}")
    print(f"💬 채팅 ID: {CHAT_ID}")
    print(f"⏰ 체크 간격: {CHECK_INTERVAL}초")
    print("=" * 50)
    
    try:
        monitor = AavePTOndboardMonitor()
        monitor.monitor()
    except KeyboardInterrupt:
        print("\n👋 모니터링이 중단되었습니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
