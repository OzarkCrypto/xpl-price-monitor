#!/usr/bin/env python3
"""
Rootdata Hot Index 정확한 정각 실행 스케줄러
매시간 정각에 정확하게 실행되도록 개선된 스케줄러
"""

import os
import sys
import time
import schedule
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rootdata_precise_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RootdataPreciseScheduler:
    def __init__(self):
        """정확한 정각 실행 스케줄러 초기화"""
        load_dotenv()
        
        # 모니터 스크립트 경로
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.monitor_script = os.path.join(self.script_dir, 'rootdata_hot_index_monitor.py')
        
        # Python 경로
        self.python_path = sys.executable
        
        logger.info(f"스케줄러 초기화 완료")
        logger.info(f"스크립트 디렉토리: {self.script_dir}")
        logger.info(f"모니터 스크립트: {self.monitor_script}")
        logger.info(f"Python 경로: {self.python_path}")

    def wait_until_next_hour(self):
        """다음 정각까지 대기"""
        now = datetime.now()
        next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        wait_seconds = (next_hour - now).total_seconds()
        
        logger.info(f"현재 시간: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"다음 실행 시간: {next_hour.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"대기 시간: {wait_seconds:.1f}초")
        
        time.sleep(wait_seconds)

    def run_monitor(self):
        """모니터 스크립트 실행"""
        try:
            logger.info("=" * 50)
            logger.info(f"정각 실행 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 50)
            
            # 모니터 스크립트 실행
            import subprocess
            result = subprocess.run([
                self.python_path, 
                self.monitor_script, 
                '--once'
            ], 
            capture_output=True, 
            text=True, 
            cwd=self.script_dir,
            timeout=300)  # 5분 타임아웃
            
            if result.returncode == 0:
                logger.info("✅ 모니터 스크립트 실행 성공")
                if result.stdout:
                    logger.info(f"출력: {result.stdout.strip()}")
            else:
                logger.error(f"❌ 모니터 스크립트 실행 실패 (코드: {result.returncode})")
                if result.stderr:
                    logger.error(f"오류: {result.stderr.strip()}")
                    
        except subprocess.TimeoutExpired:
            logger.error("❌ 모니터 스크립트 실행 타임아웃 (5분 초과)")
        except Exception as e:
            logger.error(f"❌ 모니터 스크립트 실행 중 오류: {e}")
        
        logger.info("=" * 50)

    def start_scheduler(self):
        """정확한 정각 실행 스케줄러 시작"""
        logger.info("🚀 Rootdata Hot Index 정확한 정각 실행 스케줄러 시작")
        
        # 첫 번째 실행을 위한 대기
        self.wait_until_next_hour()
        
        # 매시간 정각에 실행
        schedule.every().hour.at(":00").do(self.run_monitor)
        
        logger.info("✅ 스케줄러 설정 완료. 매시간 정각에 실행됩니다.")
        
        try:
            while True:
                # 현재 시간이 정각인지 확인
                now = datetime.now()
                if now.minute == 0 and now.second < 10:  # 정각 10초 이내
                    self.run_monitor()
                    time.sleep(60)  # 다음 분까지 대기
                else:
                    # 스케줄러 체크
                    schedule.run_pending()
                    time.sleep(1)  # 1초마다 체크
                    
        except KeyboardInterrupt:
            logger.info("🛑 스케줄러가 중단되었습니다.")
        except Exception as e:
            logger.error(f"❌ 스케줄러 실행 중 오류: {e}")

def main():
    """메인 함수"""
    try:
        scheduler = RootdataPreciseScheduler()
        scheduler.start_scheduler()
    except Exception as e:
        logger.error(f"스케줄러 초기화 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 