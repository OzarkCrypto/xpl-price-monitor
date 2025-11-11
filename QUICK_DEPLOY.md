# 🚀 빠른 배포 가이드

다른 사람들도 접속할 수 있는 공개 웹사이트를 만드는 가장 쉬운 방법입니다.

## 방법 1: Render (추천 - 가장 쉬운 방법)

### 단계별 가이드

1. **Render 접속**: https://render.com
2. **계정 생성**: GitHub로 로그인
3. **New Web Service 클릭**
4. **GitHub 저장소 연결**: `OzarkCrypto/xpl-price-monitor`
5. **설정 입력**:
   - Name: `gap-monitor`
   - Build Command: `pip install -r requirements_gap_monitor.txt`
   - Start Command: `python3 hyperliquid_binance_gap_server.py`
   - Plan: `Free`
6. **Create Web Service 클릭**
7. **완료!** 약 2-3분 후 공개 URL 생성

**결과**: `https://gap-monitor.onrender.com` (예시)

---

## 방법 2: Railway (더 간단)

1. **Railway 접속**: https://railway.app
2. **New Project 클릭**
3. **Deploy from GitHub repo 선택**
4. **저장소 선택**: `OzarkCrypto/xpl-price-monitor`
5. **자동 배포!** (설정 파일 자동 인식)

**결과**: `https://gap-monitor.up.railway.app` (예시)

---

## 방법 3: Vercel (서버리스)

⚠️ 주의: Flask 앱은 Vercel에서 서버리스 함수로 변환 필요

---

## 🎯 추천: Render 사용

Render가 가장 간단하고 Flask 앱에 적합합니다.

### 배포 후 확인사항

✅ 공개 URL 생성 확인
✅ 대시보드 접속 테스트
✅ API 엔드포인트 테스트: `https://your-app.onrender.com/api/gap/MONUSDT`

### 자동 재배포

GitHub에 푸시하면 자동으로 재배포됩니다:
```bash
git push origin main
```

---

## 📱 공유하기

배포 완료 후:
1. 공개 URL 복사
2. 다른 사람들과 공유
3. 인터넷 어디서나 접속 가능!

---

## 💰 비용

모든 방법이 **무료 플랜** 제공:
- Render: 무료 (슬립 모드 있음)
- Railway: 무료 크레딧 제공
- Vercel: 무료 (서버리스)

---

## 🆘 도움이 필요하면

자세한 내용은 `DEPLOY_RENDER.md` 참고

