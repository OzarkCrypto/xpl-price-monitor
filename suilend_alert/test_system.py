#!/usr/bin/env python3
"""
Suilend LTV 모니터링 봇 전체 시스템 테스트
"""

import os
import sys
from dotenv import load_dotenv

def test_imports():
    """필요한 모듈들이 정상적으로 import되는지 테스트합니다."""
    print("🔍 모듈 import 테스트...")
    
    try:
        from suilend_api_client import SuilendAPIClient
        print("✅ suilend_api_client import 성공")
    except ImportError as e:
        print(f"❌ suilend_api_client import 실패: {e}")
        return False
    
    try:
        from notification_system import NotificationSystem
        print("✅ notification_system import 성공")
    except ImportError as e:
        print(f"❌ notification_system import 실패: {e}")
        return False
    
    try:
        from config import get_config, validate_config
        print("✅ config import 성공")
    except ImportError as e:
        print(f"❌ config import 실패: {e}")
        return False
    
    return True

def test_config():
    """설정 파일 테스트를 실행합니다."""
    print("\n🔧 설정 테스트...")
    
    try:
        from config import print_config_summary
        print_config_summary()
        return True
    except Exception as e:
        print(f"❌ 설정 테스트 실패: {e}")
        return False

def test_api_client():
    """API 클라이언트 테스트를 실행합니다."""
    print("\n🌐 API 클라이언트 테스트...")
    
    try:
        from suilend_api_client import test_api_client
        test_api_client()
        return True
    except Exception as e:
        print(f"❌ API 클라이언트 테스트 실패: {e}")
        return False

def test_notification_system():
    """알림 시스템 테스트를 실행합니다."""
    print("\n🔔 알림 시스템 테스트...")
    
    try:
        from notification_system import main as test_notifications
        test_notifications()
        return True
    except Exception as e:
        print(f"❌ 알림 시스템 테스트 실패: {e}")
        return False

def test_monitor():
    """모니터링 봇 테스트를 실행합니다."""
    print("\n📊 모니터링 봇 테스트...")
    
    try:
        from suilend_ltv_monitor import SuilendLTVMonitor
        
        # 모니터링 봇 인스턴스 생성
        monitor = SuilendLTVMonitor()
        print("✅ 모니터링 봇 인스턴스 생성 성공")
        
        # 한 번의 모니터링 실행
        print("🔄 단일 모니터링 테스트...")
        monitor.monitor_once()
        
        return True
    except Exception as e:
        print(f"❌ 모니터링 봇 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🧪 Suilend LTV 모니터링 봇 전체 시스템 테스트")
    print("=" * 60)
    
    # 환경 변수 로드
    load_dotenv()
    
    # 환경 변수 확인
    required_vars = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  다음 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        print("📝 env_template.txt를 참고하여 .env 파일을 생성하세요.")
        print("\n테스트를 계속하려면 Enter를 누르세요...")
        input()
    
    # 각 테스트 실행
    tests = [
        ("모듈 Import", test_imports),
        ("설정", test_config),
        ("API 클라이언트", test_api_client),
        ("알림 시스템", test_notification_system),
        ("모니터링 봇", test_monitor),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 예외 발생: {e}")
            results.append((test_name, False))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📋 테스트 결과 요약")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 통과" if success else "❌ 실패"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n전체: {passed}/{total} 테스트 통과")
    
    if passed == total:
        print("🎉 모든 테스트가 성공적으로 통과했습니다!")
        print("🚀 봇을 실행할 준비가 되었습니다.")
        print("\n실행 명령어:")
        print("  ./run_monitor.sh")
        print("  또는")
        print("  python suilend_ltv_monitor.py")
    else:
        print("⚠️  일부 테스트가 실패했습니다. 문제를 해결한 후 다시 시도하세요.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 