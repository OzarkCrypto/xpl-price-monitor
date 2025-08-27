#!/usr/bin/env python3
"""
최신 마켓 찾기 v2 - 다양한 방법으로 시도
"""

import os
import requests
import json
from datetime import datetime, timezone
from notification_system import NotificationSystem

def find_recent_markets_v2():
    """다양한 방법으로 최신 마켓을 찾습니다."""
    
    # 환경 변수 설정
    os.environ['TELEGRAM_BOT_TOKEN'] = '7086607684:AAFEAN-E6XJJW77OfXs4tThEQyxOdi_t98w'
    os.environ['TELEGRAM_CHAT_ID'] = '1339285013'
    
    # 알림 시스템 초기화
    notification = NotificationSystem()
    
    print("🔍 다양한 방법으로 최신 마켓을 찾는 중...")
    
    # 방법 1: 기본 마켓 API (더 많은 마켓)
    print("\n1️⃣ 기본 마켓 API (1000개)")
    markets_1 = fetch_markets_basic(1000)
    
    # 방법 2: 활성 마켓만 필터링
    print("\n2️⃣ 활성 마켓 필터링")
    markets_2 = fetch_active_markets()
    
    # 방법 3: 다른 API 엔드포인트
    print("\n3️⃣ 대체 API 엔드포인트")
    markets_3 = fetch_alternative_api()
    
    # 모든 결과 통합
    all_markets = []
    all_markets.extend(markets_1)
    all_markets.extend(markets_2)
    all_markets.extend(markets_3)
    
    # 중복 제거 (condition_id 기준)
    unique_markets = {}
    for market in all_markets:
        market_id = market.get('condition_id', market.get('question_id', ''))
        if market_id and market_id not in unique_markets:
            unique_markets[market_id] = market
    
    print(f"\n📊 통합 결과: {len(unique_markets)}개 고유 마켓")
    
    # 최신 마켓 선택 (end_date_iso 기준, 미래 날짜만)
    recent_markets = []
    now = datetime.now(timezone.utc)
    
    for market in unique_markets.values():
        end_date_str = market.get('end_date_iso', '')
        if end_date_str:
            try:
                # Z를 +00:00으로 변환
                if end_date_str.endswith('Z'):
                    end_date_str = end_date_str.replace('Z', '+00:00')
                
                end_date = datetime.fromisoformat(end_date_str)
                if end_date.tzinfo is None:
                    end_date = end_date.replace(tzinfo=timezone.utc)
                
                days_diff = (end_date - now).days
                
                if days_diff > 0:  # 미래 날짜만
                    recent_markets.append({
                        'market': market,
                        'end_date': end_date,
                        'days_until_expiry': days_diff
                    })
            except:
                continue
    
    # 만료일까지 남은 일수로 정렬
    recent_markets.sort(key=lambda x: x['days_until_expiry'])
    
    print(f"✅ {len(recent_markets)}개의 미래 마켓 발견")
    
    if recent_markets:
        # 상위 10개 선택
        top_markets = recent_markets[:10]
        
        # 텔레그램 알림 전송
        send_recent_markets_alert(notification, top_markets)
        
        return top_markets
    else:
        # 미래 마켓이 없으면 최근에 생성된 것으로 보이는 마켓들 찾기
        print("\n🔍 미래 마켓이 없습니다. 최근 생성된 마켓을 찾는 중...")
        
        # closed=False이고 accepting_orders=True인 마켓들 찾기
        recent_created = []
        for market in unique_markets.values():
            if not market.get('closed', True) and market.get('accepting_orders', False):
                recent_created.append({
                    'market': market,
                    'title': market.get('question', 'Unknown Market'),
                    'slug': market.get('market_slug', ''),
                    'closed': market.get('closed', True),
                    'accepting_orders': market.get('accepting_orders', False)
                })
        
        if recent_created:
            print(f"✅ {len(recent_created)}개의 최근 생성 마켓 발견")
            send_recent_created_alert(notification, recent_created[:10])
            return recent_created[:10]
        else:
            print("❌ 최근 생성된 마켓도 없습니다.")
            return []

def fetch_markets_basic(limit):
    """기본 마켓 API로 마켓 가져오기"""
    try:
        url = "https://clob.polymarket.com/markets"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        params = {'limit': limit}
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            markets = data.get('data', [])
            print(f"   ✅ {len(markets)}개 마켓 수신")
            return markets
        else:
            print(f"   ❌ API 오류: {response.status_code}")
            return []
    except Exception as e:
        print(f"   ❌ 오류: {e}")
        return []

