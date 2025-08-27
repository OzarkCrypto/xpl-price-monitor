#!/usr/bin/env python3
"""
VC Investment Monitor Bot
VC 투자 정보를 모니터링하고 좋은 VC가 투자한 프로젝트에 대해 알람을 보내는 텔레그램 봇
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import aiohttp
from bs4 import BeautifulSoup
import sqlite3
import os

# 텔레그램 봇 설정
TELEGRAM_TOKEN = "7902910088:AAEF6kdafHyu-gCdvC5kWoq1CpDeabtw0_g"
CHAT_ID = "1339285013"

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vc_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VCInvestmentMonitor:
    def __init__(self):
        self.db_path = "vc_monitor.db"
        self.top_vcs = [
            "a16z", "Andreessen Horowitz", "Paradigm", "Polychain", "Pantera Capital",
            "Electric Capital", "Multicoin Capital", "Framework Ventures", "Dragonfly Capital",
            "Three Arrows Capital", "Alameda Research", "Binance Labs", "Coinbase Ventures",
            "Galaxy Digital", "Digital Currency Group", "BlockTower Capital", "Arrington Capital",
            "Blockchain Capital", "ConsenSys Ventures", "Polychain Capital", "Placeholder",
            "1confirmation", "Variant Fund", "Standard Crypto", "Crypto.com Capital",
            "Animoca Brands", "Y Combinator", "Sequoia Capital", "Tiger Global", "SoftBank"
        ]
        self.init_database()
        
    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vc_investments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                round_type TEXT,
                date TEXT,
                amount TEXT,
                categories TEXT,
                investors TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notified BOOLEAN DEFAULT FALSE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS top_vc_investments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                round_type TEXT,
                date TEXT,
                amount TEXT,
                categories TEXT,
                top_vcs TEXT,
                all_investors TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notified BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("데이터베이스 초기화 완료")
    
    async def scrape_crypto_fundraising(self) -> List[Dict]:
        """crypto-fundraising.info에서 투자 정보 스크래핑"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://crypto-fundraising.info/') as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        investments = []
                        # 최근 투자 이벤트 찾기
                        project_elements = soup.find_all('div', class_='project-item') or soup.find_all('tr')
                        
                        for element in project_elements[:10]:  # 최근 10개 프로젝트
                            try:
                                # 프로젝트 정보 추출 (웹사이트 구조에 따라 조정 필요)
                                project_name = element.find('h3') or element.find('td')
                                if project_name:
                                    project_name = project_name.get_text(strip=True)
                                    
                                    # 간단한 정보 구조로 파싱
                                    investment = {
                                        'project_name': project_name,
                                        'round_type': 'Unknown',
                                        'date': datetime.now().strftime('%Y-%m-%d'),
                                        'amount': 'TBD',
                                        'categories': 'Unknown',
                                        'investors': 'Unknown',
                                        'source': 'crypto-fundraising.info'
                                    }
                                    investments.append(investment)
                            except Exception as e:
                                logger.error(f"프로젝트 파싱 오류: {e}")
                                continue
                        
                        return investments
                    else:
                        logger.error(f"crypto-fundraising.info 접근 실패: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"crypto-fundraising.info 스크래핑 오류: {e}")
            return []
    
    async def scrape_twitter_dealflow(self) -> List[Dict]:
        """Twitter/X에서 Crypto_Dealflow 정보 스크래핑 (간단한 구조)"""
        # Twitter API 접근이 제한적이므로 기본 구조만 제공
        return []
    
    def check_top_vc_involvement(self, investors: str) -> tuple[bool, List[str]]:
        """투자자 목록에서 Top VC 참여 여부 확인"""
        if not investors or investors == 'Unknown':
            return False, []
        
        found_vcs = []
        investors_lower = investors.lower()
        
        for vc in self.top_vcs:
            if vc.lower() in investors_lower:
                found_vcs.append(vc)
        
        return len(found_vcs) > 0, found_vcs
    
    def save_investment(self, investment: Dict):
        """투자 정보를 데이터베이스에 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO vc_investments 
            (project_name, round_type, date, amount, categories, investors, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            investment['project_name'],
            investment['round_type'],
            investment['date'],
            investment['amount'],
            investment['categories'],
            investment['investors'],
            investment['source']
        ))
        
        conn.commit()
        conn.close()
    
    def save_top_vc_investment(self, investment: Dict, top_vcs: List[str]):
        """Top VC가 참여한 투자를 별도 테이블에 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO top_vc_investments 
            (project_name, round_type, date, amount, categories, top_vcs, all_investors, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            investment['project_name'],
            investment['round_type'],
            investment['date'],
            investment['amount'],
            investment['categories'],
            ', '.join(top_vcs),
            investment['investors'],
            investment['source']
        ))
        
        conn.commit()
        conn.close()
    
    async def send_telegram_message(self, message: str):
        """텔레그램으로 메시지 전송"""
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            data = {
                "chat_id": CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        logger.info("텔레그램 메시지 전송 성공")
                    else:
                        logger.error(f"텔레그램 메시지 전송 실패: {response.status}")
        except Exception as e:
            logger.error(f"텔레그램 메시지 전송 오류: {e}")
    
    def format_investment_message(self, investment: Dict, top_vcs: List[str]) -> str:
        """투자 정보를 텔레그램 메시지 형식으로 포맷팅"""
        message = f"""
🚀 <b>Top VC 투자 알림!</b>

📊 <b>프로젝트:</b> {investment['project_name']}
💰 <b>라운드:</b> {investment['round_type']}
📅 <b>날짜:</b> {investment['date']}
💵 <b>금액:</b> {investment['amount']}
🏷️ <b>카테고리:</b> {investment['categories']}

⭐ <b>참여한 Top VC:</b>
{chr(10).join([f"• {vc}" for vc in top_vcs])}

👥 <b>전체 투자자:</b>
{investment['investors']}

🔗 <b>출처:</b> {investment['source']}
        """
        return message.strip()
    
    async def check_new_investments(self):
        """새로운 투자 정보 확인 및 알림"""
        try:
            # crypto-fundraising.info에서 정보 스크래핑
            investments = await self.scrape_crypto_fundraising()
            
            for investment in investments:
                # 이미 저장된 투자인지 확인
                if not self.is_investment_exists(investment):
                    # Top VC 참여 여부 확인
                    has_top_vc, top_vcs = self.check_top_vc_involvement(investment['investors'])
                    
                    # 투자 정보 저장
                    self.save_investment(investment)
                    
                    if has_top_vc:
                        # Top VC 투자 정보 별도 저장
                        self.save_top_vc_investment(investment, top_vcs)
                        
                        # 텔레그램 알림 전송
                        message = self.format_investment_message(investment, top_vcs)
                        await self.send_telegram_message(message)
                        
                        logger.info(f"Top VC 투자 알림 전송: {investment['project_name']}")
                    
                    # 잠시 대기 (API 제한 방지)
                    await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"투자 정보 확인 오류: {e}")
    
    def is_investment_exists(self, investment: Dict) -> bool:
        """투자 정보가 이미 데이터베이스에 존재하는지 확인"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM vc_investments 
            WHERE project_name = ? AND date = ? AND source = ?
        ''', (investment['project_name'], investment['date'], investment['source']))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    async def run_monitor(self):
        """모니터링 실행"""
        logger.info("VC 투자 모니터링 시작")
        
        while True:
            try:
                await self.check_new_investments()
                logger.info("투자 정보 확인 완료, 30분 후 재확인")
                await asyncio.sleep(1800)  # 30분 대기
                
            except KeyboardInterrupt:
                logger.info("모니터링 중단")
                break
            except Exception as e:
                logger.error(f"모니터링 오류: {e}")
                await asyncio.sleep(300)  # 오류 시 5분 후 재시도

async def main():
    """메인 함수"""
    monitor = VCInvestmentMonitor()
    await monitor.run_monitor()

if __name__ == "__main__":
    asyncio.run(main())
