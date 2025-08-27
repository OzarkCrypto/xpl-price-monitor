# 🚀 Suilend LTV 모니터링 봇

Suilend 프로토콜에서 특정 지갑의 LTV(Loan-to-Value)를 실시간으로 모니터링하고, 문제 발생 시 다양한 채널을 통해 즉시 알림을 보내는 봇입니다.

## ✨ 주요 기능

- 🔍 **실시간 LTV 모니터링**: 지정된 지갑의 LTV를 주기적으로 확인
- 🚨 **다단계 알림 시스템**: 경고, 위험, 청산 위험 단계별 알림
- 📱 **다양한 알림 채널**: 텔레그램, Discord, Slack, 소리, 데스크톱, 전화
- ⚡ **즉시 대응**: LTV 임계값 초과 시 즉시 알림
- 📊 **상세한 모니터링**: 담보, 대출, 헬스 팩터 등 포지션 정보 제공
- 🔧 **유연한 설정**: 환경 변수를 통한 쉬운 설정 관리

## 🎯 모니터링 대상

현재 모니터링 중인 지갑:
```
0x5a1051f618466d097272d1cc961f24ded3ebcc6e98384b5d06cadfd960ca58be
```

## 📋 요구사항

- Python 3.8+
- macOS (전화 알림 기능)
- 인터넷 연결
- 텔레그램 봇 토큰

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone <repository-url>
cd suilend-ltv-monitor
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate     # Windows
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
```bash
# env_template.txt를 .env로 복사
cp env_template.txt .env

# .env 파일 편집하여 실제 값 입력
nano .env
```

### 5. 봇 실행
```bash
# 쉘 스크립트 사용 (권장)
chmod +x run_monitor.sh
./run_monitor.sh

# 또는 직접 실행
python suilend_ltv_monitor.py
```

## ⚙️ 설정

### 환경 변수

| 변수명 | 설명 | 필수 | 기본값 |
|--------|------|------|--------|
| `TELEGRAM_BOT_TOKEN` | 텔레그램 봇 토큰 | ✅ | - |
| `TELEGRAM_CHAT_ID` | 텔레그램 채팅 ID | ✅ | - |
| `PHONE_NUMBER` | 전화번호 (선택사항) | ❌ | - |
| `MONITORING_INTERVAL` | 모니터링 간격 (분) | ❌ | 5 |
| `LTV_WARNING_THRESHOLD` | LTV 경고 임계값 | ❌ | 0.8 |
| `LTV_DANGER_THRESHOLD` | LTV 위험 임계값 | ❌ | 0.9 |
| `LTV_LIQUIDATION_THRESHOLD` | LTV 청산 임계값 | ❌ | 0.95 |

### LTV 임계값 설정

- **경고 (Warning)**: 80% - LTV가 높아지고 있음을 알림
- **위험 (Danger)**: 90% - 즉시 조치가 필요함을 알림
- **청산 위험 (Liquidation)**: 95% - 청산 위험이 매우 높음을 알림

## 🔔 알림 시스템

### 알림 채널

1. **텔레그램** (기본)
   - 실시간 메시지 전송
   - HTML 포맷 지원
   - 이모지와 함께 가독성 높은 메시지

2. **소리 알림**
   - macOS 시스템 사운드 사용
   - 상황별 다른 알림음

3. **데스크톱 알림**
   - macOS 알림 센터 사용
   - 화면에 팝업 표시

4. **전화 알림** (긴급 시)
   - FaceTime 앱을 통한 전화 시도
   - 청산 위험 시에만 활성화

### 알림 메시지 예시

```
🚨 Suilend LTV 긴급 알림 🚨

지갑: 0x5a1051f...
현재 LTV: 92.5%
상태: DANGER
헬스 팩터: 1.05
시간: 2024-01-15 14:30:25

⚠️ 위험 수준! LTV가 위험 수준에 도달했습니다!
```

