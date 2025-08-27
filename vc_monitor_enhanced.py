#!/usr/bin/env python3
"""
Enhanced VC Investment Monitor Bot
향상된 스크래퍼를 사용하여 VC 투자 정보를 모니터링하고 알림을 보내는 봇
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import aiohttp
import sqlite3
import os
from vc_scraper import VCFundraisingScraper

# 텔레그램 봇 설정
TELEGRAM_TOKEN = "7902910088:AAEF6kdafHyu-gCdvC5kWoq1CpDeabtw0_g"
CHAT_ID = "1339285013"

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vc_monitor_enhanced.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedVCInvestmentMonitor:
    def __init__(self):
        self.db_path = "vc_monitor_enhanced.db"
        self.top_vcs = [
            # Tier 1: 최고 수준의 VC
            "a16z", "Andreessen Horowitz", "Paradigm", "Polychain Capital", "Pantera Capital",
            "Electric Capital", "Multicoin Capital", "Framework Ventures", "Dragonfly Capital",
            
            # Tier 2: 주요 VC
            "Binance Labs", "Coinbase Ventures", "Galaxy Digital", "Digital Currency Group",
            "BlockTower Capital", "Arrington Capital", "Blockchain Capital", "ConsenSys Ventures",
            "Placeholder", "1confirmation", "Variant Fund", "Standard Crypto",
            
            # Tier 3: 성장하는 VC
            "Crypto.com Capital", "Animoca Brands", "Y Combinator", "Sequoia Capital",
            "Tiger Global", "SoftBank", "Republic", "HyperChain Capital", "Breyer Capital",
            "Selini Capital", "Big Brain Holdings", "DNA Fund", "Protein Capital",
            "Quantstamp", "Web3com Ventures", "KuCoin Ventures", "Karatage", "Sui Foundation",
            "ParaFi Capital", "Kraken", "Arrington Capital", "FalconX", "Paper Ventures",
            "Maven 11 Capital", "dao5", "daofive", "Comma3 Ventures", "Borderless Capital"
        ]
        
        # VC 등급별 가중치
        self.vc_tiers = {
            "tier1": ["a16z", "Andreessen Horowitz", "Paradigm", "Polychain Capital", "Pantera Capital"],
            "tier2": ["Electric Capital", "Multicoin Capital", "Framework Ventures", "Dragonfly Capital"],
            "tier3": ["Binance Labs", "Coinbase Ventures", "Galaxy Digital", "Digital Currency Group"]
        }
        
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
                notified BOOLEAN DEFAULT FALSE,
                vc_score INTEGER DEFAULT 0
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
                vc_score INTEGER DEFAULT 0,
                tier_level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notified BOOLEAN DEFAULT FALSE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vc_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vc_name TEXT NOT NULL,
                investment_count INTEGER DEFAULT 0,
                last_investment_date TEXT,
                total_amount TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("향상된 데이터베이스 초기화 완료")
    
    def calculate_vc_score(self, found_vcs: List[str]) -> tuple[int, str]:
        """VC 참여도에 따른 점수 계산"""
        if not found_vcs:
            return 0, "none"
        
        score = 0
        tier_level = "none"
        
        for vc in found_vcs:
            vc_lower = vc.lower()
            
            # Tier 1: 최고 점수
            if any(t1.lower() in vc_lower for t1 in self.vc_tiers["tier1"]):
                score += 100
                tier_level = "tier1"
            # Tier 2: 중간 점수
            elif any(t2.lower() in vc_lower for t2 in self.vc_tiers["tier2"]):
                score += 70
                tier_level = "tier2"
            # Tier 3: 기본 점수
            elif any(t3.lower() in vc_lower for t3 in self.vc_tiers["tier3"]):
                score += 50
                tier_level = "tier3"
            # 기타 Top VC
            elif any(top_vc.lower() in vc_lower for top_vc in self.top_vcs):
                score += 30
                tier_level = "other_top"
        
        # 투자자 수에 따른 보너스 점수
        if len(found_vcs) >= 3:
            score += 20
        elif len(found_vcs) >= 2:
            score += 10
        
        return score, tier_level
    
    async def scrape_investments(self) -> List[Dict]:
        """향상된 스크래퍼를 사용하여 투자 정보 수집"""
        try:
            async with VCFundraisingScraper() as scraper:
                investments = await scraper.scrape_recent_fundraising()
                logger.info(f"스크래핑 완료: {len(investments)}개 투자 정보 발견")
                return investments
        except Exception as e:
            logger.error(f"스크래핑 오류: {e}")
            return []
    
    def check_top_vc_involvement(self, investors: str) -> tuple[bool, List[str], int, str]:
        """투자자 목록에서 Top VC 참여 여부 확인 및 점수 계산"""
        if not investors or investors == 'Unknown':
            return False, [], 0, "none"
        
        found_vcs = []
        investors_lower = investors.lower()
        
        for vc in self.top_vcs:
            if vc.lower() in investors_lower:
                found_vcs.append(vc)
        
        has_top_vc = len(found_vcs) > 0
        vc_score, tier_level = self.calculate_vc_score(found_vcs)
        
        return has_top_vc, found_vcs, vc_score, tier_level
    
    def save_investment(self, investment: Dict, vc_score: int = 0):
        """투자 정보를 데이터베이스에 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO vc_investments 
            (project_name, round_type, date, amount, categories, investors, source, vc_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            investment['project_name'],
            investment['round_type'],
            investment['date'],
            investment['amount'],
            investment['categories'],
            investment['investors'],
            investment['source'],
            vc_score
        ))
        
        conn.commit()
        conn.close()
    
    def save_top_vc_investment(self, investment: Dict, top_vcs: List[str], vc_score: int, tier_level: str):
        """Top VC가 참여한 투자를 별도 테이블에 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO top_vc_investments 
            (project_name, round_type, date, amount, categories, top_vcs, all_investors, source, vc_score, tier_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            investment['project_name'],
            investment['round_type'],
            investment['date'],
            investment['amount'],
            investment['categories'],
            ', '.join(top_vcs),
            investment['investors'],
            investment['source'],
            vc_score,
            tier_level
        ))
        
        conn.commit()
        conn.close()
    
    def update_vc_stats(self, vc_names: List[str], investment_date: str, amount: str):
        """VC 통계 업데이트"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for vc_name in vc_names:
            # 기존 통계 확인
            cursor.execute('SELECT * FROM vc_stats WHERE vc_name = ?', (vc_name,))
            existing = cursor.fetchone()
            
            if existing:
                # 기존 통계 업데이트
                cursor.execute('''
                    UPDATE vc_stats 
                    SET investment_count = investment_count + 1,
                        last_investment_date = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE vc_name = ?
                ''', (investment_date, vc_name))
            else:
                # 새로운 VC 통계 생성
                cursor.execute('''
                    INSERT INTO vc_stats (vc_name, investment_count, last_investment_date, total_amount)
                    VALUES (?, 1, ?, ?)
                ''', (vc_name, investment_date, amount))
        
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
    
    def format_investment_message(self, investment: Dict, top_vcs: List[str], vc_score: int, tier_level: str) -> str:
        """투자 정보를 텔레그램 메시지 형식으로 포맷팅"""
        # Tier별 이모지 설정
        tier_emoji = {
            "tier1": "🔥🔥🔥",
            "tier2": "🔥🔥",
            "tier3": "🔥",
            "other_top": "⭐",
            "none": "📊"
        }
        
        emoji = tier_emoji.get(tier_level, "📊")
        
        message = f"""
{emoji} <b>VC 투자 알림!</b> {emoji}

📊 <b>프로젝트:</b> {investment['project_name']}
💰 <b>라운드:</b> {investment['round_type']}
📅 <b>날짜:</b> {investment['date']}
💵 <b>금액:</b> {investment['amount']}
🏷️ <b>카테고리:</b> {investment['categories']}
⭐ <b>VC 점수:</b> {vc_score}/100

🚀 <b>참여한 Top VC:</b>
{chr(10).join([f"• {vc}" for vc in top_vcs])}

👥 <b>전체 투자자:</b>
{investment['investors']}

🔗 <b>출처:</b> {investment['source']}
        """
        return message.strip()
    
    async def check_new_investments(self):
        """새로운 투자 정보 확인 및 알림"""
        try:
            # 향상된 스크래퍼로 투자 정보 수집
            investments = await self.scrape_investments()
            
            for investment in investments:
                # 이미 저장된 투자인지 확인
                if not self.is_investment_exists(investment):
                    # Top VC 참여 여부 확인 및 점수 계산
                    has_top_vc, top_vcs, vc_score, tier_level = self.check_top_vc_involvement(investment['investors'])
                    
                    # 투자 정보 저장
                    self.save_investment(investment, vc_score)
                    
                    if has_top_vc:
                        # Top VC 투자 정보 별도 저장
                        self.save_top_vc_investment(investment, top_vcs, vc_score, tier_level)
                        
                        # VC 통계 업데이트
                        self.update_vc_stats(top_vcs, investment['date'], investment['amount'])
                        
                        # 텔레그램 알림 전송 (점수가 50 이상인 경우만)
                        if vc_score >= 50:
                            message = self.format_investment_message(investment, top_vcs, vc_score, tier_level)
                            await self.send_telegram_message(message)
                            
                            logger.info(f"Top VC 투자 알림 전송: {investment['project_name']} (점수: {vc_score})")
                        else:
                            logger.info(f"VC 점수 부족으로 알림 생략: {investment['project_name']} (점수: {vc_score})")
                    
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
    
    async def send_daily_summary(self):
        """일일 투자 요약 전송"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 오늘의 투자 정보 조회
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT COUNT(*) FROM vc_investments WHERE date = ?
            ''', (today,))
            
            total_investments = cursor.fetchone()[0]
            
            # 오늘의 Top VC 투자 조회
            cursor.execute('''
                SELECT COUNT(*) FROM top_vc_investments WHERE date = ?
            ''', (today,))
            
            top_vc_investments = cursor.fetchone()[0]
            
            # 가장 활발한 VC 조회
            cursor.execute('''
                SELECT vc_name, investment_count FROM vc_stats 
                ORDER BY investment_count DESC LIMIT 5
            ''')
            
            top_vcs = cursor.fetchall()
            
            conn.close()
            
            if total_investments > 0:
                message = f"""
