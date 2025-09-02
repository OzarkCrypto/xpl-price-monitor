#!/bin/bash

# VC Investment Monitor Bot 데몬 중지 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/vc_monitor.pid"

echo "🛑 VC 투자 모니터링 봇 데몬 중지..."

# PID 파일 확인
if [ ! -f "$PID_FILE" ]; then
    echo "❌ PID 파일을 찾을 수 없습니다. 봇이 실행 중이지 않을 수 있습니다."
    exit 1
fi

# PID 읽기
PID=$(cat "$PID_FILE")

# 프로세스 존재 확인
if ! ps -p $PID > /dev/null 2>&1; then
    echo "❌ PID $PID에 해당하는 프로세스가 없습니다."
    echo "🧹 PID 파일을 정리합니다."
    rm -f "$PID_FILE"
    exit 1
fi

# 프로세스 종료
echo "🔄 프로세스 $PID 종료 중..."
kill $PID

# 종료 대기
sleep 3

# 강제 종료 확인
if ps -p $PID > /dev/null 2>&1; then
    echo "⚠️ 프로세스가 응답하지 않습니다. 강제 종료합니다."
    kill -9 $PID
    sleep 1
fi

# 최종 확인
if ps -p $PID > /dev/null 2>&1; then
    echo "❌ 프로세스 종료에 실패했습니다."
    exit 1
else
    echo "✅ 봇이 성공적으로 중지되었습니다."
    rm -f "$PID_FILE"
fi










