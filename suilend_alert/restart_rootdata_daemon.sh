#!/bin/bash

# Rootdata Hot Index 모니터 데몬 재시작 스크립트

echo "🔄 Rootdata Hot Index 모니터 데몬 재시작"
echo "======================================"

# 현재 디렉토리로 이동
cd "$(dirname "$0")"

echo "1️⃣ 기존 모니터 중지 중..."
if [ -f "stop_rootdata_daemon.sh" ]; then
    ./stop_rootdata_daemon.sh
else
    echo "⚠️  중지 스크립트를 찾을 수 없습니다. 수동으로 중지합니다..."
    
    # 프로세스 ID 찾기
    PID=$(pgrep -f "rootdata_hot_index_monitor.py")
    
    if [ ! -z "$PID" ]; then
        echo "🔄 프로세스 $PID 중지 중..."
        kill $PID
        sleep 2
        
        # 강제 종료가 필요한 경우
        if ps -p $PID > /dev/null 2>&1; then
            echo "⚠️  프로세스가 응답하지 않습니다. 강제 종료 중..."
            kill -9 $PID
            sleep 1
        fi
        
        echo "✅ 기존 프로세스가 중지되었습니다."
    else
        echo "ℹ️  실행 중인 프로세스가 없습니다."
    fi
fi

echo ""
echo "2️⃣ 새 모니터 시작 중..."
if [ -f "start_rootdata_daemon.sh" ]; then
    ./start_rootdata_daemon.sh
else
    echo "⚠️  시작 스크립트를 찾을 수 없습니다. 수동으로 시작합니다..."
    
    # 백그라운드에서 모니터 실행
    echo "🔄 백그라운드에서 모니터 실행 중..."
    nohup python3 rootdata_hot_index_monitor.py > rootdata_background.log 2>&1 &
    
    # 프로세스 ID 저장
    echo $! > rootdata_monitor.pid
    
    echo "✅ 모니터가 백그라운드에서 실행되었습니다!"
    echo "📊 프로세스 ID: $(cat rootdata_monitor.pid)"
fi

echo ""
echo "3️⃣ 상태 확인 중..."
sleep 2

if [ -f "check_rootdata_status.sh" ]; then
    ./check_rootdata_status.sh
else
    echo "📊 프로세스 상태:"
    if pgrep -f "rootdata_hot_index_monitor.py" > /dev/null; then
        echo "✅ 모니터가 성공적으로 재시작되었습니다!"
        ps aux | grep rootdata_hot_index_monitor | grep -v grep
    else
        echo "❌ 모니터 재시작에 실패했습니다."
    fi
fi

echo ""
echo "🎉 재시작 완료!"
echo "💡 이제 노트북을 끄거나 커서를 끄도 모니터가 계속 실행됩니다!" 