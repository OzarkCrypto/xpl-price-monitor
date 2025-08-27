#!/usr/bin/env python3
"""
Rootdata Hot Index 모니터 테스트 프로그램
설정과 기본 기능을 테스트합니다.
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """환경 변수 설정을 테스트합니다."""
    print("🔧 환경 변수 테스트...")
    
    load_dotenv()
    
    required_vars = ["ROOTDATA_BOT_TOKEN", "ROOTDATA_CHAT_ID"]
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if var == "ROOTDATA_CHAT_ID":
                print(f"✅ {var}: {value}")
            else:
                print(f"✅ {var}: {value[:10]}...")
        else:
            print(f"❌ {var}: 설정되지 않음")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  다음 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        print("📝 .env 파일을 확인하고 필요한 환경 변수를 설정하세요.")
        return False
    
    print("✅ 모든 환경 변수가 설정되었습니다.")
    return True

def test_imports():
    """필요한 모듈들이 정상적으로 import되는지 테스트합니다."""
    print("\n🔍 모듈 import 테스트...")
    
    try:
        import requests
        print("✅ requests import 성공")
    except ImportError as e:
        print(f"❌ requests import 실패: {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✅ beautifulsoup4 import 성공")
    except ImportError as e:
        print(f"❌ beautifulsoup4 import 실패: {e}")
        return False
    
    try:
        import schedule
        print("✅ schedule import 성공")
    except ImportError as e:
        print(f"❌ schedule import 실패: {e}")
        return False
    
    try:
        from rootdata_hot_index_monitor import RootdataHotIndexMonitor
        print("✅ rootdata_hot_index_monitor import 성공")
        return True
    except ImportError as e:
        print(f"❌ rootdata_hot_index_monitor import 실패: {e}")
        return False

def test_monitor_initialization():
    """모니터 초기화를 테스트합니다."""
    print("\n🚀 모니터 초기화 테스트...")
    
    try:
        from rootdata_hot_index_monitor import RootdataHotIndexMonitor
        monitor = RootdataHotIndexMonitor()
        print("✅ RootdataHotIndexMonitor 초기화 성공")
        return True
    except Exception as e:
        print(f"❌ 모니터 초기화 실패: {e}")
        return False

def test_single_monitoring():
    """단일 모니터링을 테스트합니다."""
    print("\n📊 단일 모니터링 테스트...")
    
    try:
        from rootdata_hot_index_monitor import RootdataHotIndexMonitor
        monitor = RootdataHotIndexMonitor()
        
        print("🔄 모니터링 실행 중...")
        monitor.monitor_once()
        
        print("✅ 단일 모니터링 테스트 성공")
        return True
    except Exception as e:
        print(f"❌ 단일 모니터링 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🧪 Rootdata Hot Index 모니터 테스트")
    print("=" * 50)
    
    # 환경 변수 테스트
    if not test_environment():
        print("\n❌ 환경 변수 테스트 실패")
        print("📝 .env 파일을 설정한 후 다시 시도하세요.")
        return False
    
    # 모듈 import 테스트
    if not test_imports():
        print("\n❌ 모듈 import 테스트 실패")
        print("📦 필요한 패키지를 설치하세요: pip install -r requirements.txt")
        return False
    
    # 모니터 초기화 테스트
    if not test_monitor_initialization():
        print("\n❌ 모니터 초기화 테스트 실패")
        return False
    
    # 단일 모니터링 테스트
    if not test_single_monitoring():
        print("\n❌ 단일 모니터링 테스트 실패")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 모든 테스트가 성공적으로 통과했습니다!")
    print("🚀 모니터를 실행할 준비가 되었습니다.")
    print("\n실행 명령어:")
    print("  ./run_rootdata_monitor.sh")
    print("  또는")
    print("  python3 rootdata_hot_index_monitor.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 