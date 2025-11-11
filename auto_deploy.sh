#!/bin/bash

# 자동 배포 스크립트
# Railway CLI를 사용하여 자동 배포

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 자동 배포 시작..."
echo ""

# Railway CLI 설치 확인
if ! command -v railway &> /dev/null; then
    echo "📦 Railway CLI 설치 중..."
    
    # 사용자 디렉토리에 설치
    INSTALL_DIR="$HOME/.local/bin"
    mkdir -p "$INSTALL_DIR"
    
    # Railway CLI 다운로드 및 설치
    if [[ "$OSTYPE" == "darwin"* ]]; then
        ARCH=$(uname -m)
        if [ "$ARCH" == "arm64" ]; then
            RAILWAY_URL="https://github.com/railwayapp/cli/releases/latest/download/railway-darwin-arm64"
        else
            RAILWAY_URL="https://github.com/railwayapp/cli/releases/latest/download/railway-darwin-amd64"
        fi
    else
        RAILWAY_URL="https://github.com/railwayapp/cli/releases/latest/download/railway-linux-amd64"
    fi
    
    curl -L -o "$INSTALL_DIR/railway" "$RAILWAY_URL"
    chmod +x "$INSTALL_DIR/railway"
    
    # PATH에 추가
    export PATH="$INSTALL_DIR:$PATH"
    
    echo "✅ Railway CLI 설치 완료"
    echo ""
fi

# Railway 로그인 확인
if ! railway whoami &> /dev/null; then
    echo "🔐 Railway 로그인이 필요합니다..."
    echo "브라우저가 열리면 로그인해주세요."
    railway login
fi

echo "📋 현재 프로젝트 확인..."
cd "$SCRIPT_DIR"

# Railway 프로젝트 초기화 또는 연결
if [ ! -f ".railway" ]; then
    echo "🆕 새 Railway 프로젝트 생성 중..."
    railway init
else
    echo "✅ 기존 Railway 프로젝트 사용"
fi

echo ""
echo "🚀 배포 시작..."
railway up

echo ""
echo "✅ 배포 완료!"
echo "📋 배포 URL 확인: railway domain"

