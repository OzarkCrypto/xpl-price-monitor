#!/usr/bin/env python3
"""
Suilend LTV 모니터링 봇 설정 파일
"""

import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 기본 설정
DEFAULT_CONFIG = {
    # 모니터링 설정
    "MONITORING_INTERVAL": 5,  # 분 단위
    "MAX_CONSECUTIVE_FAILURES": 3,
    
    # LTV 임계값 (백분율)
    "LTV_WARNING_THRESHOLD": 0.8,      # 80% - 경고
    "LTV_DANGER_THRESHOLD": 0.9,       # 90% - 위험
    "LTV_LIQUIDATION_THRESHOLD": 0.95, # 95% - 청산 위험
    
    # 헬스 팩터 임계값
    "HEALTH_FACTOR_WARNING": 1.2,
    "HEALTH_FACTOR_DANGER": 1.1,
    "HEALTH_FACTOR_LIQUIDATION": 1.0,
    
    # 알림 설정
    "ENABLE_TELEGRAM": True,
    "ENABLE_DISCORD": False,
    "ENABLE_SLACK": False,
    "ENABLE_SOUND": True,
    "ENABLE_DESKTOP": True,
    "ENABLE_PHONE": True,
    
    # 로깅 설정
    "LOG_LEVEL": "INFO",
    "LOG_FILE": "suilend_monitor.log",
    "LOG_MAX_SIZE": 10 * 1024 * 1024,  # 10MB
    "LOG_BACKUP_COUNT": 5,
    
    # API 설정
    "SUILEND_API_URL": "https://api.suilend.com",
    "SUI_RPC_URL": "https://fullnode.mainnet.sui.io:443",
    "REQUEST_TIMEOUT": 30,
    "MAX_RETRIES": 3,
    
    # 알림 간격 제한 (스팸 방지)
    "MIN_ALERT_INTERVAL": 300,  # 5분
    "MAX_ALERTS_PER_HOUR": 10,
}

def get_config(key: str, default=None):
    """환경 변수에서 설정값을 가져옵니다."""
    return os.getenv(key, DEFAULT_CONFIG.get(key, default))

def get_ltv_thresholds():
    """LTV 임계값을 반환합니다."""
    return {
        "warning": float(get_config("LTV_WARNING_THRESHOLD", 0.8)),
        "danger": float(get_config("LTV_DANGER_THRESHOLD", 0.9)),
        "liquidation": float(get_config("LTV_LIQUIDATION_THRESHOLD", 0.95))
    }

def get_health_factor_thresholds():
    """헬스 팩터 임계값을 반환합니다."""
    return {
        "warning": float(get_config("HEALTH_FACTOR_WARNING", 1.2)),
        "danger": float(get_config("HEALTH_FACTOR_DANGER", 1.1)),
        "liquidation": float(get_config("HEALTH_FACTOR_LIQUIDATION", 1.0))
    }

def get_monitoring_config():
    """모니터링 설정을 반환합니다."""
    return {
        "interval_minutes": int(get_config("MONITORING_INTERVAL", 5)),
        "max_failures": int(get_config("MAX_CONSECUTIVE_FAILURES", 3)),
        "request_timeout": int(get_config("REQUEST_TIMEOUT", 30)),
        "max_retries": int(get_config("MAX_RETRIES", 3))
    }

def get_notification_config():
    """알림 설정을 반환합니다."""
    return {
        "telegram": bool(get_config("ENABLE_TELEGRAM", True)),
        "discord": bool(get_config("ENABLE_DISCORD", False)),
        "slack": bool(get_config("ENABLE_SLACK", False)),
        "sound": bool(get_config("ENABLE_SOUND", True)),
        "desktop": bool(get_config("ENABLE_DESKTOP", True)),
        "phone": bool(get_config("ENABLE_PHONE", True)),
        "min_interval": int(get_config("MIN_ALERT_INTERVAL", 300)),
        "max_per_hour": int(get_config("MAX_ALERTS_PER_HOUR", 10))
    }

