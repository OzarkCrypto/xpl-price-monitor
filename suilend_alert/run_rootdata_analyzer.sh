#!/bin/bash

# Rootdata 웹사이트 구조 분석기 실행 스크립트

echo "🔍 Rootdata 웹사이트 구조 분석기"
echo "================================"

# 현재 디렉토리로 이동
cd "$(dirname "$0")"

# Python 가상환경이 있다면 활성화
if [ -d "venv" ]; then
    echo "🐍 가상환경 활성화 중..."
    source venv/bin/activate
fi

# 필요한 패키지 설치 확인
echo "📦 필요한 패키지 확인 중..."
python -c "import requests, beautifulsoup4" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  필요한 패키지가 설치되지 않았습니다."
    echo "📥 패키지 설치 중..."
    pip install requests beautifulsoup4
fi

# 분석기 실행
echo "🚀 Rootdata 웹사이트 구조 분석 중..."
echo "📊 결과는 콘솔과 HTML 파일로 저장됩니다."
echo ""

python rootdata_analyzer.py

echo ""
echo "✅ 분석이 완료되었습니다."
echo "💡 HTML 소스 파일을 확인하여 실제 데이터 구조를 파악하세요." 