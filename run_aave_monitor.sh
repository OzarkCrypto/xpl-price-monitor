#!/bin/bash

# Aave 거버넌스 모니터링 봇 실행 스크립트

echo "🚀 Aave 거버넌스 모니터링 봇 시작"
echo "=================================="

# Python 가상환경 확인 및 활성화
if [ -d "venv" ]; then
    echo "📦 가상환경 활성화 중..."
    source venv/bin/activate
else
    echo "📦 가상환경 생성 중..."
    python3 -m venv venv
    source venv/bin/activate
    
    echo "📦 필요한 패키지 설치 중..."
    pip install -r requirements_aave_monitor.txt
fi

# 모니터링 봇 실행
echo "🤖 모니터링 봇 실행 중..."
python3 aave_governance_monitor.py

echo "✅ 모니터링 봇 종료"