📊 <b>일일 VC 투자 요약</b>

📅 <b>날짜:</b> {today}
💼 <b>총 투자:</b> {total_investments}건
⭐ <b>Top VC 투자:</b> {top_vc_investments}건

🏆 <b>가장 활발한 VC:</b>
{chr(10).join([f"• {vc[0]}: {vc[1]}건" for vc in top_vcs])}
                """
                
                await self.send_telegram_message(message.strip())
                logger.info("일일 요약 전송 완료")
                
        except Exception as e:
            logger.error(f"일일 요약 전송 오류: {e}")
    
    async def run_monitor(self):
        """모니터링 실행"""
        logger.info("향상된 VC 투자 모니터링 시작")
        
        # 시작 알림 전송
        start_message = """
🚀 <b>VC 투자 모니터링 봇 시작!</b>

✅ crypto-fundraising.info 모니터링 활성화
✅ Top VC 투자 알림 설정 완료
✅ 자동 점수 계산 시스템 활성화

모니터링을 시작합니다...
        """
        await self.send_telegram_message(start_message.strip())
        
        last_daily_summary = datetime.now().date()
        
        while True:
            try:
                await self.check_new_investments()
                
                # 일일 요약 전송 (매일 자정)
                current_date = datetime.now().date()
                if current_date > last_daily_summary:
                    await self.send_daily_summary()
                    last_daily_summary = current_date
                
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
    monitor = EnhancedVCInvestmentMonitor()
    await monitor.run_monitor()

if __name__ == "__main__":
    asyncio.run(main())
