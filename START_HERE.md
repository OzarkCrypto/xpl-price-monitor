# 🌐 공개 웹사이트 만들기 - 시작하기

다른 사람들도 접속할 수 있는 웹사이트를 만드는 **가장 쉬운 방법**입니다.

## ⚡ 5분 안에 완료하기

### 1단계: Render 접속 및 로그인
👉 https://render.com 접속
- GitHub 계정으로 로그인 (또는 이메일로 가입)

### 2단계: 새 서비스 생성
1. **"New +"** 버튼 클릭
2. **"Web Service"** 선택
3. **"Connect GitHub"** 클릭
4. 저장소 선택: **`OzarkCrypto/xpl-price-monitor`**

### 3단계: 설정 입력
다음 정보를 **정확히** 입력하세요:

```
Name: gap-monitor
Environment: Python 3
Build Command: pip install -r requirements_gap_monitor.txt
Start Command: python3 hyperliquid_binance_gap_server.py
Plan: Free
```

### 4단계: 배포 시작
- **"Create Web Service"** 버튼 클릭
- 약 2-3분 대기
- ✅ 완료!

## 🎉 배포 완료!

배포가 완료되면 다음과 같은 URL이 생성됩니다:
```
https://gap-monitor.onrender.com
```

이 URL을 복사해서 다른 사람들과 공유하세요!

## 📱 접속 테스트

브라우저에서 다음 주소로 접속해보세요:
- 메인 페이지: `https://gap-monitor.onrender.com`
- API 테스트: `https://gap-monitor.onrender.com/api/gap/MONUSDT`

## 🔄 자동 업데이트

앞으로 GitHub에 코드를 푸시하면 자동으로 웹사이트가 업데이트됩니다!

```bash
git push origin main
```

## 💡 팁

- **무료 플랜**: 완전 무료로 사용 가능
- **자동 HTTPS**: SSL 인증서 자동 설정
- **슬립 모드**: 15분간 요청이 없으면 서버가 잠들 수 있음 (첫 요청 시 깨어남)

## 🆘 문제가 있나요?

자세한 가이드: `DEPLOY_RENDER.md` 또는 `QUICK_DEPLOY.md` 참고

