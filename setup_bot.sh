#!/bin/bash
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
