#!/usr/bin/env python3
"""
활성 마켓 현황 확인
"""

import requests
from datetime import datetime

def check_active_markets():
    """활성 마켓 현황 확인"""
    
    url = "https://clob.polymarket.com/markets"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    params = {'limit': 100}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get('data', [])
            
            print(f"총 {len(markets)}개 마켓 확인")
            
            # 상태별 분류
            closed_count = 0
            open_count = 0
            accepting_orders_count = 0
            active_count = 0
            recent_markets = []
            
            now = datetime.now()
            
            for market in markets:
                closed = market.get('closed', True)
                accepting_orders = market.get('accepting_orders', False)
                active = market.get('active', True)
                
                if closed:
                    closed_count += 1
                else:
                    open_count += 1
                    
                if accepting_orders:
                    accepting_orders_count += 1
                    
                if active and not closed:
                    active_count += 1
                    
                # 최근 마켓 확인 (end_date_iso가 미래인 것)
                end_date_str = market.get('end_date_iso', '')
                if end_date_str:
                    try:
                        end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                        if end_date > now and not closed:
                            recent_markets.append({
                                'question': market.get('question', 'Unknown'),
                                'end_date': end_date.strftime('%Y-%m-%d'),
                                'accepting_orders': accepting_orders,
                                'active': active,
                                'slug': market.get('market_slug', '')
                            })
                    except:
                        pass
            
            print(f"\n마켓 상태 분석:")
            print(f"  종료된 마켓: {closed_count}")
            print(f"  열린 마켓: {open_count}")
            print(f"  주문 받는 마켓: {accepting_orders_count}")
            print(f"  활성 마켓: {active_count}")
            
            # 최근 활성 마켓 출력
            recent_markets.sort(key=lambda x: x['end_date'], reverse=True)
            
            print(f"\n최근 활성 마켓 (상위 10개):")
            for i, market in enumerate(recent_markets[:10]):
                status = "💚 주문가능" if market['accepting_orders'] else "🟡 주문불가"
                print(f"{i+1}. {market['question'][:60]}...")
                print(f"   만료: {market['end_date']} | {status}")
                print()
            
        else:
            print(f"API 오류: {response.status_code}")
            
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    check_active_markets()