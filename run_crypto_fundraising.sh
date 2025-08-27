#!/bin/bash

# Crypto Fundraising Monitor 실행 스크립트

# 스크립트 디렉토리로 이동
cd "$(dirname "$0")"

# 가상환경 활성화 (있는 경우)
if [ -d "venv" ]; then
    echo "가상환경 활성화 중..."
    source venv/bin/activate
fi

# 의존성 확인
if ! python -c "import requests, bs4, pydantic, dotenv" 2>/dev/null; then
    echo "필요한 의존성이 설치되지 않았습니다."
    echo "다음 명령어로 설치하세요:"
    echo "pip install -r requirements_crypto_fundraising.txt"
    exit 1
fi

# 환경변수 파일 확인
if [ ! -f ".env" ]; then
    echo "경고: .env 파일이 없습니다."
    echo "env_template.txt를 .env로 복사하고 설정하세요."
    echo "cp env_template.txt .env"
    echo ""
    echo "필수 설정:"
    echo "- TELEGRAM_BOT_TOKEN"
    echo "- TELEGRAM_CHAT_ID"
    echo ""
fi

# 모니터 실행
echo "Crypto Fundraising Monitor 실행 중..."
python crypto_fundraising_monitor/run.py

# 실행 결과 확인
if [ $? -eq 0 ]; then
    echo "✅ 모니터링이 성공적으로 완료되었습니다."
else
    echo "❌ 모니터링 실행 중 오류가 발생했습니다."
    echo "로그 파일을 확인하세요: crypto_fundraising_monitor.log"
    exit 1
fi 