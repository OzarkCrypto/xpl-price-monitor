# Render 배포 가이드 (단계별)

이 가이드는 Render를 사용하여 Hyperliquid vs Binance 가격 갭 모니터를 공개 웹사이트로 배포하는 방법입니다.

## 🚀 빠른 배포 (5분 안에 완료)

### 1단계: Render 계정 생성

1. https://render.com 접속
2. "Get Started for Free" 클릭
3. GitHub 계정으로 로그인 (또는 이메일로 가입)

### 2단계: 새 Web Service 생성

1. Render 대시보드에서 **"New +"** 버튼 클릭
2. **"Web Service"** 선택
3. **"Connect GitHub"** 클릭 (처음이면 GitHub 연결)
4. 저장소 선택: `OzarkCrypto/xpl-price-monitor`

### 3단계: 서비스 설정

다음 정보를 입력하세요:

- **Name**: `gap-monitor` (또는 원하는 이름)
- **Region**: `Singapore` (또는 가장 가까운 지역)
- **Branch**: `main`
- **Root Directory**: (비워두기)
- **Environment**: `Python 3`
- **Build Command**: 
  ```
  pip install -r requirements_gap_monitor.txt
  ```
- **Start Command**: 
  ```
  python3 hyperliquid_binance_gap_server.py
  ```
- **Plan**: `Free` 선택

### 4단계: 환경 변수 설정 (선택사항)

"Environment" 섹션에서:
- `FLASK_DEBUG`: `False`
- `PORT`: 자동 설정됨 (수정 불필요)

### 5단계: 배포 시작

1. **"Create Web Service"** 버튼 클릭
2. 배포가 자동으로 시작됩니다 (약 2-3분 소요)
3. 배포 완료 후 공개 URL이 생성됩니다!

## 📋 배포 완료 후

배포가 완료되면 다음과 같은 URL이 제공됩니다:
```
https://gap-monitor.onrender.com
```

이 URL을 다른 사람들과 공유하세요!

## 🔄 자동 재배포

GitHub에 코드를 푸시하면 자동으로 재배포됩니다:
```bash
git add .
git commit -m "Update"
git push origin main
```

## ⚙️ 고급 설정

### 커스텀 도메인 연결

1. Render 대시보드에서 서비스 선택
2. "Settings" → "Custom Domains"
3. 도메인 추가 및 DNS 설정

### 무료 플랜 제한사항

- **슬립 모드**: 15분간 요청이 없으면 서버가 슬립 모드로 전환
- **첫 요청**: 슬립 모드에서 깨어나는데 약 30초 소요
- **해결책**: Uptime Robot 같은 서비스를 사용하여 주기적으로 핑

## 🐛 문제 해결

### 배포 실패 시

1. **로그 확인**: Render 대시보드 → "Logs" 탭
2. **의존성 확인**: `requirements_gap_monitor.txt` 확인
3. **포트 확인**: 서버가 `PORT` 환경 변수를 사용하는지 확인

### 서버가 응답하지 않는 경우

1. **슬립 모드**: 첫 요청 시 30초 정도 대기
2. **로그 확인**: 에러 메시지 확인
3. **재배포**: "Manual Deploy" → "Deploy latest commit"

## 💡 팁

- 무료 플랜도 충분히 사용 가능합니다
- 자동 HTTPS 제공 (SSL 인증서 자동 설정)
- GitHub 연동으로 자동 배포 가능
- 로그 실시간 확인 가능

