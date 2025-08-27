#!/bin/bash

# Rootdata Hot Index 모니터 실행 스크립트

echo "🔥 Rootdata Hot Index 모니터 시작"
echo "=================================="

# 현재 디렉토리로 이동
cd "$(dirname "$0")"

# Python 가상환경이 있다면 활성화
if [ -d "venv" ]; then
    echo "🐍 가상환경 활성화 중..."
    source venv/bin/activate
fi

# 필요한 패키지 설치 확인
echo "📦 필요한 패키지 확인 중..."
python -c "import requests, beautifulsoup4, schedule, python-dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  필요한 패키지가 설치되지 않았습니다."
    echo "📥 패키지 설치 중..."
    pip install requests beautifulsoup4 schedule python-dotenv
fi

# 환경 변수 파일 확인
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다."
    echo "📝 env_template.txt를 참고하여 .env 파일을 생성하세요."
    echo "필요한 환경 변수:"
    echo "  - TELEGRAM_BOT_TOKEN"
    echo "  - TELEGRAM_CHAT_ID"
    exit 1
fi

# 모니터 실행
echo "🚀 Rootdata Hot Index 모니터 실행 중..."
echo "⏰ 1시간마다 TOP 10 업데이트 (매시간 정각)"
echo "🛑 중단하려면 Ctrl+C를 누르세요"
echo ""

python rootdata_hot_index_monitor.py

echo ""
echo "👋 모니터가 종료되었습니다." 