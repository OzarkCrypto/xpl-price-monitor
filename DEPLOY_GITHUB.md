# GitHub를 통한 클라우드 배포 가이드

GitHub에 코드를 올려서 클라우드에서 서버를 자동으로 실행하는 방법입니다.

## 🚀 빠른 시작 (3단계)

### 1단계: GitHub에 코드 푸시

```bash
# 필요한 파일 추가
git add hyperliquid_binance_gap_server.py
git add templates/hyperliquid_binance_gap_dashboard.html
git add requirements_gap_monitor.txt
git add render.yaml Procfile railway.json
git add README_gap_monitor.md

# 커밋 및 푸시
git commit -m "Add Hyperliquid vs Binance gap monitor"
git push origin main
```

### 2단계: 클라우드 서비스 선택 및 배포

아래 중 하나를 선택하세요:

#### 옵션 A: Render (추천 - 무료 플랜 제공)

1. **Render 계정 생성**: https://render.com
2. **새 Web Service 생성**:
   - "New" → "Web Service" 클릭
   - GitHub 저장소 연결
   - 다음 설정 입력:
     - **Name**: `gap-monitor`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements_gap_monitor.txt`
     - **Start Command**: `python3 hyperliquid_binance_gap_server.py`
     - **Plan**: Free (무료)
3. **배포 완료!** 자동으로 URL이 생성됩니다.

#### 옵션 B: Railway (간단한 설정)

1. **Railway 계정 생성**: https://railway.app
2. **새 프로젝트 생성**:
   - "New Project" 클릭
   - "Deploy from GitHub repo" 선택
   - 저장소 선택
3. **자동 배포!** `railway.json` 파일이 자동으로 인식됩니다.

#### 옵션 C: Fly.io (글로벌 배포)

1. **Fly.io 계정 생성**: https://fly.io
2. **Fly CLI 설치**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```
3. **배포**:
   ```bash
   fly launch
   fly deploy
   ```

## 📋 배포 후 확인

배포가 완료되면 다음과 같은 공개 URL이 제공됩니다:
- Render: `https://gap-monitor.onrender.com`
- Railway: `https://gap-monitor.up.railway.app`
- Fly.io: `https://gap-monitor.fly.dev`

이 URL을 다른 사람들과 공유하세요!

## 🔄 자동 배포

GitHub에 코드를 푸시하면 자동으로 재배포됩니다:
```bash
git add .
git commit -m "Update gap monitor"
git push
```

## ⚙️ 환경 변수 설정 (선택사항)

클라우드 서비스 대시보드에서 환경 변수를 설정할 수 있습니다:

- `FLASK_DEBUG`: `False` (프로덕션)
- `PORT`: 자동 설정됨 (수정 불필요)

## 🐛 문제 해결

### 배포 실패 시

1. **로그 확인**: 클라우드 서비스 대시보드에서 로그 확인
2. **의존성 확인**: `requirements_gap_monitor.txt`에 모든 패키지가 포함되어 있는지 확인
3. **포트 확인**: 서버가 환경 변수 `PORT`를 사용하는지 확인

### 서버가 시작되지 않는 경우

1. **빌드 로그 확인**: 의존성 설치 오류 확인
2. **시작 명령어 확인**: `python3 hyperliquid_binance_gap_server.py`가 올바른지 확인
3. **템플릿 경로 확인**: `templates/` 폴더가 포함되어 있는지 확인

## 💡 팁

- **무료 플랜 제한**: 일정 시간 비활성 시 서버가 슬립 모드로 전환될 수 있습니다 (첫 요청 시 깨어남)
- **도메인 연결**: 커스텀 도메인을 연결할 수 있습니다
- **SSL 자동**: 모든 클라우드 서비스가 자동으로 HTTPS 제공

## 📊 서비스 비교

| 서비스 | 무료 플랜 | 자동 배포 | 슬립 모드 | 추천도 |
|--------|----------|----------|----------|--------|
| Render | ✅ | ✅ | ⚠️ (15분) | ⭐⭐⭐⭐⭐ |
| Railway | ✅ | ✅ | ❌ | ⭐⭐⭐⭐ |
| Fly.io | ✅ | ✅ | ❌ | ⭐⭐⭐ |

## 🎯 다음 단계

배포가 완료되면:
1. 공개 URL 테스트
2. 다른 사람들과 URL 공유
3. 모니터링 및 로그 확인

