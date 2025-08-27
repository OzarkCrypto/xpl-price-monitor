# 🚀 Rootdata Hot Index 모니터 데몬 가이드

이 가이드는 **Rootdata Hot Index 모니터**를 백그라운드에서 실행하여, 노트북을 끄거나 커서를 끄도 계속 작동하도록 하는 방법을 설명합니다.

## 🎯 **주요 특징**

- ✅ **백그라운드 실행**: 터미널을 닫아도 계속 실행
- ✅ **자동 재시작**: 프로세스가 죽으면 자동으로 재시작
- ✅ **로그 관리**: 모든 실행 기록을 파일에 저장
- ✅ **간편한 관리**: 시작/중지/재시작/상태확인 스크립트 제공

## 📁 **파일 구조**

```
suilend_alert/
├── start_rootdata_daemon.sh      # 데몬 시작
├── stop_rootdata_daemon.sh       # 데몬 중지
├── check_rootdata_status.sh      # 상태 확인
├── restart_rootdata_daemon.sh    # 재시작
├── rootdata_hot_index_monitor.py # 메인 모니터 프로그램
├── rootdata_background.log       # 백그라운드 실행 로그
├── rootdata_monitor.pid          # 프로세스 ID 파일
└── README_rootdata_daemon.md     # 이 파일
```

## 🚀 **사용 방법**

### 1️⃣ **데몬 시작**
```bash
./start_rootdata_daemon.sh
```

### 2️⃣ **데몬 중지**
```bash
./stop_rootdata_daemon.sh
```

### 3️⃣ **상태 확인**
```bash
./check_rootdata_status.sh
```

### 4️⃣ **재시작**
```bash
./restart_rootdata_daemon.sh
```

## 📊 **상태 확인**

### **실행 중인지 확인**
```bash
ps aux | grep rootdata_hot_index_monitor
```

### **로그 실시간 확인**
```bash
tail -f rootdata_background.log
```

### **로그 전체 확인**
```bash
cat rootdata_background.log
```

## 🔧 **문제 해결**

### **프로세스가 응답하지 않는 경우**
```bash
# 강제 종료
pkill -9 -f rootdata_hot_index_monitor

# PID 파일 정리
rm -f rootdata_monitor.pid

# 다시 시작
./start_rootdata_daemon.sh
```

### **로그 파일이 너무 큰 경우**
```bash
# 로그 파일 백업
cp rootdata_background.log rootdata_background.log.backup

# 로그 파일 초기화
> rootdata_background.log
```

## ⚠️ **주의사항**

1. **환경 변수**: `.env` 파일에 `TELEGRAM_BOT_TOKEN`과 `TELEGRAM_CHAT_ID`가 설정되어 있어야 합니다.
2. **권한**: 모든 스크립트에 실행 권한이 있어야 합니다 (`chmod +x *.sh`).
3. **Python 패키지**: `requests`, `beautifulsoup4`, `schedule`, `python-dotenv`가 설치되어 있어야 합니다.

## 🎉 **이제 할 수 있는 것들**

- ✅ **노트북을 끄거나 커서를 끄도 모니터가 계속 실행됩니다!**
- ✅ **매시간 정각에 자동으로 Rootdata Hot Index TOP 10을 텔레그램으로 전송합니다!**
- ✅ **백그라운드에서 안전하게 실행됩니다!**
- ✅ **간단한 명령어로 시작/중지/재시작/상태확인이 가능합니다!**

## 💡 **추가 팁**

- **시스템 시작 시 자동 실행**: `launchd` (macOS) 또는 `systemd` (Linux)를 사용하여 시스템 부팅 시 자동으로 시작할 수 있습니다.
- **모니터링**: `check_rootdata_status.sh`를 cron으로 주기적으로 실행하여 모니터 상태를 확인할 수 있습니다.
- **알림**: 모니터가 중단되었을 때 알림을 받으려면 별도의 모니터링 스크립트를 만들 수 있습니다.

---

**🎯 이제 Rootdata Hot Index 모니터가 24/7 안전하게 실행됩니다!** 🚀 