def fetch_active_markets():
    """활성 마켓만 필터링해서 가져오기"""
    try:
        url = "https://clob.polymarket.com/markets"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 다양한 파라미터로 시도
        params_list = [
            {'active': True},
            {'closed': False},
            {'accepting_orders': True},
            {'limit': 500, 'active': True},
            {'limit': 500, 'closed': False}
        ]
        
        all_markets = []
        for params in params_list:
            try:
                response = requests.get(url, headers=headers, params=params, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    markets = data.get('data', [])
                    all_markets.extend(markets)
            except:
                continue
        
        print(f"   ✅ {len(all_markets)}개 활성 마켓 수신")
        return all_markets
    except Exception as e:
        print(f"   ❌ 오류: {e}")
        return []

def fetch_alternative_api():
    """대체 API 엔드포인트 시도"""
    try:
        # gamma-api.polymarket.com 시도
        url = "https://gamma-api.polymarket.com/markets"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            markets = response.json()
            print(f"   ✅ gamma-api에서 {len(markets)}개 마켓 수신")
            return markets
        else:
            print(f"   ❌ gamma-api 오류: {response.status_code}")
            return []
    except Exception as e:
        print(f"   ❌ gamma-api 오류: {e}")
        return []

def send_recent_markets_alert(notification, recent_markets):
    """최신 마켓들을 텔레그램으로 알림 전송"""
    
    message = """
🔍 <b>폴리마켓 최신 마켓 TOP 10</b>

가장 최근에 만들어진 마켓들을 찾았습니다!
    """.strip()
    
    for i, market_info in enumerate(recent_markets, 1):
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
📊 <b>총 마켓 수:</b> {len(recent_markets)}개

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

def send_recent_created_alert(notification, recent_markets):
    """최근 생성된 마켓들을 텔레그램으로 알림 전송"""
    
    message = """
🔍 <b>폴리마켓 최근 생성 마켓 TOP 10</b>

현재 활성화되어 있는 마켓들을 찾았습니다!
    """.strip()
    
    for i, market_info in enumerate(recent_markets, 1):
        market = market_info['market']
        title = market_info['title']
        slug = market_info['slug']
        closed = market_info['closed']
        accepting_orders = market_info['accepting_orders']
        
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
{status_emoji} 상태: {status_text}
🔗 <a href="{link}">폴리마켓에서 보기</a>
        """.strip()
        
        message += market_info_text
    
    message += f"""

⏰ <b>조회 시간:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}
📊 <b>총 마켓 수:</b> {len(recent_markets)}개

💡 <i>이 마켓들은 현재 활성화되어 있는 마켓들입니다.</i>
    """.strip()
    
    print("📱 텔레그램으로 최근 생성 마켓 알림을 전송합니다...")
    
    # 텔레그램 전송
    success = notification.send_telegram_message(message)
    
    if success:
        print("✅ 텔레그램 알림 전송 성공!")
        print("텔레그램에서 최근 생성 마켓 목록을 확인해보세요.")
    else:
        print("❌ 텔레그램 알림 전송 실패!")

def main():
    """메인 함수"""
    print("🚀 폴리마켓 최신 마켓 찾기 v2 시작")
    print("=" * 60)
    
    recent_markets = find_recent_markets_v2()
    
    if recent_markets:
        print(f"\n✅ {len(recent_markets)}개의 최신 마켓을 찾았습니다!")
        print("\n📋 상위 5개 마켓 미리보기:")
        
        for i, market_info in enumerate(recent_markets[:5], 1):
            if 'days_until_expiry' in market_info:
                # 미래 날짜 마켓
                market = market_info['market']
                days_left = market_info['days_until_expiry']
                title = market.get('question', 'Unknown Market')[:60]
                print(f"{i}. {title}... (만료까지 {days_left}일)")
            else:
                # 최근 생성 마켓
                title = market_info['title'][:60]
                status = "주문가능" if market_info['accepting_orders'] else "주문불가"
                print(f"{i}. {title}... ({status})")
    else:
        print("❌ 최신 마켓을 찾을 수 없습니다.")
    
    print("\n" + "=" * 60)
    print("🎯 완료! 텔레그램에서 상세 정보를 확인하세요.")

if __name__ == "__main__":
    main() 