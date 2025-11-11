# ▲ Vercel로 배포하기

Vercel은 서버리스 플랫폼으로, Flask 앱을 서버리스 함수로 변환하여 배포합니다.

## ⚡ 빠른 배포 (5분)

### 1단계: Vercel 접속 및 로그인
1. 브라우저에서 **https://vercel.com** 접속
2. **"Sign Up"** 또는 **"Log In"** 클릭
3. **"Continue with GitHub"** 클릭
4. GitHub 계정으로 로그인

### 2단계: 새 프로젝트 생성
1. Vercel 대시보드에서 **"Add New..."** → **"Project"** 클릭
2. GitHub 저장소 목록에서 **`OzarkCrypto/xpl-price-monitor`** 찾기
3. **"Import"** 클릭

### 3단계: 프로젝트 설정
Vercel이 자동으로 설정을 감지합니다. 다음을 확인하세요:

**Framework Preset:**
```
Other
```
(또는 자동 감지)

**Root Directory:**
```
./
```
(기본값 그대로)

**Build Command:**
```
(비워두기 - Vercel이 자동으로 처리)
```

**Output Directory:**
```
(비워두기)
```

**Install Command:**
```
(비워두기)
```

**중요**: Vercel은 `vercel.json` 파일을 자동으로 인식합니다!

### 4단계: 환경 변수 설정 (선택사항)
"Environment Variables" 섹션에서:
- `FLASK_DEBUG`: `False`
- `PYTHON_VERSION`: `3.9`

### 5단계: 배포 시작
1. **"Deploy"** 버튼 클릭
2. 배포가 시작됩니다 (약 2-3분 소요)
3. 배포 완료 후 공개 URL이 생성됩니다!

## ✅ 배포 완료 확인

배포가 완료되면:
1. 대시보드에서 **"Visit"** 버튼 클릭
2. 또는 공개 URL 확인
   - 예: `https://xpl-price-monitor.vercel.app`
3. 대시보드가 정상적으로 보이는지 확인

## 🎯 Vercel의 장점

- ✅ **매우 빠른 배포**: 몇 분 안에 완료
- ✅ **자동 HTTPS**: SSL 인증서 자동 설정
- ✅ **글로벌 CDN**: 전 세계 빠른 속도
- ✅ **무료 플랜**: 충분한 무료 사용량
- ✅ **자동 재배포**: GitHub 푸시 시 자동 업데이트

## ⚠️ 주의사항

### 서버리스 제한사항
- **백그라운드 작업**: 서버리스 함수는 요청이 있을 때만 실행
- **상태 유지**: 메모리 상태가 요청 간에 유지되지 않을 수 있음
- **타임아웃**: 함수 실행 시간 제한 (무료 플랜: 10초)

### 해결 방법
1. **상태 관리**: 데이터베이스나 외부 저장소 사용
2. **백그라운드 작업**: 별도의 워커 서비스 사용 (예: Vercel Cron Jobs)
3. **캐싱**: 외부 캐시 서비스 사용

## 🔄 자동 재배포

GitHub에 코드를 푸시하면 자동으로 재배포됩니다:
```bash
git push origin main
```

## 🛠️ Vercel 설정 파일

프로젝트에 `vercel.json` 파일이 있습니다:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "hyperliquid_binance_gap_server.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "hyperliquid_binance_gap_server.py"
    }
  ]
}
```

## 💰 비용

- **무료 플랜**: 
  - 월 100GB 대역폭
  - 무제한 요청
  - 함수 실행 시간: 10초 제한
- **프로 플랜**: $20/월 (더 많은 기능)

## 🆘 문제 해결

### 배포 실패 시
1. **로그 확인**: Vercel 대시보드 → "Deployments" → "View Function Logs"
2. **빌드 로그 확인**: "Build Logs" 탭에서 에러 확인
3. **의존성 확인**: `requirements_gap_monitor.txt` 확인

### 함수 타임아웃
- 요청 처리 시간이 10초를 초과하면 타임아웃
- 해결: 비동기 작업을 별도로 처리

### 상태 유지 문제
- 서버리스 함수는 상태를 유지하지 않음
- 해결: 데이터베이스나 외부 저장소 사용

## 📱 커스텀 도메인

1. Vercel 대시보드 → 프로젝트 → "Settings" → "Domains"
2. 도메인 추가
3. DNS 설정 안내에 따라 설정

## 🔧 Vercel CLI 사용 (선택사항)

터미널에서 직접 배포할 수도 있습니다:

```bash
# Vercel CLI 설치
npm i -g vercel

# 로그인
vercel login

# 배포
vercel

# 프로덕션 배포
vercel --prod
```

---

**지금 바로 시작하세요!** 👉 https://vercel.com

