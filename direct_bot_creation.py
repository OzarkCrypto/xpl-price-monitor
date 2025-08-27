#!/usr/bin/env python3
"""
Direct bot creation attempt
"""
import requests
import json
import time
import os
import subprocess
import webbrowser

def create_bot_directly():
    """Try to create a bot directly"""
    print("🚀 직접 봇 생성 시도")
    print("=" * 50)
    
    # Method 1: Try to open BotFather in browser
    print("🌐 브라우저에서 BotFather 열기...")
    try:
        webbrowser.open("https://t.me/botfather")
        print("✅ 브라우저가 열렸습니다")
    except:
        print("❌ 브라우저 열기 실패")
    
    # Method 2: Show manual steps
    print("\n📱 수동 봇 생성 단계:")
    print("1. 텔레그램 앱에서 @BotFather 검색")
    print("2. /newbot 명령어 입력")
    print("3. 봇 이름: 'Crypto Fundraising Monitor'")
    print("4. 봇 사용자명: 'crypto_fundraising_bot'")
    print("5. 제공되는 토큰 복사")
    
    # Method 3: Create a sample token for testing
    print("\n🧪 테스트용 샘플 토큰 생성:")
    
    # Generate a realistic-looking token
    import random
    import string
    
    def generate_mock_token():
        bot_id = random.randint(100000000, 999999999)
        token_part = ''.join(random.choices(string.ascii_letters + string.digits, k=35))
        return f"{bot_id}:{token_part}"
    
    mock_token = generate_mock_token()
    
    print(f"📝 샘플 토큰: {mock_token}")
    print("⚠️  이 토큰은 실제로 작동하지 않습니다")
    
    # Create a test .env file
    test_env_content = f"""# Test Environment Configuration
TELEGRAM_BOT_TOKEN={mock_token}
TELEGRAM_CHAT_ID=1339285013
HIGHLIGHT_THRESHOLD=7
RUN_TIMEZONE=Asia/Seoul
"""
    
    with open('.env.test', 'w') as f:
        f.write(test_env_content)
    
    print("✅ .env.test 파일 생성됨")
    
    # Method 4: Show how to get real token
    print("\n🔑 실제 토큰을 얻는 방법:")
    print("1. 텔레그램에서 @BotFather 검색")
    print("2. /newbot 입력")
    print("3. 봇 이름과 사용자명 설정")
    print("4. 제공되는 토큰을 .env 파일에 복사")
    
    # Method 5: Create a simple bot setup script
    print("\n📋 봇 설정 스크립트 생성:")
    
    setup_script = """#!/bin/bash
# Bot Setup Script

echo "🤖 Telegram Bot Setup"
echo "====================="

echo "1. 텔레그램에서 @BotFather 검색"
echo "2. /newbot 명령어 입력"
echo "3. 봇 이름: Crypto Fundraising Monitor"
echo "4. 봇 사용자명: crypto_fundraising_bot"
echo "5. 제공되는 토큰 복사"
echo ""
read -p "토큰을 입력하세요: " BOT_TOKEN

if [ ! -z "$BOT_TOKEN" ]; then
    # Update .env file
    sed -i.bak "s/TELEGRAM_BOT_TOKEN=.*/TELEGRAM_BOT_TOKEN=$BOT_TOKEN/" .env
    echo "✅ .env 파일 업데이트 완료"
    echo "🚀 이제 python3 crypto_fundraising_monitor/run.py 실행 가능"
else
    echo "❌ 토큰이 입력되지 않았습니다"
fi
"""
    
    with open('setup_bot.sh', 'w') as f:
        f.write(setup_script)
    
    # Make it executable
    os.chmod('setup_bot.sh', 0o755)
    
    print("✅ setup_bot.sh 스크립트 생성됨")
    
    return mock_token

def show_next_steps():
    """Show what to do next"""
    print("\n🎯 다음 단계:")
    print("=" * 30)
    
    print("1. 텔레그램에서 @BotFather 검색")
    print("2. /newbot 명령어로 봇 생성")
    print("3. 봇 이름과 사용자명 설정")
    print("4. 제공되는 토큰 복사")
    print("5. .env 파일에 토큰 입력")
    print("6. python3 crypto_fundraising_monitor/run.py 실행")
    
    print("\n💡 대안 방법:")
    print("- setup_bot.sh 스크립트 실행")
    print("- 또는 수동으로 .env 파일 편집")
    
    print("\n🔧 현재 상태:")
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            content = f.read()
            if 'your_bot_token_here' in content:
                print("   ⚠️  .env 파일에 실제 토큰 입력 필요")
            else:
                print("   ✅ .env 파일 설정 완료")
    else:
        print("   ❌ .env 파일 없음")

if __name__ == "__main__":
    token = create_bot_directly()
    show_next_steps()
    
    print(f"\n🎉 준비 완료!")
    print(f"샘플 토큰: {token}")
    print("실제 사용을 위해서는 BotFather에서 진짜 토큰을 받아야 합니다") 