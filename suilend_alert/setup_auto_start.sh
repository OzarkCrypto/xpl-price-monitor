#!/bin/bash

# RootData Hot Index 모니터 자동 시작 설정 스크립트

echo "🚀 RootData Hot Index 모니터 자동 시작 설정"
echo "=========================================="

# 현재 디렉토리 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_FILE="com.chasanghun.rootdata-monitor.plist"
PLIST_PATH="$SCRIPT_DIR/$PLIST_FILE"

# plist 파일이 존재하는지 확인
if [ ! -f "$PLIST_PATH" ]; then
    echo "❌ plist 파일을 찾을 수 없습니다: $PLIST_PATH"
    exit 1
fi

echo "📁 스크립트 디렉토리: $SCRIPT_DIR"
echo "📄 plist 파일: $PLIST_PATH"

# LaunchAgents 디렉토리로 복사
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
TARGET_PLIST="$LAUNCH_AGENTS_DIR/$PLIST_FILE"

echo "📂 LaunchAgents 디렉토리: $LAUNCH_AGENTS_DIR"

# LaunchAgents 디렉토리가 없으면 생성
if [ ! -d "$LAUNCH_AGENTS_DIR" ]; then
    echo "📁 LaunchAgents 디렉토리 생성 중..."
    mkdir -p "$LAUNCH_AGENTS_DIR"
fi

# plist 파일을 LaunchAgents로 복사
echo "📋 plist 파일을 LaunchAgents로 복사 중..."
cp "$PLIST_PATH" "$TARGET_PLIST"

# 파일 권한 설정
echo "🔐 파일 권한 설정 중..."
chmod 644 "$TARGET_PLIST"

# launchd에 서비스 등록
echo "🔧 launchd에 서비스 등록 중..."
launchctl load "$TARGET_PLIST"

if [ $? -eq 0 ]; then
    echo "✅ 자동 시작 설정 완료!"
    echo ""
    echo "📋 설정된 내용:"
    echo "  - 서비스명: com.chasanghun.rootdata-monitor"
    echo "  - 실행 스크립트: $SCRIPT_DIR/start_rootdata_daemon.sh"
    echo "  - 로그 파일: $SCRIPT_DIR/rootdata_launchd.log"
    echo "  - 오류 로그: $SCRIPT_DIR/rootdata_launchd_error.log"
    echo ""
    echo "🔄 이제 재부팅 후에도 자동으로 실행됩니다!"
    echo ""
    echo "🔧 유용한 명령어:"
    echo "  서비스 상태 확인: launchctl list | grep rootdata"
    echo "  서비스 중지: launchctl unload $TARGET_PLIST"
    echo "  서비스 시작: launchctl load $TARGET_PLIST"
    echo "  로그 확인: tail -f $SCRIPT_DIR/rootdata_launchd.log"
else
    echo "❌ 서비스 등록 실패!"
    echo "💡 수동으로 등록하려면:"
    echo "  launchctl load $TARGET_PLIST"
fi 