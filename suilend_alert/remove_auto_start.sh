#!/bin/bash

# RootData Hot Index 모니터 자동 시작 해제 스크립트

echo "🛑 RootData Hot Index 모니터 자동 시작 해제"
echo "=========================================="

# 서비스명
SERVICE_NAME="com.chasanghun.rootdata-monitor"
PLIST_FILE="com.chasanghun.rootdata-monitor.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
TARGET_PLIST="$LAUNCH_AGENTS_DIR/$PLIST_FILE"

echo "🔍 서비스 상태 확인 중..."
launchctl list | grep "$SERVICE_NAME"

if [ $? -eq 0 ]; then
    echo "✅ 서비스가 실행 중입니다."
    
    # 서비스 중지
    echo "🛑 서비스 중지 중..."
    launchctl unload "$TARGET_PLIST"
    
    if [ $? -eq 0 ]; then
        echo "✅ 서비스가 중지되었습니다."
    else
        echo "❌ 서비스 중지 실패!"
    fi
else
    echo "ℹ️ 서비스가 실행 중이 아닙니다."
fi

# plist 파일 제거
if [ -f "$TARGET_PLIST" ]; then
    echo "🗑️ plist 파일 제거 중..."
    rm "$TARGET_PLIST"
    
    if [ $? -eq 0 ]; then
        echo "✅ plist 파일이 제거되었습니다."
    else
        echo "❌ plist 파일 제거 실패!"
    fi
else
    echo "ℹ️ plist 파일이 존재하지 않습니다."
fi

echo ""
echo "🎯 자동 시작 설정이 해제되었습니다."
echo "💡 이제 재부팅 후에도 자동으로 실행되지 않습니다."
echo ""
echo "🔧 수동으로 모니터를 시작하려면:"
echo "  ./start_rootdata_daemon.sh" 