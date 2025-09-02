# Aave 거버넌스 포럼 모니터링 봇

Aave 거버넌스 포럼의 새로운 댓글과 활동을 모니터링하여 텔레그램으로 알림을 보내는 봇입니다.

## 🔍 모니터링 유형

### 1. **다중 포럼 모니터링** (`aave_multi_forum_monitor.py`)
- 특정 포럼들의 새로운 댓글과 활동 감지
- USDe, sUSDe, tUSDe PT 토큰 관련 포럼 모니터링

### 2. **PT/Onboard 키워드 모니터링** (`aave_pt_onboard_monitor.py`)
- "PT"와 "Onboard" 단어가 모두 포함된 새로운 토픽 감지
- 해당 토픽에 달린 새로운 댓글 감지
- **전체 거버넌스 포럼에서 키워드 기반 모니터링**
- **탐색 범위: 최근 2주 내 활동만**

## 🚀 주요 기능

- **실시간 모니터링**: Aave 거버넌스 포럼의 새로운 댓글과 활동 감지
- **텔레그램 알림**: 새로운 내용 발견 시 즉시 텔레그램으로 알림
- **다중 포럼 지원**: 여러 포럼을 동시에 모니터링
- **자동 실행**: GitHub Actions를 통해 1시간마다 자동 실행
- **중복 방지**: SQLite 데이터베이스로 중복 알림 방지

## 📋 모니터링 대상

### 다중 포럼 모니터링
1. **USDe November expiry PT tokens** - USDe November 만기 PT 토큰
2. **sUSDe November expiry PT tokens** - sUSDe November 만기 PT 토큰  
3. **tUSDe December expiry PT tokens** - tUSDe December 만기 PT 토큰

### PT/Onboard 키워드 모니터링
- **전체 거버넌스 포럼** (`https://governance.aave.com/c/governance/4`)
- "PT"와 "Onboard" 단어가 모두 포함된 모든 토픽
- **탐색 범위: 최근 2주 내 활동만**
- 해당 토픽의 새로운 댓글

## ⚙️ 설정 방법

### 1. GitHub Secrets 설정

GitHub 저장소의 Settings > Secrets and variables > Actions에서 다음을 설정:

- `TELEGRAM_TOKEN`: 텔레그램 봇 토큰
- `TELEGRAM_CHAT_ID`: 텔레그램 채팅 ID

### 2. 로컬 실행 (선택사항)

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
export TELEGRAM_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# 봇 실행
python aave_multi_forum_monitor.py
```

## 🔄 자동 실행

- **GitHub Actions**: 매시간 정각에 자동 실행 (UTC 기준)
- **수동 실행**: GitHub Actions 탭에서 `workflow_dispatch`로 수동 실행 가능

## 📊 알림 내용

### 다중 포럼 모니터링
#### 댓글 알림
- 포럼 이름
- 작성자
- 댓글 내용 (200자 제한)
- 작성 시간
- 링크

#### 활동 알림
- 포럼 이름
- 활동 유형
- 활동 설명
- 발생 시간
- 링크

### PT/Onboard 키워드 모니터링
#### 새로운 토픽 알림
- 제목
- 작성자
- 내용 (200자 제한)
- 마지막 활동 시간
- 링크

#### 새로운 댓글 알림
- 토픽 ID
- 작성자
- 댓글 내용 (300자 제한)
- 작성 시간
- 링크

## 🛠️ 기술 스택

- **Python 3.9+**
- **BeautifulSoup4**: HTML 파싱
- **Requests**: HTTP 요청
- **SQLite**: 데이터 저장
- **GitHub Actions**: 자동화

## 📝 로그

### 다중 포럼 모니터링
- `aave_multi_monitor.log`: 상세 로그 파일
- `aave_multi_monitor.db`: SQLite 데이터베이스

### PT/Onboard 키워드 모니터링
- `aave_pt_onboard_monitor.log`: 상세 로그 파일
- `aave_pt_onboard_monitor.db`: SQLite 데이터베이스

## 🔧 커스터마이징

### 새로운 포럼 추가

`aave_multi_forum_monitor.py`의 `FORUMS` 리스트에 추가:

```python
FORUMS = [
    # 기존 포럼들...
    {
        'name': '새로운 포럼',
        'url': 'https://governance.aave.com/t/새로운-포럼',
        'description': '새로운 포럼 설명'
    }
]
```

### 키워드 모니터링 설정

`aave_pt_onboard_monitor.py`의 `is_pt_onboard_topic()` 함수를 수정하여 다른 키워드 조합을 모니터링할 수 있습니다:

```python
def is_custom_topic(self, title: str, content: str) -> bool:
    title_lower = title.lower()
    content_lower = content.lower()
    
    # 원하는 키워드 조합 설정
    has_keyword1 = 'keyword1' in title_lower or 'keyword1' in content_lower
    has_keyword2 = 'keyword2' in title_lower or 'keyword2' in content_lower
    
    return has_keyword1 and has_keyword2
```

### 모니터링 간격 변경

`CHECK_INTERVAL` 값을 수정 (초 단위):
- 1시간: 3600
- 30분: 1800
- 15분: 900

## 📞 지원

문제가 발생하거나 기능 추가 요청이 있으시면 GitHub Issues를 통해 문의해주세요.

## �� 라이선스

MIT License
