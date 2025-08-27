#!/usr/bin/env python3
"""
폴리마켓 모니터 설정 파일
"""

import os
from typing import Dict, Any

class PolymarketConfig:
    """폴리마켓 모니터 설정 클래스"""
    
    # 기본 설정
    DEFAULT_CONFIG = {
        # 모니터링 설정
        'check_interval': 60,  # 초 단위 (1분)
        'max_markets_per_check': 100,
        
        # 알림 설정
        'enable_new_market_alerts': True,
        'enable_market_updates': False,
        
        # 폴리마켓 API 설정
        'base_url': 'https://clob.polymarket.com',
        'markets_url': 'https://clob.polymarket.com/markets',
        
        # 로깅 설정
        'log_level': 'INFO',
        'log_file': 'polymarket_monitor.log',
        
        # 캐시 설정
        'cache_file': 'polymarket_known_markets.json',
        'cache_backup_count': 5,
        
        # 알림 템플릿 설정
        'alert_templates': {
            'new_market': {
                'emoji': '🚨',
                'title': '새로운 폴리마켓 마켓 발견!',
                'include_volume': True,
                'include_participants': True,
                'include_expiration': True
            },
            'market_update': {
                'emoji': '📈',
                'title': '폴리마켓 마켓 업데이트',
                'include_volume_change': True,
                'include_participants': True
            }
        }
    }
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or 'polymarket_config.json'
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """설정 파일을 로드합니다."""
        try:
            if os.path.exists(self.config_file):
                import json
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 기본 설정과 사용자 설정을 병합
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(user_config)
                    return config
            else:
                return self.DEFAULT_CONFIG.copy()
        except Exception as e:
            print(f"설정 파일 로드 오류: {e}")
            return self.DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """설정을 파일에 저장합니다."""
        try:
            import json
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print(f"설정이 {self.config_file}에 저장되었습니다.")
        except Exception as e:
            print(f"설정 저장 오류: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """설정 값을 가져옵니다."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """설정 값을 설정합니다."""
        self.config[key] = value
    
    def create_default_config(self):
        """기본 설정 파일을 생성합니다."""
        try:
            import json
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
            print(f"기본 설정 파일이 {self.config_file}에 생성되었습니다.")
        except Exception as e:
            print(f"기본 설정 파일 생성 오류: {e}")
    
    def show_config(self):
        """현재 설정을 출력합니다."""
        print("=== 폴리마켓 모니터 설정 ===")
        for key, value in self.config.items():
            print(f"{key}: {value}")
        print("==========================")

def create_env_template():
    """환경 변수 템플릿 파일을 생성합니다."""
    env_content = """# 폴리마켓 모니터 환경 변수 설정

# 텔레그램 설정
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# 모니터링 설정
POLYMARKET_CHECK_INTERVAL=60
POLYMARKET_MAX_MARKETS=100

# 알림 설정
ENABLE_NEW_MARKET_ALERTS=true
ENABLE_MARKET_UPDATES=false

# 로깅 설정
LOG_LEVEL=INFO
LOG_FILE=polymarket_monitor.log

# API 설정
POLYMARKET_API_TIMEOUT=30
POLYMARKET_MAX_RETRIES=3
"""
    
    try:
        with open('.env.template', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(".env.template 파일이 생성되었습니다.")
        print("이 파일을 .env로 복사하고 실제 값으로 수정하세요.")
    except Exception as e:
        print(f"환경 변수 템플릿 생성 오류: {e}")

if __name__ == "__main__":
    # 기본 설정 파일 생성
    config = PolymarketConfig()
    config.create_default_config()
    
    # 환경 변수 템플릿 생성
    create_env_template()
    
    print("\n설정이 완료되었습니다!")
    print("1. .env.template을 .env로 복사하고 텔레그램 봇 토큰과 채팅 ID를 설정하세요.")
    print("2. polymarket_config.json에서 모니터링 설정을 조정하세요.")
    print("3. python polymarket_monitor.py로 모니터링을 시작하세요.") 