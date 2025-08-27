#!/bin/bash

# Rootdata Hot Index 모니터 데몬 실행 스크립트
# 이 스크립트는 백그라운드에서 모니터를 실행하고, 노트북을 끄거나 커서를 끄도 계속 실행됩니다.

echo "🚀 Rootdata Hot Index 모니터 데몬 시작"
echo "======================================"

# 현재 디렉토리로 이동
cd "$(dirname "$0")"

# 이미 실행 중인 프로세스가 있는지 확인
if pgrep -f "rootdata_hot_index_monitor.py" > /dev/null; then
    echo "⚠️  이미 실행 중인 모니터가 있습니다."
    echo "현재 실행 중인 프로세스:"
    ps aux | grep rootdata_hot_index_monitor | grep -v grep
    echo ""
    echo "중지하려면: ./stop_rootdata_daemon.sh"
    echo "재시작하려면: ./restart_rootdata_daemon.sh"
    exit 1
fi

# Python 가상환경이 있다면 활성화
if [ -d "venv" ]; then
    echo "🐍 가상환경 활성화 중..."
    source venv/bin/activate
fi

# 필요한 패키지 설치 확인
echo "📦 필요한 패키지 확인 중..."
python3 -c "import requests, bs4, schedule, dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  필요한 패키지가 설치되지 않았습니다."
    echo "📥 패키지 설치 중..."
    pip3 install requests beautifulsoup4 schedule python-dotenv
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

# 백그라운드에서 모니터 실행
echo "🔄 백그라운드에서 모니터 실행 중..."
nohup python3 rootdata_hot_index_monitor.py > rootdata_background.log 2>&1 &

# 프로세스 ID 저장
echo $! > rootdata_monitor.pid

echo "✅ 모니터가 백그라운드에서 실행되었습니다!"
echo "📊 프로세스 ID: $(cat rootdata_monitor.pid)"
echo "📝 로그 파일: rootdata_background.log"
echo ""
echo "🔍 상태 확인: ./check_rootdata_status.sh"
echo "🛑 중지: ./stop_rootdata_daemon.sh"
echo "🔄 재시작: ./restart_rootdata_daemon.sh"
echo ""
echo "💡 이제 노트북을 끄거나 커서를 끄도 모니터가 계속 실행됩니다!" 