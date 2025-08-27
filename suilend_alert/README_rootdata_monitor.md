# 🔥 Rootdata Hot Index 모니터

Rootdata 웹사이트의 hot index를 매시간 정각에 모니터링하고 TOP 10을 텔레그램으로 전송하는 자동화 봇입니다.

## 📋 주요 기능

- **자동 모니터링**: 매시간 정각에 자동으로 hot index 데이터 수집
- **TOP 10 랭킹**: hot index 순으로 정렬하여 상위 10개 프로젝트 선별
- **변화값 추적**: 이전 시간 대비 hot index 변화량 표시 (📈 증가/📉 감소/🆕 신규/➖ 변화없음)
- **텔레그램 알림**: 자동으로 텔레그램 채널에 랭킹 정보 전송
- **데이터 저장**: 이전 데이터 자동 저장 및 비교 기능
- **실시간 로깅**: 모든 활동을 로그 파일에 기록
- **에러 처리**: 네트워크 오류나 파싱 실패 시 자동 복구

## 🚀 설치 및 설정

### 1. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일에 다음 정보를 추가하세요:

```bash
# Rootdata Hot Index 모니터링 전용 설정
ROOTDATA_BOT_TOKEN=your_bot_token_here
ROOTDATA_CHAT_ID=your_chat_id_here
```

**중요**: 기존 Suilend LTV 모니터링과 Alkimi 가격 모니터링은 그대로 유지되며, 
Rootdata Hot Index만 새로운 텔레그램 채널로 전송됩니다.

### 3. 텔레그램 봇 설정

1. [@BotFather](https://t.me/botfather)에서 새 봇 생성
2. 봇 토큰을 `.env` 파일에 입력
3. 봇을 원하는 채널에 추가
4. 채널 ID를 `.env` 파일에 입력

## 📊 사용 방법

### 웹사이트 구조 분석 (처음 실행 시)

```bash
# 실행 권한 부여
chmod +x run_rootdata_analyzer.sh

# 분석기 실행
./run_rootdata_analyzer.sh
```

이 단계에서 Rootdata 웹사이트의 실제 구조를 파악하고 HTML 소스 파일이 저장됩니다.

### 모니터링 시작

```bash
# 실행 권한 부여
chmod +x run_rootdata_monitor.sh

# 모니터 실행
./run_rootdata_monitor.sh
```

### 한 번만 실행 (테스트용)

```bash
python rootdata_hot_index_monitor.py --once
```

## ⏰ 스케줄

모니터는 **매시간 정각**에 자동으로 실행됩니다:
- **00:00** (자정)
- **01:00** (새벽 1시)
- **02:00** (새벽 2시)
- **...**
- **22:00** (저녁 10시)
- **23:00** (저녁 11시)

총 **24시간 동안 24번** 실행되어 실시간에 가까운 모니터링을 제공합니다.

## 📁 파일 구조

```
suilend_alert/
├── rootdata_hot_index_monitor.py    # 메인 모니터링 프로그램
├── rootdata_analyzer.py             # 웹사이트 구조 분석기
├── run_rootdata_monitor.sh          # 모니터 실행 스크립트
├── run_rootdata_analyzer.sh         # 분석기 실행 스크립트
├── rootdata_hot_index.log           # 로그 파일
├── rootdata_source_*.html           # HTML 소스 파일 (분석용)
└── README_rootdata_monitor.md       # 이 파일
```

## 🔧 커스터마이징

### 파싱 로직 수정

`rootdata_hot_index_monitor.py`의 `parse_hot_index` 메서드를 수정하여 실제 웹사이트 구조에 맞게 조정하세요.

### 알림 시간 변경

`start_scheduler` 메서드에서 스케줄 시간을 원하는 대로 수정할 수 있습니다.

### 메시지 형식 변경

`format_telegram_message` 메서드에서 텔레그램 메시지 형식을 커스터마이징할 수 있습니다.

## 🐛 문제 해결

### 데이터를 가져올 수 없는 경우

1. `rootdata_analyzer.py`를 실행하여 웹사이트 구조 분석
2. HTML 소스 파일 확인
3. `parse_hot_index` 메서드의 파싱 로직 수정

### 텔레그램 전송 실패

1. 봇 토큰과 채팅 ID 확인
2. 봇이 채널에 추가되었는지 확인
3. 봇 권한 설정 확인

### 네트워크 오류

1. 인터넷 연결 상태 확인
2. Rootdata 웹사이트 접근 가능 여부 확인
3. 방화벽 설정 확인

## 📝 로그 확인

```bash
# 실시간 로그 확인
tail -f rootdata_hot_index.log

# 최근 로그 확인
tail -n 100 rootdata_hot_index.log
```

## 🔒 보안 주의사항

- `.env` 파일을 Git에 커밋하지 마세요
- 텔레그램 봇 토큰을 공개하지 마세요
- 프로덕션 환경에서는 적절한 보안 설정을 적용하세요

## 📞 지원

문제가 발생하거나 개선 사항이 있으면 이슈를 등록해 주세요.

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 