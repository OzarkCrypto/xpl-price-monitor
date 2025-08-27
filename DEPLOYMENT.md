# 🚀 Vercel 배포 가이드

XPL 가격 모니터를 Vercel에 배포하는 방법입니다.

## 📋 사전 준비

1. **GitHub 계정** - 코드를 저장할 저장소가 필요합니다
2. **Vercel 계정** - [vercel.com](https://vercel.com)에서 가입

## 🔧 배포 단계

### 1. GitHub에 코드 푸시

```bash
# Git 저장소 초기화
git init
git add .
git commit -m "Initial commit: XPL Price Monitor"

# GitHub 저장소와 연결 (YOUR_REPO_URL을 실제 저장소 URL로 변경)
git remote add origin YOUR_REPO_URL
git push -u origin main
```

### 2. Vercel에서 배포

1. [vercel.com](https://vercel.com)에 로그인
2. "New Project" 클릭
3. GitHub 저장소 선택
4. 자동으로 배포 설정 감지됨
5. "Deploy" 클릭

## 📁 배포 파일 구조

```
├── api/
│   └── index.py          # Vercel 서버리스 함수
├── xpl_price_monitor.py  # 메인 Flask 앱
├── vercel.json           # Vercel 설정
├── requirements.txt      # Python 의존성
└── templates/
    └── index.html        # HTML 템플릿
```

## 🌐 배포 후 접속

배포가 완료되면 다음과 같은 URL로 접속할 수 있습니다:
- `https://your-project-name.vercel.app`

## 🔄 자동 배포

GitHub 저장소에 코드를 푸시하면 Vercel에서 자동으로 재배포됩니다.

## 📱 기능

- ✅ 실시간 XPL 가격 모니터링
- ✅ Binance vs Hyperliquid 가격 비교
- ✅ 가격 갭 분석
- ✅ 업데이트 시간 및 경과 시간 표시
- ✅ 반응형 디자인
- ✅ 30초 자동 업데이트

## 🐛 문제 해결

### 배포 실패 시
1. `requirements.txt` 확인
2. `vercel.json` 설정 확인
3. Python 버전 호환성 확인

### API 오류 시
1. Binance API 상태 확인
2. Hyperliquid API 상태 확인
3. 네트워크 연결 확인

## 📞 지원

문제가 발생하면 GitHub Issues에 등록해 주세요.
