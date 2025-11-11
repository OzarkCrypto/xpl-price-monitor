# 🚂 Railway 자동 배포 가이드

Railway는 GitHub 저장소를 연결하면 **자동으로 배포**됩니다!

## ✅ 배포 준비 완료

다음 파일들이 준비되어 있습니다:
- ✅ `railway.json`: Railway 배포 설정
- ✅ `railway.toml`: Railway 설정 (최신 형식)
- ✅ `requirements_gap_monitor.txt`: Python 의존성
- ✅ 모든 코드 파일: GitHub에 푸시 완료

## 🚀 Railway 배포 방법

### 방법 1: Railway 웹사이트에서 배포 (가장 쉬움)

1. **https://railway.app** 접속
2. **"Start a New Project"** 클릭
3. **"Deploy from GitHub repo"** 선택
4. GitHub 계정으로 로그인 (처음이면)
5. 저장소 선택: **`OzarkCrypto/xpl-price-monitor`**
6. **자동 배포 시작!** 🎉

Railway가 자동으로:
- `railway.json` 또는 `railway.toml` 파일 인식
- Python 환경 감지
- 의존성 설치
- 서버 시작

### 방법 2: Railway CLI 사용

```bash
# Railway CLI 설치 (이미 시도함)
# 사용자 디렉토리에 설치됨: ~/.local/bin/railway

# 로그인
railway login

# 프로젝트 초기화
railway init

# 배포
railway up
```

## 📋 배포 후 확인

배포가 완료되면:
1. Railway 대시보드에서 공개 URL 확인
2. 예: `https://gap-monitor.up.railway.app`
3. 대시보드 접속 테스트

## 🔄 자동 재배포

GitHub에 코드를 푸시하면 자동으로 재배포됩니다:
```bash
git push origin main
```

## 💰 비용

- **무료 크레딧**: 월 $5 제공
- **사용량**: 실제 사용한 만큼만 과금
- **예상**: 소규모 앱은 거의 무료

## 🎯 Railway의 장점

- ✅ Flask 앱 직접 지원
- ✅ 백그라운드 스레드 지원
- ✅ 상태 유지 가능
- ✅ 슬립 모드 없음
- ✅ 설정 파일 자동 인식
- ✅ 자동 HTTPS

---

**지금 바로 Railway에서 배포하세요!** 👉 https://railway.app

