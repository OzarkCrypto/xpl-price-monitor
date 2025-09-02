# 🚀 Aave 모니터링 봇 배포 가이드

## 📋 사전 준비

1. **텔레그램 봇 생성**
   - @BotFather에서 봇 생성
   - 봇 토큰 받기
   - 봇과 대화 시작

2. **채팅 ID 확인**
   - 봇에게 메시지 보내기
   - `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` 접속
   - `chat.id` 값 확인

## 🔍 모니터링 봇 종류

### 1. **다중 포럼 모니터링 봇**
- 특정 포럼들의 새로운 댓글과 활동 감지
- USDe, sUSDe, tUSDe PT 토큰 관련 포럼 모니터링

### 2. **PT/Onboard 키워드 모니터링 봇**
- "PT"와 "Onboard" 단어가 모두 포함된 새로운 토픽 감지
- 해당 토픽에 달린 새로운 댓글 감지
- **전체 거버넌스 포럼에서 키워드 기반 모니터링**
- **탐색 범위: 최근 2주 내 활동만**

## 🔧 GitHub 설정

### 1. 저장소 생성
```bash
# 로컬에서 새 저장소 초기화
git init
git add .
git commit -m "Initial commit: Aave governance monitor bot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### 2. GitHub Secrets 설정

GitHub 저장소의 **Settings** > **Secrets and variables** > **Actions**에서:

- **New repository secret** 클릭
- `TELEGRAM_TOKEN`: 텔레그램 봇 토큰 입력
- `TELEGRAM_CHAT_ID`: 텔레그램 채팅 ID 입력

### 3. Actions 권한 설정

**Settings** > **Actions** > **General**에서:
- **Actions permissions**: "Allow all actions and reusable workflows" 선택
- **Workflow permissions**: "Read and write permissions" 선택

## ✅ 배포 확인

### 1. Actions 탭 확인
- GitHub 저장소의 **Actions** 탭에서 워크플로우 실행 상태 확인
- 초록색 체크마크가 뜨면 성공

### 2. 텔레그램 알림 확인
- **다중 포럼 모니터링 봇** 시작 메시지 확인
- **PT/Onboard 키워드 모니터링 봇** 시작 메시지 확인
- 1시간 후 자동 실행 확인

### 3. 모니터링 결과 확인
- 새로운 PT/Onboard 토픽 발견 시 알림
- 해당 토픽에 새로운 댓글 달릴 때 알림
- 각 알림에 링크 포함되어 있는지 확인

## 🧪 테스트

### 수동 실행 테스트
1. **Actions** 탭에서 **Aave Governance Monitor** 워크플로우 선택
2. **Run workflow** 버튼 클릭
3. **Run workflow** 클릭하여 즉시 실행

### 로그 확인
- Actions 실행 후 **monitor** 작업 클릭
- 각 단계별 로그 확인

## 🔄 모니터링 설정 변경

### 포럼 추가/제거
`aave_multi_forum_monitor.py`의 `FORUMS` 리스트 수정

### 실행 간격 변경
`.github/workflows/aave_monitor.yml`의 cron 표현식 수정:
- 1시간: `'0 * * * *'`
- 30분: `'*/30 * * * *'`
- 15분: `'*/15 * * * *'`

## 🚨 문제 해결

### 봇이 메시지를 보내지 않는 경우
1. 텔레그램 봇 토큰 확인
2. 채팅 ID 확인
3. 봇과 대화 시작했는지 확인

### Actions 실행 실패
1. 로그에서 오류 메시지 확인
2. Python 버전 호환성 확인
3. 의존성 패키지 설치 오류 확인

### 포럼 접근 오류
1. URL 유효성 확인
2. 네트워크 연결 상태 확인
3. Aave 포럼 접근 권한 확인

## 📞 지원

문제가 발생하면:
1. GitHub Issues 생성
2. Actions 로그 첨부
3. 오류 메시지 상세 설명
