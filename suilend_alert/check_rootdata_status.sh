#!/bin/bash

# Rootdata Hot Index 모니터 데몬 상태 확인 스크립트

echo "🔍 Rootdata Hot Index 모니터 데몬 상태 확인"
echo "========================================="

# 현재 디렉토리로 이동
cd "$(dirname "$0")"

# 프로세스 상태 확인
echo "📊 프로세스 상태:"
if pgrep -f "rootdata_hot_index_monitor.py" > /dev/null; then
    echo "✅ 모니터가 실행 중입니다!"
    
    # 프로세스 정보 출력
    echo ""
    echo "📋 프로세스 상세 정보:"
    ps aux | grep rootdata_hot_index_monitor | grep -v grep
    
    # PID 파일 확인
    if [ -f "rootdata_monitor.pid" ]; then
        PID=$(cat rootdata_monitor.pid)
        echo ""
        echo "📁 PID 파일: $PID"
        
        # PID 파일의 프로세스가 실제로 실행 중인지 확인
        if ps -p $PID > /dev/null 2>&1; then
            echo "✅ PID 파일과 실제 프로세스가 일치합니다."
        else
            echo "⚠️  PID 파일과 실제 프로세스가 일치하지 않습니다."
            echo "PID 파일을 정리하는 것을 권장합니다."
        fi
    else
        echo "⚠️  PID 파일이 없습니다."
    fi
    
    # 로그 파일 확인
    if [ -f "rootdata_background.log" ]; then
        echo ""
        echo "📝 로그 파일 정보:"
        echo "   파일: rootdata_background.log"
        echo "   크기: $(du -h rootdata_background.log | cut -f1)"
        echo "   최종 수정: $(stat -f "%Sm" rootdata_background.log)"
        
        echo ""
        echo "📖 최근 로그 (마지막 10줄):"
        tail -10 rootdata_background.log
    else
        echo "⚠️  로그 파일이 없습니다."
    fi
    
else
    echo "❌ 모니터가 실행 중이 아닙니다."
    
    # PID 파일 확인
    if [ -f "rootdata_monitor.pid" ]; then
        echo "⚠️  PID 파일이 남아있지만 프로세스가 실행되지 않습니다."
        echo "PID 파일을 정리하는 것을 권장합니다."
    fi
    
    echo ""
    echo "💡 모니터를 시작하려면: ./start_rootdata_daemon.sh"
fi

echo ""
echo "🔧 유용한 명령어:"
echo "  시작: ./start_rootdata_daemon.sh"
echo "  중지: ./stop_rootdata_daemon.sh"
echo "  재시작: ./restart_rootdata_daemon.sh"
echo "  로그 실시간 확인: tail -f rootdata_background.log" 