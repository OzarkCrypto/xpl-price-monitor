# Aave 거버넌스 모니터링 봇

Aave 거버넌스 포럼의 새로운 댓글이나 활동을 실시간으로 모니터링하고 텔레그램으로 알림을 보내는 봇입니다.

## 🎯 모니터링 대상

- **URL**: [USDe November expiry PT tokens on Aave V3 Core Instance](https://governance.aave.com/t/direct-to-aip-onboard-usde-november-expiry-pt-tokens-on-aave-v3-core-instance/23013)
- **내용**: 새로운 댓글, 활동 내역
- **체크 간격**: 5분마다

## 🚀 주요 기능

- 🔍 **실시간 모니터링**: Aave 거버넌스 포럼 페이지를 주기적으로 체크
- 💬 **댓글 감지**: 새로운 댓글이 올라오면 즉시 알림
- 📢 **활동 추적**: 포럼의 새로운 활동을 감지하고 알림
- 🤖 **텔레그램 알림**: 설정된 텔레그램 채팅방으로 실시간 알림
- 💾 **데이터 저장**: SQLite 데이터베이스에 모든 활동 기록
- 📝 **상세 로깅**: 모든 활동을 로그 파일에 기록

## 📋 필요 요구사항

- Python 3.7+
- 인터넷 연결
- 텔레그램 봇 토큰
- 텔레그램 채팅 ID

## 🛠️ 설치 및 설정

### 1. 의존성 설치

```bash
# 가상환경 생성
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows

# 필요한 패키지 설치
pip install -r requirements_aave_monitor.txt
```

### 2. 설정 확인

`aave_governance_monitor.py` 파일에서 다음 설정을 확인하세요:

```python
TELEGRAM_TOKEN = "8253278813:AAH5I5cMlu6N7srGDNl8LkPnW2PUJRPPTTI"
CHAT_ID = "1339285013"
MONITOR_URL = "https://governance.aave.com/t/direct-to-aip-onboard-usde-november-expiry-pt-tokens-on-aave-v3-core-instance/23013"
CHECK_INTERVAL = 300  # 5분마다 체크
```

## 🚀 사용법

### 1. 테스트 실행

먼저 봇이 정상적으로 작동하는지 테스트해보세요:

```bash
python3 test_aave_monitor.py
```

### 2. 직접 실행

```bash
python3 aave_governance_monitor.py
```

### 3. 백그라운드 실행 (데몬)

```bash
# 실행 권한 부여
chmod +x *.sh

# 백그라운드에서 실행
./start_aave_monitor_daemon.sh

# 상태 확인
ps aux | grep aave_governance_monitor

# 중지
./stop_aave_monitor_daemon.sh
```

### 4. 쉘 스크립트 실행

```bash
./run_aave_monitor.sh
```

## 📱 텔레그램 알림 예시

### 새 댓글 알림
```
🔔 새로운 댓글 발견!

👤 작성자: ACI
💬 내용: This proposal will be a Direct to AIP...
⏰ 시간: 2025-08-25T11:09:00Z
🔗 링크: 댓글 보기

#Aave #Governance #USDe #PT #Token
```

### 새 활동 알림
```
📢 새로운 활동 발견!

📋 유형: activity
📝 설명: New activity detected...
⏰ 시간: 2025-08-25T11:10:00Z
🔗 링크: 포럼 보기

#Aave #Governance #Activity
```

## 📊 데이터베이스 구조

### comments 테이블
- `id`: 자동 증가 ID
- `comment_id`: 댓글 고유 ID
- `author`: 작성자
- `content`: 댓글 내용
- `timestamp`: 작성 시간
- `url`: 댓글 링크
- `created_at`: 기록 생성 시간

### activities 테이블
- `id`: 자동 증가 ID
- `activity_type`: 활동 유형
- `description`: 활동 설명
- `timestamp`: 활동 시간
- `url`: 포럼 링크
- `created_at`: 기록 생성 시간

## 📝 로그 파일

- `aave_monitor.log`: 일반 로그
- `aave_monitor_daemon.log`: 데몬 실행 로그

## ⚙️ 설정 옵션

### 체크 간격 조정
```python
CHECK_INTERVAL = 300  # 5분 (초 단위)
```

### 모니터링 URL 변경
```python
MONITOR_URL = "새로운_URL"
```

### 텔레그램 설정 변경
```python
TELEGRAM_TOKEN = "새로운_토큰"
CHAT_ID = "새로운_채팅_ID"
```

## 🔧 문제 해결

### 1. 텔레그램 봇이 응답하지 않는 경우
- 봇 토큰이 올바른지 확인
- 채팅 ID가 정확한지 확인
- 봇이 해당 채팅방에 추가되었는지 확인

### 2. 페이지 접근이 안 되는 경우
- 인터넷 연결 상태 확인
- Aave 웹사이트 접근 가능 여부 확인
- User-Agent 헤더 확인

### 3. 파싱 오류가 발생하는 경우
- Aave 웹사이트 구조 변경 여부 확인
- HTML 요소 클래스명 변경 여부 확인
- 로그 파일에서 구체적인 오류 내용 확인

## 📈 모니터링 통계

봇이 실행되면 다음과 같은 정보를 제공합니다:

- 📊 현재 댓글 수
- 📊 현재 활동 수
- 🔍 새로운 댓글/활동 감지
- 📝 텔레그램 메시지 전송 상태
- ⏰ 모니터링 시작/종료 시간

## 🚨 주의사항

1. **API 제한**: Aave 웹사이트에 과도한 요청을 보내지 않도록 주의
2. **데이터 백업**: 중요한 모니터링 데이터는 정기적으로 백업
3. **토큰 보안**: 텔레그램 봇 토큰을 안전하게 보관
4. **리소스 관리**: 장기간 실행 시 시스템 리소스 모니터링

## 📞 지원

문제가 발생하거나 질문이 있으시면:

1. 로그 파일 확인
2. 테스트 스크립트 실행
3. 설정 값 재확인
4. 의존성 패키지 재설치

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

**Happy Monitoring! 🚀**


