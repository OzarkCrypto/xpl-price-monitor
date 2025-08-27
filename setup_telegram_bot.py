#!/usr/bin/env python3
"""
Telegram Bot Setup Helper
"""
import webbrowser
import os

def setup_telegram_bot():
    """Help user set up Telegram bot"""
    print("🤖 Telegram Bot 설정 가이드")
    print("=" * 50)
    
    print("\n1️⃣ BotFather으로 이동")
    print("   다음 링크를 클릭하거나 브라우저에서 열어주세요:")
    print("   https://t.me/botfather")
    
    # Open BotFather in browser
    try:
        webbrowser.open("https://t.me/botfather")
        print("   ✅ 브라우저가 열렸습니다.")
    except:
        print("   📱 수동으로 https://t.me/botfather 접속")
    
    print("\n2️⃣ 새 봇 생성")
    print("   BotFather에게 다음 명령어를 보내세요:")
    print("   /newbot")
    
    print("\n3️⃣ 봇 이름 설정")
    print("   예시: Crypto Fundraising Monitor")
    
    print("\n4️⃣ 봇 사용자명 설정")
    print("   예시: crypto_fundraising_bot")
    print("   (반드시 'bot'으로 끝나야 함)")
    
    print("\n5️⃣ 봇 토큰 복사")
    print("   BotFather가 제공하는 토큰을 복사하세요")
    print("   예시: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
    
    print("\n6️⃣ .env 파일에 토큰 설정")
    print("   .env 파일을 열어서 다음 줄을 수정하세요:")
    print("   TELEGRAM_BOT_TOKEN=실제_토큰_입력")
    
    print("\n7️⃣ 봇을 채팅방에 초대")
    print("   생성된 봇을 원하는 채팅방에 초대하세요")
    
    print("\n8️⃣ 채팅방 ID 확인")
    print("   봇이 채팅방에 있으면 다음 명령어로 ID 확인:")
    print("   /start")
    
    print("\n9️⃣ 시스템 테스트")
    print("   설정 완료 후 다음 명령어로 테스트:")
    print("   python3 test_system.py")
    
    print("\n🔟 실제 실행")
    print("   모든 설정이 완료되면:")
    print("   python3 crypto_fundraising_monitor/run.py")
    
    print("\n" + "=" * 50)
    print("❓ 문제가 있으면 README_crypto_fundraising.md를 참고하세요")
    
    # Check if .env exists and show current status
    if os.path.exists('.env'):
        print("\n📋 현재 .env 상태:")
        with open('.env', 'r') as f:
            content = f.read()
            if 'your_bot_token_here' in content:
                print("   ⚠️  TELEGRAM_BOT_TOKEN이 아직 설정되지 않았습니다")
            else:
                print("   ✅ TELEGRAM_BOT_TOKEN이 설정되어 있습니다")
    else:
        print("\n📋 .env 파일이 없습니다. env_template.txt를 복사해주세요")

if __name__ == "__main__":
    setup_telegram_bot() 