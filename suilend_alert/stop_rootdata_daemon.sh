#!/bin/bash

# Rootdata Hot Index 모니터 데몬 중지 스크립트

echo "🛑 Rootdata Hot Index 모니터 데몬 중지"
echo "====================================="

# 현재 디렉토리로 이동
cd "$(dirname "$0")"

# PID 파일 확인
if [ ! -f "rootdata_monitor.pid" ]; then
    echo "⚠️  PID 파일을 찾을 수 없습니다."
    echo "프로세스를 수동으로 찾아서 중지합니다..."
    
    # 프로세스 ID 찾기
    PID=$(pgrep -f "rootdata_hot_index_monitor.py")
    
    if [ -z "$PID" ]; then
        echo "❌ 실행 중인 모니터 프로세스를 찾을 수 없습니다."
        exit 1
    fi
else
    PID=$(cat rootdata_monitor.pid)
    echo "📊 프로세스 ID: $PID"
fi

# 프로세스가 실행 중인지 확인
if ! ps -p $PID > /dev/null 2>&1; then
    echo "⚠️  프로세스 $PID가 이미 종료되었습니다."
    rm -f rootdata_monitor.pid
    exit 0
fi

# 프로세스 중지
echo "🔄 프로세스 $PID 중지 중..."
kill $PID

# 프로세스가 완전히 종료될 때까지 대기
sleep 2

# 강제 종료가 필요한 경우
if ps -p $PID > /dev/null 2>&1; then
    echo "⚠️  프로세스가 응답하지 않습니다. 강제 종료 중..."
    kill -9 $PID
    sleep 1
fi

# 최종 확인
if ps -p $PID > /dev/null 2>&1; then
    echo "❌ 프로세스 중지에 실패했습니다."
    exit 1
else
    echo "✅ 프로세스가 성공적으로 중지되었습니다."
    rm -f rootdata_monitor.pid
    echo "🧹 PID 파일을 정리했습니다."
fi

echo ""
echo "💡 모니터를 다시 시작하려면: ./start_rootdata_daemon.sh" 