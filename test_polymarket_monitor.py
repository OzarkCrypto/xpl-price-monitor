#!/usr/bin/env python3
"""
폴리마켓 모니터 테스트 스크립트
"""

import os
import sys
import json
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """필요한 모듈들이 정상적으로 import되는지 테스트"""
    try:
        import requests
        logger.info("✅ requests 모듈 import 성공")
    except ImportError as e:
        logger.error(f"❌ requests 모듈 import 실패: {e}")
        return False
    
    try:
        from notification_system import NotificationSystem
        logger.info("✅ notification_system 모듈 import 성공")
    except ImportError as e:
        logger.error(f"❌ notification_system 모듈 import 실패: {e}")
        return False
    
    try:
        from polymarket_monitor import PolymarketMonitor
        logger.info("✅ polymarket_monitor 모듈 import 성공")
    except ImportError as e:
        logger.error(f"❌ polymarket_monitor 모듈 import 실패: {e}")
        return False
    
    return True

def test_notification_system():
    """알림 시스템 테스트"""
    try:
        from notification_system import NotificationSystem
        
        notification = NotificationSystem()
        logger.info("✅ 알림 시스템 초기화 성공")
        
        # 텔레그램 설정 확인
        if notification.enable_telegram:
            logger.info("✅ 텔레그램 알림 활성화됨")
        else:
            logger.warning("⚠️ 텔레그램 알림 비활성화됨 (환경 변수 확인 필요)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 알림 시스템 테스트 실패: {e}")
        return False

def test_polymarket_api():
    """폴리마켓 API 연결 테스트"""
    try:
        import requests
        
        url = "https://clob.polymarket.com/markets"
        params = {"limit": 5, "offset": 0}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        logger.info("폴리마켓 API 연결 테스트 중...")
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get('markets', [])
            logger.info(f"✅ 폴리마켓 API 연결 성공 - {len(markets)}개 마켓 데이터 수신")
            
            if markets:
                sample_market = markets[0]
                logger.info(f"샘플 마켓: {sample_market.get('title', 'Unknown')}")
            
            return True
        else:
            logger.error(f"❌ 폴리마켓 API 오류: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 폴리마켓 API 테스트 실패: {e}")
        return False

def test_config_files():
    """설정 파일 테스트"""
    config_files = [
        'polymarket_config.json',
        '.env.template'
    ]
    
    all_exist = True
    for file_path in config_files:
        if os.path.exists(file_path):
            logger.info(f"✅ {file_path} 파일 존재")
        else:
            logger.warning(f"⚠️ {file_path} 파일 없음")
            all_exist = False
    
    return all_exist

def test_environment_variables():
    """환경 변수 테스트"""
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if os.getenv(var):
            logger.info(f"✅ {var} 환경 변수 설정됨")
        else:
            logger.warning(f"⚠️ {var} 환경 변수 설정되지 않음")
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"설정되지 않은 환경 변수: {', '.join(missing_vars)}")
        return False
    
    return True

def create_test_config():
    """테스트용 설정 파일 생성"""
    try:
        from polymarket_config import PolymarketConfig
        
        config = PolymarketConfig()
        config.create_default_config()
        logger.info("✅ 기본 설정 파일 생성 완료")
        return True
        
    except Exception as e:
        logger.error(f"❌ 설정 파일 생성 실패: {e}")
        return False

def run_all_tests():
    """모든 테스트 실행"""
    logger.info("=== 폴리마켓 모니터 테스트 시작 ===")
    
    tests = [
        ("모듈 Import 테스트", test_imports),
        ("설정 파일 테스트", test_config_files),
        ("환경 변수 테스트", test_environment_variables),
        ("알림 시스템 테스트", test_notification_system),
        ("폴리마켓 API 테스트", test_polymarket_api),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} 통과")
            else:
                logger.error(f"❌ {test_name} 실패")
        except Exception as e:
            logger.error(f"❌ {test_name} 오류 발생: {e}")
    
    logger.info(f"\n=== 테스트 결과: {passed}/{total} 통과 ===")
    
    if passed == total:
        logger.info("🎉 모든 테스트가 통과했습니다!")
        return True
    else:
        logger.warning(f"⚠️ {total - passed}개 테스트가 실패했습니다.")
        return False

def main():
    """메인 함수"""
    try:
        # 설정 파일이 없으면 생성
        if not os.path.exists('polymarket_config.json'):
            logger.info("기본 설정 파일을 생성합니다...")
            create_test_config()
        
        # 모든 테스트 실행
        success = run_all_tests()
        
        if success:
            logger.info("\n🚀 폴리마켓 모니터를 실행할 준비가 완료되었습니다!")
            logger.info("다음 명령어로 모니터링을 시작하세요:")
            logger.info("  python3 polymarket_monitor.py")
            logger.info("  또는")
            logger.info("  ./run_polymarket_monitor.sh")
        else:
            logger.error("\n❌ 일부 테스트가 실패했습니다. 문제를 해결한 후 다시 시도하세요.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n테스트가 중단되었습니다.")
    except Exception as e:
        logger.error(f"테스트 실행 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 