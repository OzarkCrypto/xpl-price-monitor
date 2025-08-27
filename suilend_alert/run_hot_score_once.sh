#!/bin/bash

# Rootdata Hot Score 모니터 한 번 실행 스크립트

# 스크립트 디렉토리로 이동
cd "$(dirname "$0")"

# 가상환경 활성화 (있는 경우)
if [ -d "venv" ]; then
    echo "가상환경 활성화 중..."
    source venv/bin/activate
fi

# 환경 변수 파일 확인
if [ ! -f ".env" ]; then
    echo "❌ .env 파일을 찾을 수 없습니다."
    echo "📝 env_template.txt를 참고하여 .env 파일을 생성하세요."
    exit 1
fi

# 필요한 패키지 설치 확인
echo "필요한 패키지 설치 확인 중..."
pip install -r requirements.txt

# 모니터 한 번 실행
echo "🔥 Rootdata Hot Score 모니터 한 번 실행..."
python rootdata_hot_score_monitor.py --once

echo "✅ 모니터 실행 완료." 