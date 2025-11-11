#!/bin/bash

# Vercel 배포 상태 확인 스크립트

echo "🔍 Vercel 배포 상태 확인 중..."
echo ""

URL="https://gap-monitor.vercel.app"

echo "📋 배포 URL: $URL"
echo ""

# 메인 페이지 확인
echo "1. 메인 페이지 확인..."
MAIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$URL" 2>/dev/null)
if [ "$MAIN_STATUS" = "200" ]; then
    echo "   ✅ 메인 페이지: 정상 ($MAIN_STATUS)"
else
    echo "   ❌ 메인 페이지: 오류 ($MAIN_STATUS)"
fi

# API 확인
echo ""
echo "2. API 엔드포인트 확인..."
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$URL/api/gap/MONUSDT" 2>/dev/null)
if [ "$API_STATUS" = "200" ]; then
    echo "   ✅ API: 정상 ($API_STATUS)"
    echo ""
    echo "   📊 API 응답 샘플:"
    curl -s "$URL/api/gap/MONUSDT" | python3 -m json.tool 2>/dev/null | head -10 || echo "   (JSON 파싱 실패)"
else
    echo "   ❌ API: 오류 ($API_STATUS)"
    echo ""
    echo "   📋 에러 응답:"
    curl -s "$URL/api/gap/MONUSDT" | head -5
fi

echo ""
echo "💡 Vercel 대시보드에서 배포 상태를 확인하세요:"
echo "   https://vercel.com/dashboard"
echo ""
echo "🔄 재배포가 필요하면:"
echo "   git push origin main"

