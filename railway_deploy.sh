#!/bin/bash

# Railway 배포 스크립트
# Railway 웹사이트에서 GitHub 저장소를 연결하면 자동 배포됩니다

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚂 Railway 배포 준비 확인..."
echo ""

# 필수 파일 확인
REQUIRED_FILES=(
    "railway.json"
    "railway.toml"
    "hyperliquid_binance_gap_server.py"
    "requirements_gap_monitor.txt"
    "templates/hyperliquid_binance_gap_dashboard.html"
)

MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$SCRIPT_DIR/$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo "❌ 다음 파일들이 없습니다:"
    for file in "${MISSING_FILES[@]}"; do
        echo "   - $file"
    done
    exit 1
fi

echo "✅ 모든 필수 파일이 있습니다!"
echo ""

# GitHub 저장소 확인
GIT_REMOTE=$(git remote get-url origin 2>/dev/null)
if [ -z "$GIT_REMOTE" ]; then
    echo "❌ GitHub 저장소가 설정되지 않았습니다."
    exit 1
fi

echo "✅ GitHub 저장소: $GIT_REMOTE"
echo ""

# Railway CLI 확인
if command -v railway &> /dev/null; then
    echo "✅ Railway CLI 설치됨"
    echo ""
    echo "🚀 Railway CLI로 배포하려면:"
    echo "   railway login"
    echo "   railway init"
    echo "   railway up"
    echo ""
else
    echo "ℹ️  Railway CLI가 설치되지 않았습니다."
    echo ""
fi

echo "🌐 Railway 웹사이트에서 배포:"
echo "   1. https://railway.app 접속"
echo "   2. 'Start a New Project' 클릭"
echo "   3. 'Deploy from GitHub repo' 선택"
echo "   4. 저장소 선택: OzarkCrypto/xpl-price-monitor"
echo "   5. 자동 배포!"
echo ""
echo "✅ 배포 준비 완료!"

