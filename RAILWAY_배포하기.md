# 🚂 Railway로 배포하기 (가장 간단!)

Railway는 설정 파일을 자동으로 인식해서 **가장 쉽게** 배포할 수 있습니다.

## ⚡ 3단계로 완료!

### 1단계: Railway 접속 및 로그인
1. 브라우저에서 **https://railway.app** 접속
2. **"Start a New Project"** 또는 **"Login"** 클릭
3. **"Login with GitHub"** 클릭
4. GitHub 계정으로 로그인

### 2단계: 저장소 연결
1. **"New Project"** 클릭
2. **"Deploy from GitHub repo"** 선택
3. GitHub 저장소 목록에서 **`OzarkCrypto/xpl-price-monitor`** 찾기
4. 클릭하여 선택

### 3단계: 자동 배포!
1. Railway가 자동으로 `railway.json` 파일을 인식합니다
2. 자동으로 배포가 시작됩니다 (약 2-3분)
3. 배포 완료 후 공개 URL이 생성됩니다!

## ✅ 배포 완료 확인

배포가 완료되면:
1. 프로젝트 대시보드에서 **"Settings"** 클릭
2. **"Generate Domain"** 클릭하여 공개 URL 생성
3. 또는 자동으로 생성된 URL 확인
   - 예: `https://gap-monitor.up.railway.app`

## 🎯 Railway의 장점

- ✅ **설정 파일 자동 인식**: `railway.json` 파일만 있으면 됨
- ✅ **슬립 모드 없음**: 항상 실행 중
- ✅ **무료 크레딧**: 월 $5 크레딧 제공
- ✅ **자동 재배포**: GitHub 푸시 시 자동 업데이트
- ✅ **간단한 설정**: 복잡한 설정 불필요

## 💰 비용

- **무료 크레딧**: 월 $5 (신규 가입 시)
- **사용량**: 실제 사용한 만큼만 과금
- **예상 비용**: 소규모 앱은 거의 무료

## 🔄 자동 업데이트

GitHub에 코드를 푸시하면 자동으로 재배포됩니다:
```bash
git push origin main
```

## 🆘 문제 해결

### 배포가 안 되는 경우
1. **로그 확인**: Railway 대시보드 → "Deployments" → "View Logs"
2. **설정 확인**: `railway.json` 파일이 올바른지 확인

### 도메인이 안 보이는 경우
1. **Settings** → **"Generate Domain"** 클릭
2. 또는 **"Custom Domain"** 추가 가능

---

**지금 바로 시작하세요!** 👉 https://railway.app

