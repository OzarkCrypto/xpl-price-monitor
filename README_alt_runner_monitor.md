# 🚀 알트 러너 모니터링 텔레그램 봇

알트 러너를 자동으로 찾아주는 모니터링 텔레그램 봇입니다.

## 📋 모니터링 조건

1. **코인베이스 상장**: 코인베이스에 상장되어 있어야 함
2. **거래량 폭증**: 도지(DOGE)보다 거래량이 많아야 함 (1.1배 이상)
3. **펀딩비 음수**: 바이낸스에서 펀딩비가 음수여야 함 (-0.1% 이하)

## 🛠️ 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements_alt_runner.txt
```

### 2. 텔레그램 설정 확인
`alt_runner_monitor.py` 파일에서 다음 설정을 확인하세요:
- `TELEGRAM_TOKEN`: 텔레그램 봇 토큰
- `CHAT_ID`: 알림을 받을 채팅 ID

## 🚀 사용법

### 즉시 실행 (한 번만)
```bash
python3 alt_runner_monitor.py
```

### 백그라운드 데몬으로 실행
```bash
# 데몬 시작
./start_alt_runner_daemon.sh

# 데몬 중지
./stop_alt_runner_daemon.sh

# 상태 확인
ps aux | grep alt_runner_monitor
```

### 쉘 스크립트로 실행
```bash
./run_alt_runner_monitor.sh
```

## 📊 모니터링 정보

### API 소스
- **코인베이스 상장**: CoinGecko API
- **거래량 데이터**: CoinGecko API  
- **펀딩비**: 바이낸스 Futures API

### 모니터링 간격
- 기본: 30분마다 자동 실행
- 설정 가능: `run_monitoring_loop(interval_minutes)` 파라미터로 조정

## 🔔 텔레그램 알림 예시

```
🚨 알트 러너 발견! 🚨

📊 도지 24시간 거래량: $123,456,789

🎯 발견된 알트 러너: 2개

1. BTC (Bitcoin)
   💰 24시간 거래량: $456,789,012
   📈 도지 대비: 3.70배
   📊 24시간 변화: 5.23%
   💸 펀딩비: -0.002500

2. ETH (Ethereum)
   💰 24시간 거래량: $234,567,890
   📈 도지 대비: 1.90배
   📊 24시간 변화: 3.45%
   💸 펀딩비: -0.001800

⏰ 발견 시간: 2024-01-15 14:30:25
```

## 📁 파일 구조

```
practice/
├── alt_runner_monitor.py          # 메인 모니터링 봇
├── requirements_alt_runner.txt    # 필요한 패키지 목록
├── run_alt_runner_monitor.sh      # 실행 스크립트
├── start_alt_runner_daemon.sh    # 데몬 시작 스크립트
├── stop_alt_runner_daemon.sh     # 데몬 중지 스크립트
├── alt_runner_monitor.log        # 로그 파일 (자동 생성)
└── alt_runner_monitor.pid        # PID 파일 (자동 생성)
```

## ⚙️ 설정 옵션

### 거래량 임계값 조정
```python
self.volume_threshold = 1.1  # 도지 대비 1.1배 이상
```

### 펀딩비 임계값 조정
```python
self.funding_rate_threshold = -0.001  # -0.1% 이하
```

### 모니터링 간격 조정
```python
await monitor.run_monitoring_loop(15)  # 15분마다
```

## 🚨 주의사항

1. **API 제한**: CoinGecko와 바이낸스 API 사용량 제한이 있을 수 있습니다
2. **네트워크**: 안정적인 인터넷 연결이 필요합니다
3. **텔레그램**: 봇 토큰과 채팅 ID가 올바르게 설정되어야 합니다

## 🔧 문제 해결

### 텔레그램 메시지가 전송되지 않는 경우
1. 봇 토큰이 올바른지 확인
2. 채팅 ID가 올바른지 확인
3. 봇이 채팅방에 추가되어 있는지 확인

### API 오류가 발생하는 경우
1. 인터넷 연결 상태 확인
2. API 서버 상태 확인
3. 로그 파일에서 오류 메시지 확인

## 📝 로그 확인

```bash
# 실시간 로그 확인
tail -f alt_runner_monitor.log

# 최근 로그 확인
tail -100 alt_runner_monitor.log
```

## 🤝 기여

버그 리포트나 기능 제안은 이슈로 등록해 주세요.

---

**⚠️ 투자 조언이 아닙니다. 이 도구는 정보 제공 목적으로만 사용하세요.** 