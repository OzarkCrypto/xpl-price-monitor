# 🚀 지금 바로 배포하기

이 가이드를 따라하면 **5분 안에** 공개 웹사이트가 만들어집니다!

## 방법 1: Render (가장 쉬운 방법) ⭐

### 단계별 가이드

1. **Render 접속**
   - https://render.com 접속
   - "Get Started for Free" 클릭

2. **GitHub로 로그인**
   - "Continue with GitHub" 클릭
   - GitHub 계정으로 로그인

3. **새 Web Service 생성**
   - 대시보드에서 **"New +"** 버튼 클릭
   - **"Web Service"** 선택

4. **GitHub 저장소 연결**
   - "Connect GitHub" 클릭 (처음이면 GitHub 연결)
   - 저장소 선택: **`OzarkCrypto/xpl-price-monitor`**

5. **설정 입력** (아래 내용을 정확히 복사해서 붙여넣기)
   ```
   Name: gap-monitor
   Environment: Python 3
   Build Command: pip install -r requirements_gap_monitor.txt
   Start Command: python3 hyperliquid_binance_gap_server.py
   Plan: Free
   ```

6. **배포 시작**
   - "Create Web Service" 버튼 클릭
   - 약 2-3분 대기

7. **완료!** 🎉
   - 배포 완료 후 공개 URL이 표시됩니다
   - 예: `https://gap-monitor.onrender.com`

---

## 방법 2: Railway (더 빠름)

1. **Railway 접속**
   - https://railway.app 접속
   - "Start a New Project" 클릭

2. **GitHub로 로그인**
   - "Deploy from GitHub repo" 선택
   - GitHub 계정으로 로그인

3. **저장소 선택**
   - `OzarkCrypto/xpl-price-monitor` 선택

4. **자동 배포!**
   - Railway가 자동으로 설정 파일을 인식합니다
   - 약 2-3분 후 배포 완료

5. **URL 확인**
   - 배포 완료 후 공개 URL 확인
   - 예: `https://gap-monitor.up.railway.app`

---

## 🎯 추천: Render 사용

Render가 가장 간단하고 안정적입니다!

### 배포 후 확인사항

✅ 공개 URL 생성 확인
✅ 대시보드 접속 테스트
✅ API 테스트: `https://your-app.onrender.com/api/gap/MONUSDT`

### 자동 재배포

앞으로 GitHub에 코드를 푸시하면 자동으로 재배포됩니다:
```bash
git push origin main
```

---

## 💡 팁

- **무료 플랜**: 완전 무료로 사용 가능
- **자동 HTTPS**: SSL 인증서 자동 설정
- **슬립 모드**: 15분간 요청이 없으면 서버가 잠들 수 있음 (첫 요청 시 약 30초 소요)

---

## 🆘 문제 해결

### 배포 실패 시

1. **로그 확인**: Render/Railway 대시보드 → "Logs" 탭
2. **의존성 확인**: `requirements_gap_monitor.txt` 확인
3. **포트 확인**: 서버가 `PORT` 환경 변수를 사용하는지 확인

### 서버가 응답하지 않는 경우

1. **슬립 모드**: 첫 요청 시 30초 정도 대기
2. **재배포**: "Manual Deploy" → "Deploy latest commit"

---

## 📱 공유하기

배포 완료 후:
1. 공개 URL 복사
2. 다른 사람들과 공유
3. 인터넷 어디서나 접속 가능!

---

**지금 바로 시작하세요!** 👉 https://render.com

