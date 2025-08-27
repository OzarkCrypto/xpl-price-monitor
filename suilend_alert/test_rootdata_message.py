#!/usr/bin/env python3
"""
Rootdata Hot Index 텔레그램 메시지 테스트 스크립트
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def test_telegram_message():
    """기존 데이터를 사용해서 텔레그램 메시지를 테스트합니다."""
    
    # 텔레그램 설정
    telegram_bot_token = os.getenv('ROOTDATA_BOT_TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = os.getenv('ROOTDATA_CHAT_ID') or os.getenv('TELEGRAM_CHAT_ID')
    extra_chat_id = os.getenv('ROOTDATA_EXTRA_CHAT_ID')
    
    if not telegram_bot_token or not telegram_chat_id:
        print("❌ 텔레그램 설정이 완료되지 않았습니다.")
        return
    
    # 기존 데이터 로드
    try:
        with open('rootdata_hot_index_history.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"✅ 기존 데이터 로드 완료: {len(data.get('data', []))}개 프로젝트")
    except Exception as e:
        print(f"❌ 데이터 로드 실패: {e}")
        return
    
    # 프로젝트 이름 매핑 (긴 이름을 짧고 명확하게)
    project_name_mapping = {
        'Game developer platformOVERTAKE': 'OVERTAKE',
        'A Web3 Privacy Acceleration so...': 'Multiple Network',
        'Fantasy sports platformFootball.Fun': 'Football.Fun',
        'Crypto Lending PlatformWorld Liberty Financial': 'World Liberty Financial',
        'Meme CoinYZY MoneyYZY': 'YZY Money',
        'Connecting Bitcoin to DeFi with LBTCLombard': 'Lombard',
        'Layer 1 blockchainSuiSUI': 'SUI',
        'Intention-driven modular blockchainWarden Protocol': 'Warden Protocol',
        'Token launchpadheavenLIGHT': 'heaven',
        'Cross-platform play-and-earn d...': 'Xterio'
    }
    
    def clean_project_name(project_name):
        """프로젝트 이름을 읽기 쉽게 정리합니다."""
        if project_name in project_name_mapping:
            return project_name_mapping[project_name]
        return project_name
    
    # 텔레그램 메시지 포맷
    def format_telegram_message(data):
        """텔레그램 메시지를 포맷합니다."""
        if not data:
            return "❌ Hot index 데이터를 가져올 수 없습니다."
        
        # TOP 10만 선택
        top_data = sorted(data, key=lambda x: x.get('hot_index', 0), reverse=True)[:10]
        
        message = "🔥 Rootdata Hot Index TOP 10 (테스트)\n"
        message += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        message += "⏰ 매시간 정각 업데이트\n\n"
        
        for i, item in enumerate(top_data, 1):
            project_name = clean_project_name(item['project_name'])
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
    
    # 메시지 생성
    message = format_telegram_message(data['data'])
    print("📝 생성된 메시지:")
    print("=" * 50)
    print(message)
    print("=" * 50)
    
    # 전송할 채널 목록
    chat_ids = [telegram_chat_id]
    if extra_chat_id:
        chat_ids.append(extra_chat_id)
    
    print(f"📤 총 {len(chat_ids)}개 채널에 메시지 전송 중...")
    
    # 텔레그램으로 메시지 전송
    success_count = 0
    for chat_id in chat_ids:
        try:
            url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
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
                print(f"✅ 텔레그램 메시지 전송 성공 (Chat ID: {chat_id})")
                success_count += 1
            else:
                print(f"❌ 텔레그램 API 오류: {result.get('description', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ 텔레그램 전송 실패 (Chat ID: {chat_id}): {e}")
    
    if success_count == len(chat_ids):
        print(f"🎉 모든 채널({len(chat_ids)}개)에 메시지 전송 완료!")
    else:
        print(f"⚠️ 일부 채널 전송 실패: {success_count}/{len(chat_ids)}")

if __name__ == "__main__":
    test_telegram_message() 