def get_api_config():
    """API 설정을 반환합니다."""
    return {
        "suilend_url": get_config("SUILEND_API_URL", "https://api.suilend.com"),
        "sui_rpc_url": get_config("SUI_RPC_URL", "https://fullnode.mainnet.sui.io:443"),
        "timeout": int(get_config("REQUEST_TIMEOUT", 30))
    }

def get_logging_config():
    """로깅 설정을 반환합니다."""
    return {
        "level": get_config("LOG_LEVEL", "INFO"),
        "file": get_config("LOG_FILE", "suilend_monitor.log"),
        "max_size": int(get_config("LOG_MAX_SIZE", 10 * 1024 * 1024)),
        "backup_count": int(get_config("LOG_BACKUP_COUNT", 5))
    }

def validate_config():
    """설정값의 유효성을 검증합니다."""
    errors = []
    
    # 필수 환경 변수 확인
    required_vars = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    for var in required_vars:
        if not os.getenv(var):
            errors.append(f"필수 환경 변수 {var}가 설정되지 않았습니다.")
    
    # LTV 임계값 검증
    ltv_thresholds = get_ltv_thresholds()
    if not (0 < ltv_thresholds["warning"] < ltv_thresholds["danger"] < ltv_thresholds["liquidation"] < 1):
        errors.append("LTV 임계값이 올바르지 않습니다. (0 < warning < danger < liquidation < 1)")
    
    # 헬스 팩터 임계값 검증
    health_thresholds = get_health_factor_thresholds()
    if not (health_thresholds["liquidation"] < health_thresholds["danger"] < health_thresholds["warning"]):
        errors.append("헬스 팩터 임계값이 올바르지 않습니다. (liquidation < danger < warning)")
    
    # 모니터링 간격 검증
    interval = int(get_config("MONITORING_INTERVAL", 5))
    if interval < 1:
        errors.append("모니터링 간격은 최소 1분이어야 합니다.")
    
    return errors

def print_config_summary():
    """현재 설정을 요약하여 출력합니다."""
    print("🔧 Suilend LTV 모니터링 봇 설정 요약")
    print("=" * 50)
    
    # 모니터링 설정
    monitoring = get_monitoring_config()
    print(f"⏰ 모니터링 간격: {monitoring['interval_minutes']}분")
    print(f"🔄 최대 연속 실패: {monitoring['max_failures']}회")
    print(f"⏱️  요청 타임아웃: {monitoring['request_timeout']}초")
    
    # LTV 임계값
    ltv = get_ltv_thresholds()
    print(f"\n📊 LTV 임계값:")
    print(f"  - 경고: {ltv['warning']:.1%}")
    print(f"  - 위험: {ltv['danger']:.1%}")
    print(f"  - 청산: {ltv['liquidation']:.1%}")
    
    # 헬스 팩터 임계값
    health = get_health_factor_thresholds()
    print(f"\n💚 헬스 팩터 임계값:")
    print(f"  - 경고: {health['warning']:.1f}")
    print(f"  - 위험: {health['danger']:.1f}")
    print(f"  - 청산: {health['liquidation']:.1f}")
    
    # 알림 설정
    notifications = get_notification_config()
    print(f"\n🔔 알림 설정:")
    print(f"  - 텔레그램: {'활성화' if notifications['telegram'] else '비활성화'}")
    print(f"  - Discord: {'활성화' if notifications['discord'] else '비활성화'}")
    print(f"  - Slack: {'활성화' if notifications['slack'] else '비활성화'}")
    print(f"  - 소리: {'활성화' if notifications['sound'] else '비활성화'}")
    print(f"  - 데스크톱: {'활성화' if notifications['desktop'] else '비활성화'}")
    print(f"  - 전화: {'활성화' if notifications['phone'] else '비활성화'}")
    
    # 검증 오류 확인
    errors = validate_config()
    if errors:
        print(f"\n❌ 설정 오류:")
        for error in errors:
            print(f"  - {error}")
    else:
        print(f"\n✅ 설정이 유효합니다.")

if __name__ == "__main__":
    print_config_summary() 