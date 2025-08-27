#!/bin/bash

# RootData Hot Index 모니터 정각 실행 Cron 설정 스크립트

echo "🕐 RootData Hot Index 모니터 정각 실행 Cron 설정"
echo "=============================================="

# 현재 디렉토리 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITOR_SCRIPT="$SCRIPT_DIR/rootdata_hot_index_monitor.py"
PYTHON_PATH=$(which python3)

echo "📁 스크립트 디렉토리: $SCRIPT_DIR"
echo "🐍 Python 경로: $PYTHON_PATH"
echo "📄 모니터 스크립트: $MONITOR_SCRIPT"

# 스크립트 실행 권한 확인
if [ ! -x "$MONITOR_SCRIPT" ]; then
    echo "🔐 스크립트 실행 권한 설정 중..."
    chmod +x "$MONITOR_SCRIPT"
fi

# 현재 cron 작업 확인
echo "🔍 현재 cron 작업 확인 중..."
crontab -l 2>/dev/null | grep -i rootdata || echo "  기존 rootdata cron 작업 없음"

# 새로운 cron 작업 생성
CRON_JOB="0 * * * * cd $SCRIPT_DIR && $PYTHON_PATH $MONITOR_SCRIPT --once >> $SCRIPT_DIR/rootdata_cron.log 2>&1"

echo ""
echo "📋 추가할 cron 작업:"
echo "  $CRON_JOB"
echo ""

# 사용자 확인
read -p "이 cron 작업을 추가하시겠습니까? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 기존 cron 작업 백업
    echo "💾 기존 cron 작업 백업 중..."
    crontab -l 2>/dev/null > /tmp/rootdata_cron_backup.txt
    
    # 새로운 cron 작업 추가
    echo "➕ 새로운 cron 작업 추가 중..."
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    
    if [ $? -eq 0 ]; then
        echo "✅ Cron 작업 추가 완료!"
        echo ""
        echo "📋 설정된 내용:"
        echo "  - 실행 시간: 매시간 정각 (0분)"
        echo "  - 실행 명령: $PYTHON_PATH $MONITOR_SCRIPT --once"
        echo "  - 로그 파일: $SCRIPT_DIR/rootdata_cron.log"
        echo "  - 작업 디렉토리: $SCRIPT_DIR"
        echo ""
        echo "🔄 이제 매시간 정각에 자동으로 실행됩니다!"
        echo ""
        echo "🔧 유용한 명령어:"
        echo "  cron 작업 확인: crontab -l"
        echo "  cron 작업 편집: crontab -e"
        echo "  cron 작업 제거: crontab -r"
        echo "  로그 확인: tail -f $SCRIPT_DIR/rootdata_cron.log"
        echo ""
        echo "💡 백업 파일: /tmp/rootdata_cron_backup.txt"
    else
        echo "❌ Cron 작업 추가 실패!"
        echo "💡 수동으로 추가하려면:"
        echo "  crontab -e"
        echo "  그리고 다음 줄 추가:"
        echo "  $CRON_JOB"
    fi
else
    echo "❌ Cron 작업 추가가 취소되었습니다."
fi 