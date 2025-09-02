#!/bin/bash

# VC Investment Monitor Bot 실행 스크립트

echo "🚀 VC 투자 모니터링 봇 시작..."

# Python 가상환경 활성화 (선택사항)
# source venv/bin/activate

# 의존성 설치 확인
echo "📦 의존성 확인 중..."
pip install -r requirements_vc_monitor.txt

# 봇 실행
echo "🤖 VC 모니터링 봇 실행 중..."
python3 vc_monitor_enhanced.py

echo "✅ 봇 실행 완료"










