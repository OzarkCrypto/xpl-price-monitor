#!/bin/bash

# 알트 러너 모니터링 봇 실행 스크립트

echo "🚀 알트 러너 모니터링 봇 시작..."

# Python 가상환경 활성화 (선택사항)
# source venv/bin/activate

# 의존성 설치
echo "📦 의존성 패키지 설치 중..."
pip install -r requirements_alt_runner.txt

# 모니터링 봇 실행
echo "🤖 알트 러너 모니터링 봇 실행 중..."
python3 alt_runner_monitor.py

echo "✅ 모니터링 봇 실행 완료" 