# Crypto Fundraising Monitor

자동으로 [crypto-fundraising.info](https://crypto-fundraising.info/)의 신규 프로젝트를 모니터링하고 텔레그램으로 요약을 전송하는 시스템입니다.

## 🎯 주요 기능

- 🔍 **자동 스크래핑**: crypto-fundraising.info에서 매일 신규 프로젝트 수집
- 📊 **투자자 품질 점수**: VC 티어별 자동 점수 계산 및 하이라이트
- 📱 **텔레그램 알림**: 신규 프로젝트를 3줄 형식으로 자동 전송
- 💾 **중복 방지**: SQLite를 통한 상태 관리로 중복 알림 방지
- ✂️ **자동 분할**: 4096자 제한 초과 시 메시지 자동 분할
- 🕐 **정기 실행**: GitHub Actions 또는 cron을 통한 자동화

## 📱 메시지 형식

각 프로젝트는 다음 3줄 형식으로 표시됩니다:

```
프로젝트: {프로젝트명}        # 하이라이트면 굵게 처리
Raise amount: ${금액_USD}
Investors: {투자자1, 투자자2, ...}
```

### 하이라이트 규칙

투자자 품질 점수가 임계값(기본: 7점) 이상인 프로젝트는 **굵게** 표시됩니다.

## 🏆 투자자 품질 점수 체계

### T1 (5점) - 최고 티어
- a16z, Sequoia, Paradigm, Polychain, Dragonfly, Pantera
- Multicoin, Jump, Framework, Bain, Lightspeed, Coinbase Ventures
- CoinFund, Hypersphere, Lightspeed Faction

### T2 (3점) - 고품질 티어
- HashKey, Electric, Hashed, DCG, Sky9, Spartan, Animoca
- NFX, Shima, Placeholder, Variant, Mirana Ventures, Offchain Labs
- Polygon, Yunqi Partners, Tykhe Ventures, Varrock, Echo, Breed VC
- WAGMI Ventures, Veris Ventures, CRIT Ventures

### T3 (2점) - 중간 티어
- Y Combinator (YC), Techstars, OKX Ventures, Binance Labs
- SBI Holdings, 13bookscapital, Mark Ransford

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
pip install -r requirements_crypto_fundraising.txt
```

### 2. 환경 변수 설정

```bash
cp env_template.txt .env
```

`.env` 파일 편집:
```env
TELEGRAM_BOT_TOKEN=your_actual_bot_token
TELEGRAM_CHAT_ID=1339285013
HIGHLIGHT_THRESHOLD=7
RUN_TIMEZONE=Asia/Seoul
```

### 3. 텔레그램 봇 설정

1. [@BotFather](https://t.me/botfather)에서 새 봇 생성
2. 봇 토큰을 `.env`에 설정
3. 봇을 원하는 채팅방에 초대
4. 채팅방 ID를 `TELEGRAM_CHAT_ID`에 설정

### 4. 시스템 테스트

```bash
python3 test_system.py
```

### 5. 실행

```bash
# 수동 실행
python3 crypto_fundraising_monitor/run.py

# 또는 실행 스크립트 사용
./run_crypto_fundraising.sh
```

## 📁 프로젝트 구조

```
crypto_fundraising_monitor/
├── __init__.py              # 패키지 초기화
├── config.py                # 설정 및 VC 티어 정의
├── models.py                # 데이터 모델 (Pydantic)
├── scraper.py               # 웹 스크래핑 로직
├── scoring.py               # 투자자 품질 점수 계산
├── storage.py               # SQLite 상태 관리
├── notify.py                # 텔레그램 알림 전송
├── main.py                  # 메인 모니터링 로직
└── run.py                   # 독립 실행 스크립트

# 실행 및 설정 파일들
├── run_crypto_fundraising.sh    # 실행 스크립트
├── setup_cron.sh                # Cron 설정 스크립트
├── requirements_crypto_fundraising.txt  # 의존성
├── env_template.txt              # 환경변수 템플릿
├── .env                          # 환경변수 (사용자 생성)
└── README_crypto_fundraising.md  # 이 파일
```

## ⚙️ 자동화 실행

### GitHub Actions (권장)

`.github/workflows/crypto_fundraising.yml` 파일이 이미 포함되어 있습니다.

GitHub Secrets에 다음을 설정하세요:
- `TELEGRAM_BOT_TOKEN`: 텔레그램 봇 토큰
- `TELEGRAM_CHAT_ID`: 채팅방 ID

### Cron (로컬/서버)

자동 설정:
```bash
./setup_cron.sh
```

수동 설정:
```bash
crontab -e

# 매일 오전 9시 실행 (한국시간)
0 9 * * * cd /path/to/project && python3 crypto_fundraising_monitor/run.py
```

## 🔧 설정 커스터마이징

### VC 티어 수정

`crypto_fundraising_monitor/config.py`에서 `VC_TIERS` 딕셔너리 수정:

```python
VC_TIERS = {
    'T1': {  # +5점
        'your_vc_name', 'another_vc'
    },
    'T2': {  # +3점
        'medium_tier_vc'
    },
    'T3': {  # +2점
        'lower_tier_vc'
    }
}
```

### 하이라이트 임계값 조정

`.env` 파일에서 `HIGHLIGHT_THRESHOLD` 값 수정:

```env
HIGHLIGHT_THRESHOLD=10  # 더 높은 품질만 하이라이트
```

## 📊 모니터링 및 로깅

### 로그 파일

- `crypto_fundraising_monitor.log`: 상세 실행 로그
- `crypto_fundraising_state.db`: SQLite 상태 데이터베이스

### 로그 레벨

- INFO: 일반 실행 정보
- WARNING: 경고 메시지
- ERROR: 오류 및 실패 정보

## 🧪 테스트

### 전체 시스템 테스트

```bash
python3 test_system.py
```

### 개별 모듈 테스트

```bash
# VC 점수 계산 테스트
python3 test_crypto_fundraising.py

# 스크래퍼 테스트
python3 test_scraper.py

# VC 매칭 테스트
python3 debug_vc_matching.py
```

## 🚨 문제 해결

### 일반적인 문제

1. **텔레그램 연결 실패**
   - 봇 토큰이 올바른지 확인
   - 봇이 채팅방에 초대되었는지 확인

2. **스크래핑 실패**
   - 웹사이트 구조 변경 가능성
   - 네트워크 연결 상태 확인

3. **중복 알림**
   - 데이터베이스 파일 권한 확인
   - `crypto_fundraising_state.db` 파일 상태 확인

### 디버깅

더 자세한 로그를 보려면 `main.py`에서 로그 레벨을 `DEBUG`로 변경:

```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## 🔒 보안 주의사항

- **절대** `.env` 파일을 Git에 커밋하지 마세요
- 텔레그램 봇 토큰을 안전하게 관리하세요
- GitHub Actions Secrets를 사용하여 민감한 정보 보호

## 📈 성능 및 확장성

### 현재 성능

- 스크래핑: ~10-15초
- 점수 계산: ~1초
- 텔레그램 전송: ~2-5초
- 총 실행 시간: ~15-25초

### 확장 가능성

- 새로운 VC 티어 추가
- 추가 웹사이트 지원
- 다양한 알림 채널 (Slack, Discord 등)
- 고급 분석 및 리포트

## 🤝 기여

버그 리포트나 기능 제안은 이슈로 등록해 주세요.

### 개발 환경 설정

```bash
# 가상환경 생성
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements_crypto_fundraising.txt

# 개발 모드로 설치
pip install -e .
```

## 📄 라이선스

이 프로젝트는 교육 및 개인 사용 목적으로 제작되었습니다.

## 🎉 완성된 기능

✅ [AC1] python main.py 실행 시, 당일 기준 신규 항목이 텔레그램으로 전송된다.  
✅ [AC2] 모든 신규 항목이 3줄 포맷으로 나열되며, 임계값 이상만 프로젝트명이 굵게 표시된다.  
✅ [AC3] 같은 항목은 이후 실행에서 중복 전송되지 않는다(sqlite로 판별).  
✅ [AC4] 4096자 제한 상황에서도 메시지가 자동으로 여러 개로 분할되어 전송된다.  
✅ [AC5] .env 미설정 시 친절한 에러를 내고 종료한다.  
✅ [AC6] VC 티어 리스트/임계값을 코드 상단 또는 설정 값으로 쉽게 바꿀 수 있다.  
✅ [AC7] 사이트 구조가 소폭 변해도, 스크레이퍼에서 소수의 셀렉터 교체만으로 복구 가능하다.  

모든 Acceptance Criteria가 충족되었습니다! 🎯 