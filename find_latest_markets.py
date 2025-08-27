#!/usr/bin/env python3
"""
가장 최근에 만들어진 폴리마켓 마켓 찾기 및 알림
"""

import os
import requests
import json
from datetime import datetime, timezone
from notification_system import NotificationSystem

def find_latest_markets():
    """가장 최근에 만들어진 마켓들을 찾습니다."""
    
    # 환경 변수 설정
    os.environ['TELEGRAM_BOT_TOKEN'] = '7086607684:AAFEAN-E6XJJW77OfXs4tThEQyxOdi_t98w'
    os.environ['TELEGRAM_CHAT_ID'] = '1339285013'
    
    # 알림 시스템 초기화
    notification = NotificationSystem()
    
    url = "https://clob.polymarket.com/markets"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # 더 많은 마켓을 가져와서 최신 것들을 찾기
    params = {'limit': 1000}
    
    try:
        print("🔍 폴리마켓에서 최신 마켓을 찾는 중...")
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get('data', [])
            
            print(f"📊 총 {len(markets)}개 마켓 데이터 수신")
            
            # 마켓을 end_date_iso 기준으로 정렬 (최신 순)
            valid_markets = []
            now = datetime.now(timezone.utc)
            
            for market in markets:
                end_date_str = market.get('end_date_iso', '')
                if end_date_str:
                    try:
                        end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                        # 미래 날짜의 마켓만 포함
                        if end_date > now:
                            valid_markets.append({
                                'market': market,
                                'end_date': end_date,
                                'days_until_expiry': (end_date - now).days
                            })
                    except:
                        continue
            
            # 만료일까지 남은 일수로 정렬 (가장 최근에 만료되는 것 = 가장 최근에 만들어진 것)
            valid_markets.sort(key=lambda x: x['days_until_expiry'])
            
            print(f"✅ {len(valid_markets)}개의 유효한 미래 마켓 발견")
            
            # 상위 10개 마켓 선택
            latest_markets = valid_markets[:10]
            
            # 텔레그램 알림 전송
            send_latest_markets_alert(notification, latest_markets)
            
            return latest_markets
            
        else:
            print(f"❌ API 오류: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return []

def send_latest_markets_alert(notification, latest_markets):
    """최신 마켓들을 텔레그램으로 알림 전송"""
    
    message = """
🔍 <b>폴리마켓 최신 마켓 TOP 10</b>

가장 최근에 만들어진 마켓들을 찾았습니다!
    """.strip()
    
    for i, market_info in enumerate(latest_markets, 1):
        market = market_info['market']
        days_left = market_info['days_until_expiry']
        
        # 마켓 정보 추출
        title = market.get('question', 'Unknown Market')
        slug = market.get('market_slug', '')
        end_date = market_info['end_date'].strftime('%Y-%m-%d %H:%M UTC')
        closed = market.get('closed', True)
        accepting_orders = market.get('accepting_orders', False)
        
        # 상태 이모지
        if closed:
            status_emoji = "🔴"
            status_text = "종료됨"
        elif accepting_orders:
            status_emoji = "💚"
            status_text = "주문가능"
        else:
            status_emoji = "🟡"
            status_text = "주문불가"
        
        # 링크 생성
        if slug:
            link = f"https://polymarket.com/markets/{slug}"
        else:
            link = "https://polymarket.com"
        
        # 마켓 정보 추가
        market_info_text = f"""
{i}. <b>{title[:80]}{'...' if len(title) > 80 else ''}</b>
📅 만료: {end_date}
⏰ 남은 일수: {days_left}일
{status_emoji} 상태: {status_text}
🔗 <a href="{link}">폴리마켓에서 보기</a>
        """.strip()
        
        message += market_info_text
    
    message += f"""

⏰ <b>조회 시간:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}
📊 <b>총 마켓 수:</b> {len(latest_markets)}개

💡 <i>이 마켓들은 가장 최근에 생성되었거나 가장 빨리 만료되는 마켓들입니다.</i>
    """.strip()
    
    print("📱 텔레그램으로 최신 마켓 알림을 전송합니다...")
    
    # 텔레그램 전송
    success = notification.send_telegram_message(message)
    
    if success:
        print("✅ 텔레그램 알림 전송 성공!")
        print("텔레그램에서 최신 마켓 목록을 확인해보세요.")
    else:
        print("❌ 텔레그램 알림 전송 실패!")

def main():
    """메인 함수"""
    print("🚀 폴리마켓 최신 마켓 찾기 시작")
    print("=" * 50)
    
    latest_markets = find_latest_markets()
    
    if latest_markets:
        print(f"\n✅ {len(latest_markets)}개의 최신 마켓을 찾았습니다!")
        print("\n📋 상위 5개 마켓 미리보기:")
        
        for i, market_info in enumerate(latest_markets[:5], 1):
            market = market_info['market']
            days_left = market_info['days_until_expiry']
            title = market.get('question', 'Unknown Market')[:60]
            
            print(f"{i}. {title}... (만료까지 {days_left}일)")
    else:
        print("❌ 최신 마켓을 찾을 수 없습니다.")
    
    print("\n" + "=" * 50)
    print("🎯 완료! 텔레그램에서 상세 정보를 확인하세요.")

if __name__ == "__main__":
    main() 