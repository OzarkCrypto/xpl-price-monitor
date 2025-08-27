# 폴리마켓 신규 마켓 모니터

폴리마켓에서 새로운 마켓이 생성되면 텔레그램으로 실시간 알림을 보내는 봇입니다.

## 🚀 주요 기능

- **실시간 마켓 모니터링**: 폴리마켓 API를 통해 새로운 마켓을 지속적으로 감시
- **텔레그램 알림**: 새로운 마켓 발견 시 즉시 텔레그램으로 알림 전송
- **스마트 중복 방지**: 이미 알려진 마켓은 중복 알림 방지
- **상세 마켓 정보**: 마켓 제목, 만료일, 거래량, 참여자 수 등 포함
- **자동 재시작**: 오류 발생 시 자동으로 복구 및 재시작
- **로깅 시스템**: 모든 활동을 로그 파일에 기록

## 📋 요구사항

- Python 3.7+
- 텔레그램 봇 토큰
- 텔레그램 채팅 ID
- 인터넷 연결

## 🛠️ 설치 및 설정

### 1. 저장소 클론 또는 파일 다운로드

```bash
# 필요한 파일들이 있는지 확인
ls -la polymarket_monitor.py
ls -la notification_system.py
```

### 2. 환경 변수 설정

```bash
# 환경 변수 템플릿 생성
python3 polymarket_config.py

# 템플릿을 .env로 복사
cp .env.template .env

# .env 파일 편집하여 실제 값 입력
nano .env
```

`.env` 파일에 다음 정보를 입력하세요:

```env
# 텔레그램 설정
TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
TELEGRAM_CHAT_ID=your_actual_chat_id_here

# 모니터링 설정
POLYMARKET_CHECK_INTERVAL=60
POLYMARKET_MAX_MARKETS=100

# 알림 설정
ENABLE_NEW_MARKET_ALERTS=true
ENABLE_MARKET_UPDATES=false
```

### 3. 텔레그램 봇 설정

#### 텔레그램 봇 생성
1. [@BotFather](https://t.me/botfather)에게 `/newbot` 명령어 전송
2. 봇 이름과 사용자명 설정
3. 받은 토큰을 `TELEGRAM_BOT_TOKEN`에 입력

#### 채팅 ID 확인
1. 봇을 원하는 채팅방에 초대
2. 채팅방에서 아무 메시지나 전송
3. 다음 URL로 접속하여 chat_id 확인:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
4. `chat.id` 값을 `TELEGRAM_CHAT_ID`에 입력

### 4. 필요한 패키지 설치

```bash
pip3 install requests
```

## 🚀 실행 방법

### 방법 1: 실행 스크립트 사용 (권장)

```bash
# 실행 권한 부여
chmod +x run_polymarket_monitor.sh

# 모니터링 시작
./run_polymarket_monitor.sh
```

### 방법 2: 직접 실행

```bash
python3 polymarket_monitor.py
```

### 방법 3: 백그라운드 실행

```bash
nohup python3 polymarket_monitor.py > polymarket_monitor.out 2>&1 &
```

## ⚙️ 설정 옵션

### 모니터링 설정
- `POLYMARKET_CHECK_INTERVAL`: 마켓 확인 간격 (초, 기본값: 60)
- `POLYMARKET_MAX_MARKETS`: 한 번에 확인할 최대 마켓 수 (기본값: 100)

### 알림 설정
- `ENABLE_NEW_MARKET_ALERTS`: 새로운 마켓 알림 활성화 (기본값: true)
- `ENABLE_MARKET_UPDATES`: 마켓 업데이트 알림 활성화 (기본값: false)

## 📱 알림 예시

새로운 마켓 발견 시 다음과 같은 형식으로 알림이 전송됩니다:

```
🚨 새로운 폴리마켓 마켓 발견!

📊 마켓: Will Bitcoin reach $100,000 by end of 2024?
�� 링크: 폴리마켓에서 보기
📅 만료일: 2024-12-31 23:59 UTC
💰 총 거래량: $1,250,000
👥 참여자 수: 1,234

⏰ 발견 시간: 2024-01-15 14:30:25 KST
```

## 📊 모니터링 정보

### 로그 파일
- `polymarket_monitor.log`: 모든 활동 기록
- `polymarket_known_markets.json`: 알려진 마켓 목록 캐시

### 모니터링 통계
- 새로운 마켓 발견 수
- API 호출 성공/실패율
- 알림 전송 성공/실패율

## 🔧 문제 해결

### 일반적인 문제들

#### 1. 텔레그램 알림이 전송되지 않음
- 봇 토큰과 채팅 ID가 올바른지 확인
- 봇이 채팅방에 초대되어 있는지 확인
- `.env` 파일이 올바르게 설정되었는지 확인

#### 2. API 오류 발생
- 인터넷 연결 상태 확인
- 폴리마켓 서버 상태 확인
- 로그 파일에서 구체적인 오류 메시지 확인

#### 3. 중복 알림 발생
- `polymarket_known_markets.json` 파일 삭제 후 재시작
- 마켓 해시 생성 로직 확인

### 로그 확인

```bash
# 실시간 로그 확인
tail -f polymarket_monitor.log

# 최근 오류 로그 확인
grep "ERROR" polymarket_monitor.log | tail -20
```

## 🔄 업데이트 및 유지보수

### 정기적인 점검사항
1. 로그 파일 크기 확인 및 필요시 정리
2. 알려진 마켓 캐시 파일 크기 확인
3. API 응답 시간 및 성공률 모니터링

### 성능 최적화
- `POLYMARKET_CHECK_INTERVAL` 조정으로 API 호출 빈도 조절
- `POLYMARKET_MAX_MARKETS` 조정으로 한 번에 처리할 마켓 수 조절

## 📞 지원 및 문의

문제가 발생하거나 개선 사항이 있으시면:
1. 로그 파일을 확인하여 오류 내용 파악
2. GitHub 이슈 또는 개인 연락처로 문의

## 📄 라이선스

이 프로젝트는 교육 및 개인 사용 목적으로 제작되었습니다.

---

**주의사항**: 이 봇은 폴리마켓의 공개 API를 사용합니다. API 사용 정책을 준수하고 과도한 요청을 피해주세요. 