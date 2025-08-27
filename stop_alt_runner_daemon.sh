#!/bin/bash

# 알트 러너 모니터링 봇 데몬 중지

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/alt_runner_monitor.pid"

echo "🛑 알트 러너 모니터링 봇 데몬 중지..."

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "🔄 PID $PID 프로세스 종료 중..."
        kill $PID
        
        # 프로세스가 완전히 종료될 때까지 대기
        sleep 2
        
        if ps -p $PID > /dev/null 2>&1; then
            echo "⚠️  강제 종료 중..."
            kill -9 $PID
        fi
        
        echo "✅ 데몬이 중지되었습니다."
        rm -f "$PID_FILE"
    else
        echo "⚠️  PID $PID 프로세스가 실행 중이 아닙니다."
        rm -f "$PID_FILE"
    fi
else
    echo "⚠️  PID 파일을 찾을 수 없습니다."
fi 