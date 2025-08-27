#!/bin/bash

# Aave 거버넌스 모니터링 봇을 백그라운드에서 실행

echo "🚀 Aave 거버넌스 모니터링 봇 데몬 시작"
echo "======================================"

# 실행 권한 부여
chmod +x run_aave_monitor.sh

# 백그라운드에서 실행
nohup ./run_aave_monitor.sh > aave_monitor_daemon.log 2>&1 &

# 프로세스 ID 저장
echo $! > aave_monitor.pid

echo "✅ 모니터링 봇이 백그라운드에서 실행 중입니다."
echo "📋 프로세스 ID: $(cat aave_monitor.pid)"
echo "📝 로그 파일: aave_monitor_daemon.log"
echo "🛑 중지하려면: ./stop_aave_monitor_daemon.sh"


