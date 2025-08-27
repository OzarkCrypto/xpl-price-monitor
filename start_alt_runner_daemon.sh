#!/bin/bash

# 알트 러너 모니터링 봇을 백그라운드 데몬으로 실행

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/alt_runner_monitor.pid"
LOG_FILE="$SCRIPT_DIR/alt_runner_monitor.log"

echo "🚀 알트 러너 모니터링 봇 데몬 시작..."

# 이미 실행 중인지 확인
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  이미 실행 중입니다. PID: $PID"
        exit 1
    else
        echo "🧹 이전 PID 파일 정리 중..."
        rm -f "$PID_FILE"
    fi
fi

# 의존성 설치
echo "📦 의존성 패키지 설치 중..."
pip install -r requirements_alt_runner.txt

# 백그라운드에서 실행
echo "🤖 알트 러너 모니터링 봇을 백그라운드에서 실행 중..."
nohup python3 "$SCRIPT_DIR/alt_runner_monitor.py" > "$LOG_FILE" 2>&1 &

# PID 저장
echo $! > "$PID_FILE"
echo "✅ 데몬이 시작되었습니다. PID: $!"
echo "📋 PID 파일: $PID_FILE"
echo "📝 로그 파일: $LOG_FILE"
echo "🛑 중지하려면: ./stop_alt_runner_daemon.sh" 