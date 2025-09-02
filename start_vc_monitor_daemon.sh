#!/bin/bash

# VC Investment Monitor Bot 데몬 시작 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/vc_monitor.pid"
LOG_FILE="$SCRIPT_DIR/vc_monitor_daemon.log"

echo "🚀 VC 투자 모니터링 봇 데몬 시작..."

# 이미 실행 중인지 확인
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "❌ 봇이 이미 실행 중입니다. (PID: $PID)"
        exit 1
    else
        echo "🧹 이전 PID 파일 정리 중..."
        rm -f "$PID_FILE"
    fi
fi

# 의존성 설치
echo "📦 의존성 설치 중..."
pip3 install -r requirements_vc_monitor.txt

# 백그라운드에서 봇 실행
echo "🤖 VC 모니터링 봇을 백그라운드에서 실행 중..."
nohup python3 "$SCRIPT_DIR/vc_monitor_enhanced.py" > "$LOG_FILE" 2>&1 &

# PID 저장
echo $! > "$PID_FILE"
echo "✅ 봇이 백그라운드에서 실행되었습니다. (PID: $!)"
echo "📋 로그 파일: $LOG_FILE"
echo "🆔 PID 파일: $PID_FILE"

# 상태 확인
sleep 2
if ps -p $! > /dev/null 2>&1; then
    echo "✅ 봇이 성공적으로 시작되었습니다."
else
    echo "❌ 봇 시작에 실패했습니다. 로그를 확인해주세요."
    rm -f "$PID_FILE"
    exit 1
fi










