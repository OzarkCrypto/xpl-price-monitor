#!/bin/bash

# Aave 거버넌스 모니터링 봇 데몬 중지

echo "🛑 Aave 거버넌스 모니터링 봇 데몬 중지"
echo "======================================"

if [ -f "aave_monitor.pid" ]; then
    PID=$(cat aave_monitor.pid)
    
    if ps -p $PID > /dev/null; then
        echo "📋 프로세스 ID: $PID"
        echo "🔄 프로세스 종료 중..."
        
        kill $PID
        
        # 프로세스가 완전히 종료될 때까지 대기
        sleep 3
        
        if ps -p $PID > /dev/null; then
            echo "⚠️  프로세스가 종료되지 않았습니다. 강제 종료 중..."
            kill -9 $PID
        fi
        
        echo "✅ 프로세스가 종료되었습니다."
    else
        echo "⚠️  프로세스 ID $PID가 실행 중이 아닙니다."
    fi
    
    # PID 파일 삭제
    rm -f aave_monitor.pid
else
    echo "⚠️  PID 파일을 찾을 수 없습니다."
fi

echo "✅ 모니터링 봇 데몬 중지 완료"


