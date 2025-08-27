#!/usr/bin/env python3
"""
마켓 날짜 정보 디버깅
"""

import requests
import json
from datetime import datetime, timezone

def debug_market_dates():
    """마켓 날짜 정보를 자세히 분석"""
    
    url = "https://clob.polymarket.com/markets"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    params = {'limit': 100}
    
    try:
        print("🔍 마켓 날짜 정보 분석 중...")
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get('data', [])
            
            print(f"📊 총 {len(markets)}개 마켓 분석")
            
            # 날짜 정보 분류
            date_stats = {
                'has_end_date': 0,
                'no_end_date': 0,
                'future_dates': 0,
                'past_dates': 0,
                'today': 0,
                'parse_errors': 0
            }
            
            now = datetime.now(timezone.utc)
            sample_markets = []
            
            for i, market in enumerate(markets):
                end_date_str = market.get('end_date_iso', '')
                
                if not end_date_str:
                    date_stats['no_end_date'] += 1
                    continue
                
                date_stats['has_end_date'] += 1
                
                try:
                    # Z를 +00:00으로 변환
                    if end_date_str.endswith('Z'):
                        end_date_str = end_date_str.replace('Z', '+00:00')
                    
                    end_date = datetime.fromisoformat(end_date_str)
                    
                    # UTC 시간대로 변환
                    if end_date.tzinfo is None:
                        end_date = end_date.replace(tzinfo=timezone.utc)
                    
                    days_diff = (end_date - now).days
                    
                    if days_diff > 0:
                        date_stats['future_dates'] += 1
                        if len(sample_markets) < 5:
                            sample_markets.append({
                                'title': market.get('question', 'Unknown')[:50],
                                'end_date': end_date_str,
                                'days_left': days_diff,
                                'closed': market.get('closed', True),
                                'accepting_orders': market.get('accepting_orders', False)
                            })
                    elif days_diff == 0:
                        date_stats['today'] += 1
                    else:
                        date_stats['past_dates'] += 1
                        
                except Exception as e:
                    date_stats['parse_errors'] += 1
                    if i < 5:  # 처음 5개 오류만 출력
                        print(f"날짜 파싱 오류 (마켓 {i}): {end_date_str} - {e}")
            
            # 결과 출력
            print(f"\n📅 날짜 정보 분석 결과:")
            print(f"  ✅ end_date_iso 있는 마켓: {date_stats['has_end_date']}")
            print(f"  ❌ end_date_iso 없는 마켓: {date_stats['no_end_date']}")
            print(f"  🔮 미래 날짜 마켓: {date_stats['future_dates']}")
            print(f"  📅 오늘 만료 마켓: {date_stats['today']}")
            print(f"  ⏰ 과거 날짜 마켓: {date_stats['past_dates']}")
            print(f"  🚨 파싱 오류: {date_stats['parse_errors']}")
            
            # 샘플 마켓 출력
            if sample_markets:
                print(f"\n🔍 미래 날짜 마켓 샘플:")
                for i, market in enumerate(sample_markets, 1):
                    status = "💚" if market['accepting_orders'] else "🟡"
                    print(f"{i}. {market['title']}...")
                    print(f"   만료: {market['end_date']} (남은 일수: {market['days_left']}일)")
                    print(f"   상태: {status} {'주문가능' if market['accepting_orders'] else '주문불가'}")
                    print()
            
            # 첫 번째 마켓의 전체 데이터 출력
            if markets:
                print(f"\n🔍 첫 번째 마켓 전체 데이터:")
                first_market = markets[0]
                print(f"제목: {first_market.get('question', 'N/A')}")
                print(f"end_date_iso: {first_market.get('end_date_iso', 'N/A')}")
                print(f"closed: {first_market.get('closed', 'N/A')}")
                print(f"accepting_orders: {first_market.get('accepting_orders', 'N/A')}")
                print(f"active: {first_market.get('active', 'N/A')}")
                
                # 날짜 파싱 시도
                end_date_str = first_market.get('end_date_iso', '')
                if end_date_str:
                    print(f"\n날짜 파싱 테스트:")
                    print(f"원본: {end_date_str}")
                    
                    # 다양한 형식으로 파싱 시도
                    formats_to_try = [
                        end_date_str,
                        end_date_str.replace('Z', '+00:00'),
                        end_date_str.replace('Z', ''),
                        end_date_str + '+00:00'
                    ]
                    
                    for fmt in formats_to_try:
                        try:
                            parsed = datetime.fromisoformat(fmt)
                            print(f"성공: {fmt} -> {parsed}")
                        except Exception as e:
                            print(f"실패: {fmt} -> {e}")
            
        else:
            print(f"❌ API 오류: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    debug_market_dates() 