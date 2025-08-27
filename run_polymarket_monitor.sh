#!/bin/bash

# 폴리마켓 모니터 실행 스크립트

echo "=== 폴리마켓 신규 마켓 모니터 시작 ==="

# 현재 디렉토리 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Python 가상환경 활성화 (있는 경우)
if [ -d "venv" ]; then
    echo "가상환경 활성화 중..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "가상환경 활성화 중..."
    source .venv/bin/activate
fi

# 환경 변수 파일 확인
if [ ! -f ".env" ]; then
    echo "경고: .env 파일이 없습니다."
    echo "템플릿을 복사하여 설정하세요: cp .env.template .env"
    echo "텔레그램 봇 토큰과 채팅 ID를 설정해야 합니다."
fi

# 필요한 Python 패키지 확인
echo "필요한 패키지 확인 중..."
python3 -c "import requests, json, logging" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "필요한 패키지를 설치합니다..."
    pip3 install requests
fi

# 설정 파일 생성 (없는 경우)
if [ ! -f "polymarket_config.json" ]; then
    echo "기본 설정 파일을 생성합니다..."
    python3 polymarket_config.py
fi

# 모니터링 시작
echo "폴리마켓 모니터링을 시작합니다..."
echo "중단하려면 Ctrl+C를 누르세요."
echo ""

python3 polymarket_monitor.py

echo ""
echo "=== 폴리마켓 모니터 종료 ===" 