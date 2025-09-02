# VC Investment Monitor Bot

VC 투자 정보를 모니터링하고 좋은 VC가 투자한 프로젝트에 대해 텔레그램 알림을 보내는 봇입니다.

## 🚀 주요 기능

- **자동 스크래핑**: crypto-fundraising.info에서 최신 투자 정보 자동 수집
- **Top VC 감지**: 주요 VC들의 투자 참여 여부 자동 감지
- **스마트 점수 시스템**: VC 등급별 가중치를 적용한 투자 점수 계산
- **실시간 알림**: 텔레그램을 통한 즉시 투자 알림
- **데이터베이스 저장**: 모든 투자 정보를 체계적으로 저장 및 관리
- **일일 요약**: 매일 투자 현황 요약 리포트 제공

## 📊 VC 등급 시스템

### Tier 1 (🔥🔥🔥) - 최고 수준
- a16z, Andreessen Horowitz
- Paradigm, Polychain Capital
- Pantera Capital

### Tier 2 (🔥🔥) - 주요 VC
- Electric Capital, Multicoin Capital
- Framework Ventures, Dragonfly Capital

### Tier 3 (🔥) - 성장하는 VC
- Binance Labs, Coinbase Ventures
- Galaxy Digital, Digital Currency Group

## 🛠️ 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements_vc_monitor.txt
```

### 2. 텔레그램 봇 설정
- `vc_monitor_enhanced.py` 파일에서 `TELEGRAM_TOKEN`과 `CHAT_ID` 설정
- 현재 설정된 값:
  - Token: `7902910088:AAEF6kdafHyu-gCdvC5kWoq1CpDeabtw0_g`
  - Chat ID: `1339285013`

## 🚀 실행 방법

### 1. 직접 실행
```bash
python3 vc_monitor_enhanced.py
```

### 2. 쉘 스크립트 실행
```bash
chmod +x run_vc_monitor.sh
./run_vc_monitor.sh
```

### 3. 데몬으로 백그라운드 실행
```bash
chmod +x start_vc_monitor_daemon.sh
./start_vc_monitor_daemon.sh
```

### 4. 데몬 중지
```bash
chmod +x stop_vc_monitor_daemon.sh
./stop_vc_monitor_daemon.sh
```

## 🧪 테스트

봇의 기능을 테스트하려면:
```bash
python3 test_vc_monitor.py
```

## 📁 파일 구조

```
vc_monitor_enhanced.py      # 메인 모니터링 봇
vc_scraper.py              # 향상된 웹 스크래퍼
test_vc_monitor.py         # 테스트 스크립트
requirements_vc_monitor.txt # Python 의존성
run_vc_monitor.sh          # 실행 스크립트
start_vc_monitor_daemon.sh # 데몬 시작 스크립트
stop_vc_monitor_daemon.sh  # 데몬 중지 스크립트
vc_monitor_enhanced.db     # SQLite 데이터베이스
vc_monitor_enhanced.log    # 로그 파일
```

## 🔧 설정 옵션

### 모니터링 주기
- 기본값: 30분마다 새로운 투자 정보 확인
- `vc_monitor_enhanced.py`의 `run_monitor()` 함수에서 조정 가능

### 알림 기준
- VC 점수 50점 이상인 투자만 알림 전송
- 점수는 VC 등급과 투자자 수에 따라 계산

### 데이터베이스
- SQLite 데이터베이스 사용
- 투자 정보, Top VC 투자, VC 통계 테이블 포함

## 📱 텔레그램 알림 형식

```
🔥🔥🔥 VC 투자 알림! 🔥🔥🔥

📊 프로젝트: Stargate Finance STG
💰 라운드: M&A
📅 날짜: 2025-08-01
💵 금액: TBD
🏷️ 카테고리: Infrastructure, Interoperability
⭐ VC 점수: 100/100

🚀 참여한 Top VC:
• LayerZero

👥 전체 투자자:
LayerZero

🔗 출처: crypto-fundraising.info
```

## 📊 일일 요약 리포트

매일 자정에 전송되는 요약:
- 총 투자 건수
- Top VC 투자 건수
- 가장 활발한 VC 순위

## 🚨 문제 해결

### 스크래핑 실패
- 웹사이트 구조 변경 시 `vc_scraper.py` 수정 필요
- 네트워크 연결 상태 확인

### 텔레그램 알림 실패
- 봇 토큰과 Chat ID 확인
- 텔레그램 API 상태 확인

### 데이터베이스 오류
- 파일 권한 확인
- 디스크 공간 확인

## 🔄 업데이트

### VC 목록 업데이트
`vc_monitor_enhanced.py`의 `top_vcs` 리스트에서 VC 추가/제거

### 스크래핑 규칙 업데이트
`vc_scraper.py`의 파싱 로직 수정

## 📈 성능 최적화

- 비동기 처리로 동시 요청 처리
- 데이터베이스 인덱싱으로 빠른 검색
- 중복 투자 정보 필터링

## 🔒 보안 고려사항

- 텔레그램 봇 토큰 보안 유지
- 데이터베이스 파일 접근 권한 제한
- 로그 파일에 민감한 정보 노출 방지

## 📞 지원

문제가 발생하거나 기능 개선이 필요한 경우:
1. 로그 파일 확인 (`vc_monitor_enhanced.log`)
2. 테스트 스크립트 실행으로 기능 검증
3. 데이터베이스 상태 확인

## 📝 라이선스

이 프로젝트는 교육 및 개인 사용 목적으로 제작되었습니다.










