#!/bin/bash

echo "🚀 XPL 가격 모니터 시작..."
echo "📦 필요한 패키지 설치 중..."

# 가상환경이 있다면 활성화
if [ -d "venv" ]; then
    echo "🔧 가상환경 활성화..."
    source venv/bin/activate
fi

# 패키지 설치
pip install -r requirements_xpl_monitor.txt

echo "✅ 패키지 설치 완료"
echo "🌐 웹 서버 시작 중..."

# XPL 모니터 실행
python3 xpl_price_monitor.py