## 📊 모니터링 데이터

### 수집 정보

- **총 담보 (USD)**: 지갑의 전체 담보 가치
- **총 대출 (USD)**: 지갑의 전체 대출 금액
- **전체 LTV**: 전체 포지션의 LTV 비율
- **헬스 팩터**: 포지션의 안전도 지표
- **개별 포지션**: 각 자산별 상세 정보

### 로그 파일

모니터링 결과는 `suilend_monitor.log` 파일에 저장됩니다:

```
2024-01-15 14:30:25 - INFO - 📊 LTV 모니터링 결과
============================================================
지갑: 0x5a1051f618466d097272d1cc961f24ded3ebcc6e98384b5d06cadfd960ca58be
시간: 2024-01-15 14:30:25
총 담보: $2,500.00
총 대출: $2,312.50
전체 LTV: 92.50%
헬스 팩터: 1.05
상태: DANGER
```

## 🧪 테스트

### 알림 시스템 테스트
```bash
python notification_system.py
```

### API 클라이언트 테스트
```bash
python suilend_api_client.py
```

### 설정 확인
```bash
python config.py
```

## 🔧 고급 설정

### 커스텀 임계값

`.env` 파일에서 LTV 임계값을 조정할 수 있습니다:

```bash
# LTV 임계값 (백분율)
LTV_WARNING_THRESHOLD=0.75      # 75%에서 경고
LTV_DANGER_THRESHOLD=0.85       # 85%에서 위험
LTV_LIQUIDATION_THRESHOLD=0.92  # 92%에서 청산 위험
```

### 모니터링 간격 조정

```bash
# 1분마다 모니터링 (빠른 응답)
MONITORING_INTERVAL=1

# 10분마다 모니터링 (리소스 절약)
MONITORING_INTERVAL=10
```

## 🚨 문제 해결

### 일반적인 문제

1. **텔레그램 알림이 오지 않음**
   - 봇 토큰과 채팅 ID 확인
   - 봇과의 대화 시작 확인

2. **API 연결 실패**
   - 인터넷 연결 확인
   - Suilend API 상태 확인

3. **소리 알림이 작동하지 않음**
   - 시스템 볼륨 확인
   - 알림 권한 확인

### 로그 확인

```bash
# 실시간 로그 모니터링
tail -f suilend_monitor.log

# 최근 로그 확인
tail -n 100 suilend_monitor.log
```

## 📱 텔레그램 봇 설정

### 1. 봇 생성
1. [@BotFather](https://t.me/botfather)에서 `/newbot` 명령어 사용
2. 봇 이름과 사용자명 설정
3. 봇 토큰 받기

### 2. 채팅 ID 확인
1. 봇과 대화 시작 (`/start`)
2. `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` 접속
3. `chat.id` 값 확인

### 3. 환경 변수 설정
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

## 🔒 보안 고려사항

- `.env` 파일을 Git에 커밋하지 마세요
- 봇 토큰을 안전하게 보관하세요
- 프로덕션 환경에서는 추가 보안 조치를 고려하세요

## 📈 성능 최적화

### 리소스 사용량

- **CPU**: 모니터링 간격에 따라 1-5%
- **메모리**: 약 50-100MB
- **네트워크**: 모니터링 간격에 따라 1-10KB/분

### 권장 설정

- **개발/테스트**: 1분 간격
- **프로덕션**: 5-10분 간격
- **저비용 운영**: 15-30분 간격

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## ⚠️ 면책 조항

이 도구는 교육 및 정보 제공 목적으로 제작되었습니다. 실제 투자 결정은 사용자의 책임이며, 개발자는 어떠한 금융 손실에 대해서도 책임지지 않습니다.

## 📞 지원

문제가 있거나 기능 요청이 있으시면:

1. GitHub Issues 생성
2. 로그 파일 첨부
3. 상세한 문제 설명

---

**Happy Monitoring! 🚀** 