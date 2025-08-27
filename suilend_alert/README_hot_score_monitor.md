# 🔥 Rootdata Hot Score 모니터

Rootdata에서 제공하는 프로젝트 인기도 지수(Hot Score)를 모니터링하고 텔레그램으로 전송하는 봇입니다.

## 📋 주요 기능

- **자동 모니터링**: 매시간 정각에 hot score TOP 10 자동 수집
- **텔레그램 알림**: 변경사항이 있을 때마다 텔레그램으로 전송
- **다중 채널 지원**: 여러 텔레그램 채널에 동시 전송
- **스마트 알림**: 데이터 변경사항이 있을 때만 알림 전송
- **프로젝트명 정리**: 긴 중국어 설명을 간단한 영문명으로 정리
- **개별 프로젝트 링크**: 각 프로젝트명을 클릭하면 해당 프로젝트의 Rootdata 영문 페이지로 이동
- **직접 링크**: Rootdata Projects 페이지로 바로 이동할 수 있는 링크 제공

## 🚀 설치 및 실행

### 1. 환경 변수 설정

`.env` 파일을 생성하고 다음 정보를 입력하세요:

```bash
# 텔레그램 봇 설정
ROOTDATA_BOT_TOKEN=your_telegram_bot_token_here
ROOTDATA_CHAT_ID=your_telegram_chat_id_here

# 추가 채널 (선택사항)
ROOTDATA_EXTRA_CHAT_ID=additional_chat_id_here

# 또는 일반 텔레그램 설정 사용
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 실행

#### 한 번만 실행 (테스트용)
```bash
python3 rootdata_hot_score_monitor.py --once
```

#### 지속 모니터링 (매시간 실행)
```bash
python3 rootdata_hot_score_monitor.py
```

#### 스크립트 사용
```bash
# 한 번 실행
./run_hot_score_once.sh

# 지속 모니터링
./run_hot_score_monitor.sh
```

## 📊 데이터 형식

### 텔레그램 메시지 예시

```
🔥 Rootdata Hot Score TOP 10 🔥
📅 2025-08-25 18:06:02

🥇 [YZY MONEY](https://rootdata.com/Projects/yzy-money)
   🔥 Hot Score: 538.0

🥈 [blind](https://rootdata.com/Projects/blind)
   🔥 Hot Score: 324.0

🥉 [Aubrai](https://rootdata.com/Projects/aubrai)
   🔥 Hot Score: 205.0

4️⃣ [Membit](https://rootdata.com/Projects/membit)
   🔥 Hot Score: 136.0

5️⃣ [Verso](https://rootdata.com/Projects/verso)
   🔥 Hot Score: 107.0

📊 Rootdata에서 제공하는 프로젝트 인기도 지수입니다.

🔗 [Rootdata Projects 바로가기](https://rootdata.com/Projects)
```

**참고**: 실제 텔레그램에서는 프로젝트명이 클릭 가능한 링크로 표시됩니다.

### 저장되는 데이터

- `rootdata_hot_score_history.json`: 이전 데이터와 비교용
- `rootdata_hot_score.log`: 실행 로그

## ⚙️ 설정 옵션

### 모니터링 간격
- 기본값: 매시간 정각
- `schedule.every().hour.at(":00")`에서 수정 가능

### 알림 조건
- TOP 3 프로젝트의 순위 변경
- Hot score 값이 0.1 이상 변경
- 새로운 프로젝트 등장

### 채널 설정
- 메인 채널: `ROOTDATA_CHAT_ID` 또는 `TELEGRAM_CHAT_ID`
- 추가 채널: `ROOTDATA_EXTRA_CHAT_ID`

## 🔧 커스터마이징

### 프로젝트명 매핑 추가

`ProjectNameCleaner` 클래스의 `name_mapping` 딕셔너리에 추가:

```python
self.name_mapping = {
    '긴 프로젝트명': '짧은 이름',
    'Another Long Name': 'Short Name',
    # ... 추가 매핑
}
```

### 알림 형식 수정

`format_telegram_message` 메서드를 수정하여 메시지 형식을 변경할 수 있습니다.

## 📝 로그 확인

```bash
# 실시간 로그 확인
tail -f rootdata_hot_score.log

# 최근 로그 확인
tail -20 rootdata_hot_score.log
```

## 🚨 문제 해결

### 환경 변수 로딩 실패
- `.env` 파일이 올바른 위치에 있는지 확인
- 파일 권한 확인
- 환경 변수명 오타 확인

### 텔레그램 전송 실패
- 봇 토큰 유효성 확인
- 채널 ID 확인
- 봇이 채널에 초대되었는지 확인

### 데이터 추출 실패
- Rootdata 웹사이트 접근 가능 여부 확인
- 네트워크 연결 상태 확인
- 웹사이트 구조 변경 여부 확인

## 📈 성능 최적화

- **캐싱**: 이전 데이터와 비교하여 불필요한 전송 방지
- **에러 처리**: 네트워크 오류 시 자동 재시도
- **로깅**: 상세한 실행 로그로 디버깅 지원

## 🔄 업데이트

### 자동 업데이트
- 매시간 정각에 자동 실행
- 변경사항이 있을 때만 알림 전송

### 수동 업데이트
```bash
python3 rootdata_hot_score_monitor.py --once
```

## 📞 지원

문제가 발생하거나 개선 사항이 있으면 이슈를 등록해주세요.

---

**참고**: 이 봇은 Rootdata 웹사이트의 구조 변경에 영향을 받을 수 있습니다. 정기적으로 테스트하고 필요시 코드를 업데이트하세요. 