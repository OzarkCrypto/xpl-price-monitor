# ✈️ Fly.io로 배포하기 (글로벌 배포)

Fly.io는 전 세계 여러 지역에 배포할 수 있어서 **가장 빠른** 응답 속도를 제공합니다.

## 🚀 배포 방법

### 1단계: Fly.io 가입
1. **https://fly.io** 접속
2. **"Sign Up"** 클릭
3. GitHub 또는 이메일로 가입

### 2단계: Fly CLI 설치
터미널에서 실행:
```bash
curl -L https://fly.io/install.sh | sh
```

### 3단계: 로그인
```bash
fly auth login
```
브라우저가 열리면 로그인

### 4단계: 앱 초기화
프로젝트 폴더에서:
```bash
cd /Users/chasanghun/practice
fly launch
```

질문에 답변:
- App name: `gap-monitor` (또는 원하는 이름)
- Region: 가장 가까운 지역 선택
- 기타 설정: 기본값 사용

### 5단계: 배포
```bash
fly deploy
```

### 6단계: 완료!
배포 완료 후 공개 URL 확인:
```bash
fly open
```

## 🎯 Fly.io의 장점

- ✅ **글로벌 배포**: 전 세계 여러 지역에 배포
- ✅ **빠른 속도**: 사용자에게 가장 가까운 서버로 연결
- ✅ **무료 플랜**: 3개의 공유 CPU VM
- ✅ **커스텀 도메인**: 쉽게 도메인 연결 가능

## 💰 비용

- **무료 플랜**: 3개의 공유 CPU VM
- **유료 플랜**: 사용량에 따라 과금

## 🔄 업데이트

코드 수정 후:
```bash
fly deploy
```

---

**Fly.io 시작하기** 👉 https://fly.io

