#!/bin/bash

# Suilend LTV 모니터링 봇 실행 스크립트

echo "🚀 Suilend LTV 모니터링 봇 시작"
echo "=================================="

# Python 가상환경 확인 및 활성화
if [ -d "venv" ]; then
    echo "📦 가상환경 활성화 중..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "📦 가상환경 활성화 중..."
    source .venv/bin/activate
fi

# 의존성 설치 확인
echo "🔍 의존성 확인 중..."
if ! python -c "import requests, schedule, dotenv" 2>/dev/null; then
    echo "📦 필요한 패키지 설치 중..."
    pip install -r requirements.txt
fi

# 환경 변수 파일 확인
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다."
    echo "📝 env_template.txt를 참고하여 .env 파일을 생성하세요."
    echo ""
    echo "필요한 환경 변수:"
    echo "  - TELEGRAM_BOT_TOKEN: 텔레그램 봇 토큰"
    echo "  - TELEGRAM_CHAT_ID: 텔레그램 채팅 ID"
    echo "  - PHONE_NUMBER: 전화번호 (선택사항)"
    echo "  - MONITORING_INTERVAL: 모니터링 간격 (분)"
    exit 1
fi

# 설정 확인
echo "🔧 설정 확인 중..."
python config.py

# 모니터링 봇 실행
echo ""
echo "🔄 모니터링 봇 실행 중..."
echo "중단하려면 Ctrl+C를 누르세요."
echo ""

python suilend_ltv_monitor.py 