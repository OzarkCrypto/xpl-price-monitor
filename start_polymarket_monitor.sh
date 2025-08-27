#!/bin/bash

# 폴리마켓 모니터 시작 스크립트 (환경 변수 포함)

echo "🚀 폴리마켓 신규 마켓 모니터 시작"
echo "======================================"

# 환경 변수 설정
export TELEGRAM_BOT_TOKEN="7086607684:AAFEAN-E6XJJW77OfXs4tThEQyxOdi_t98w"
export TELEGRAM_CHAT_ID="1339285013"
export POLYMARKET_CHECK_INTERVAL="60"
export POLYMARKET_MAX_MARKETS="100"
export ENABLE_NEW_MARKET_ALERTS="true"
export ENABLE_MARKET_UPDATES="false"

echo "✅ 환경 변수 설정 완료"
echo "📡 텔레그램 봇 토큰: ${TELEGRAM_BOT_TOKEN:0:20}..."
echo "💬 채팅 ID: $TELEGRAM_CHAT_ID"
echo "⏱️  확인 간격: ${POLYMARKET_CHECK_INTERVAL}초"
echo ""

# 필요한 패키지 설치 확인
echo "📦 필요한 패키지 확인 중..."
python3 -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "requests 패키지를 설치합니다..."
    pip3 install requests
fi

# 설정 파일 존재 확인
if [ ! -f "polymarket_config.json" ]; then
    echo "⚙️  기본 설정 파일 생성 중..."
    python3 polymarket_config.py
fi

echo ""
echo "🔄 모니터링 시작..."
echo "중단하려면 Ctrl+C를 누르세요"
echo "======================================"

# 모니터링 시작
python3 polymarket_monitor.py