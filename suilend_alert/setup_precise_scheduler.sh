#!/bin/bash

# RootData Hot Index 정확한 정각 실행 스케줄러 설정

echo "🕐 RootData Hot Index 정확한 정각 실행 스케줄러 설정"
echo "=================================================="

# 현재 디렉토리 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCHEDULER_SCRIPT="$SCRIPT_DIR/rootdata_precise_scheduler.py"
PYTHON_PATH=$(which python3)

echo "📁 스크립트 디렉토리: $SCRIPT_DIR"
echo "🐍 Python 경로: $PYTHON_PATH"
echo "📄 스케줄러 스크립트: $SCHEDULER_SCRIPT"

# 스크립트 실행 권한 확인
if [ ! -x "$SCHEDULER_SCRIPT" ]; then
    echo "🔐 스케줄러 스크립트 실행 권한 설정 중..."
    chmod +x "$SCHEDULER_SCRIPT"
fi

# 현재 실행 중인 프로세스 확인
echo "🔍 현재 실행 중인 프로세스 확인 중..."
ps aux | grep -E "(rootdata_precise_scheduler|rootdata_hot_index_monitor)" | grep -v grep

echo ""
echo "📋 설정 옵션:"
echo "  1. 정확한 정각 실행 스케줄러 시작 (권장)"
echo "  2. 기존 모니터링 중지"
echo "  3. 상태 확인"
echo "  4. 종료"

read -p "선택하세요 (1-4): " choice

case $choice in
    1)
        echo "🚀 정확한 정각 실행 스케줄러 시작 중..."
        
        # 백그라운드에서 실행
        nohup $PYTHON_PATH "$SCHEDULER_SCRIPT" > "$SCRIPT_DIR/rootdata_precise_scheduler.log" 2>&1 &
        SCHEDULER_PID=$!
        
        echo "✅ 스케줄러가 백그라운드에서 시작되었습니다 (PID: $SCHEDULER_PID)"
        echo "📝 로그 파일: $SCRIPT_DIR/rootdata_precise_scheduler.log"
        echo ""
        echo "🕐 이제 매시간 정각에 정확하게 실행됩니다!"
        echo "💡 다음 실행 시간을 확인하려면 로그를 확인하세요."
        ;;
        
    2)
        echo "🛑 기존 모니터링 중지 중..."
        
        # 실행 중인 프로세스 찾기 및 종료
        PIDS=$(ps aux | grep -E "(rootdata_precise_scheduler|rootdata_hot_index_monitor)" | grep -v grep | awk '{print $2}')
        
        if [ -n "$PIDS" ]; then
            echo "발견된 프로세스: $PIDS"
            for pid in $PIDS; do
                echo "프로세스 $pid 종료 중..."
                kill $pid
            done
            echo "✅ 모든 모니터링 프로세스가 종료되었습니다."
        else
            echo "ℹ️ 실행 중인 모니터링 프로세스가 없습니다."
        fi
        ;;
        
    3)
        echo "📊 현재 상태 확인 중..."
        
        # 실행 중인 프로세스
        echo "🔍 실행 중인 프로세스:"
        ps aux | grep -E "(rootdata_precise_scheduler|rootdata_hot_index_monitor)" | grep -v grep || echo "  실행 중인 프로세스 없음"
        
        # 로그 파일 확인
        echo ""
        echo "📝 로그 파일 상태:"
        if [ -f "$SCRIPT_DIR/rootdata_precise_scheduler.log" ]; then
            echo "  스케줄러 로그: $(ls -la "$SCRIPT_DIR/rootdata_precise_scheduler.log")"
            echo "  최근 로그 (마지막 5줄):"
            tail -5 "$SCRIPT_DIR/rootdata_precise_scheduler.log" 2>/dev/null || echo "    로그 파일 읽기 실패"
        else
            echo "  스케줄러 로그: 파일 없음"
        fi
        
        if [ -f "$SCRIPT_DIR/rootdata_hot_index.log" ]; then
            echo "  모니터 로그: $(ls -la "$SCRIPT_DIR/rootdata_hot_index.log")"
        else
            echo "  모니터 로그: 파일 없음"
        fi
        ;;
        
    4)
        echo "👋 종료합니다."
        exit 0
        ;;
        
    *)
        echo "❌ 잘못된 선택입니다."
        exit 1
        ;;
esac

echo ""
echo "🔧 유용한 명령어:"
echo "  스케줄러 시작: $PYTHON_PATH $SCHEDULER_SCRIPT"
echo "  로그 확인: tail -f $SCRIPT_DIR/rootdata_precise_scheduler.log"
echo "  프로세스 확인: ps aux | grep rootdata"
echo "  스케줄러 중지: pkill -f rootdata_precise_scheduler" 