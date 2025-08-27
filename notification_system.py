#!/usr/bin/env python3
"""
알림 시스템 모듈
텔레그램, 전화, 소리 등 다양한 알림 방법을 제공합니다.
"""

import os
import logging
import requests
import subprocess
from typing import Optional, Dict, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class NotificationSystem:
    """알림 시스템 클래스"""
    
    def __init__(self):
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.phone_number = os.getenv("PHONE_NUMBER")
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        self.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        
        # 알림 설정
        self.enable_telegram = bool(self.telegram_bot_token and self.telegram_chat_id)
        self.enable_discord = bool(self.discord_webhook_url)
        self.enable_slack = bool(self.slack_webhook_url)
        self.enable_sound = True
        self.enable_desktop = True
        
        logger.info(f"알림 시스템 초기화 완료:")
        logger.info(f"  - 텔레그램: {'활성화' if self.enable_telegram else '비활성화'}")
        logger.info(f"  - Discord: {'활성화' if self.enable_discord else '비활성화'}")
        logger.info(f"  - Slack: {'활성화' if self.enable_slack else '비활성화'}")
        logger.info(f"  - 소리: {'활성화' if self.enable_sound else '비활성화'}")
        logger.info(f"  - 데스크톱: {'활성화' if self.enable_desktop else '비활성화'}")
    
    def send_telegram_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """텔레그램으로 메시지를 보냅니다."""
        if not self.enable_telegram:
            logger.warning("텔레그램이 비활성화되어 있습니다.")
            return False
            
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                logger.info("텔레그램 메시지 전송 성공")
                return True
            else:
                logger.error(f"텔레그램 전송 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"텔레그램 전송 오류: {e}")
            return False
    
    def send_discord_message(self, message: str, username: str = "Suilend Monitor") -> bool:
        """Discord로 메시지를 보냅니다."""
        if not self.enable_discord:
            logger.warning("Discord가 비활성화되어 있습니다.")
            return False
            
        try:
            payload = {
                "username": username,
                "content": message,
                "avatar_url": "https://suilend.com/favicon.ico"
            }
            
            response = requests.post(self.discord_webhook_url, json=payload, timeout=30)
            
            if response.status_code == 204:
                logger.info("Discord 메시지 전송 성공")
                return True
            else:
                logger.error(f"Discord 전송 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Discord 전송 오류: {e}")
            return False
    
    def send_slack_message(self, message: str, channel: str = "#alerts") -> bool:
        """Slack으로 메시지를 보냅니다."""
        if not self.enable_slack:
            logger.warning("Slack이 비활성화되어 있습니다.")
            return False
            
        try:
            payload = {
                "channel": channel,
                "text": message,
                "username": "Suilend Monitor",
                "icon_emoji": ":warning:"
            }
            
            response = requests.post(self.slack_webhook_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                logger.info("Slack 메시지 전송 성공")
                return True
            else:
                logger.error(f"Slack 전송 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Slack 전송 오류: {e}")
            return False
    
    def make_phone_call(self, phone_number: Optional[str] = None) -> bool:
        """전화를 걸어 알림을 보냅니다."""
        target_number = phone_number or self.phone_number
        
        if not target_number:
            logger.warning("전화번호가 설정되지 않았습니다.")
            return False
            
        try:
            # macOS에서 전화 앱 열기
            # 실제 전화는 Twilio 같은 서비스 사용 권장
            logger.info(f"전화번호 {target_number}로 전화 시도")
            
            # 전화 앱 열기 (macOS)
            subprocess.run([
                "open", 
                "-a", 
                "FaceTime", 
                f"tel:{target_number}"
            ], check=True)
            
            logger.info("전화 앱이 열렸습니다.")
            return True
            
        except Exception as e:
            logger.error(f"전화 알림 오류: {e}")
            return False
    
    def play_alarm_sound(self, sound_type: str = "warning") -> bool:
        """알람 소리를 재생합니다."""
        if not self.enable_sound:
            logger.warning("소리 알림이 비활성화되어 있습니다.")
            return False
            
        try:
            # macOS 시스템 사운드
            sound_files = {
                "warning": "/System/Library/Sounds/Ping.aiff",
                "danger": "/System/Library/Sounds/Sosumi.aiff",
                "critical": "/System/Library/Sounds/Glass.aiff"
            }
            
            sound_file = sound_files.get(sound_type, sound_files["warning"])
            
            if os.path.exists(sound_file):
                subprocess.run(["afplay", sound_file], check=True)
                logger.info(f"알람 소리 재생: {sound_type}")
                return True
            else:
                logger.warning(f"사운드 파일을 찾을 수 없습니다: {sound_file}")
                return False
                
        except Exception as e:
            logger.error(f"알람 소리 재생 오류: {e}")
            return False
    
    def show_desktop_notification(self, title: str, message: str, duration: int = 10) -> bool:
        """데스크톱 알림을 표시합니다."""
        if not self.enable_desktop:
            logger.warning("데스크톱 알림이 비활성화되어 있습니다.")
            return False
            
        try:
            # macOS에서 알림 표시
            subprocess.run([
                "osascript", 
                "-e", 
                f'display notification "{message}" with title "{title}"'
            ], check=True)
            
            logger.info("데스크톱 알림 표시 성공")
            return True
            
        except Exception as e:
            logger.error(f"데스크톱 알림 오류: {e}")
            return False
    
    def send_emergency_alert(self, alert_data: Dict[str, Any]) -> bool:
        """긴급 상황 알림을 모든 채널로 전송합니다."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 메시지 생성
        message = self._format_emergency_message(alert_data, timestamp)
        
        success_count = 0
        total_count = 0
        
        # 텔레그램 전송
        if self.enable_telegram:
            total_count += 1
            if self.send_telegram_message(message):
                success_count += 1
        
        # Discord 전송
        if self.enable_discord:
            total_count += 1
            if self.send_discord_message(message):
                success_count += 1
        
        # Slack 전송
        if self.enable_slack:
            total_count += 1
            if self.send_slack_message(message):
                success_count += 1
        
        # 소리 알림
        if self.enable_sound:
            self.play_alarm_sound("critical")
        
        # 데스크톱 알림
        if self.enable_desktop:
            self.show_desktop_notification(
                "🚨 Suilend 긴급 알림",
                f"LTV: {alert_data.get('ltv', 'N/A'):.2%} - 즉시 조치 필요!"
            )
        
        # 전화 알림 (긴급 상황에서만)
        if alert_data.get('status') == 'LIQUIDATION_IMMINENT':
            self.make_phone_call()
        
        logger.info(f"긴급 알림 전송 완료: {success_count}/{total_count} 성공")
        return success_count > 0
    
    def _format_emergency_message(self, alert_data: Dict[str, Any], timestamp: str) -> str:
        """긴급 상황 메시지를 포맷합니다."""
        wallet = alert_data.get('wallet_address', 'Unknown')
        ltv = alert_data.get('ltv', 0)
        status = alert_data.get('status', 'Unknown')
        health_factor = alert_data.get('health_factor', 0)
        total_weighted_borrows = alert_data.get('total_weighted_borrows', 0)
        total_liq_threshold = alert_data.get('total_liq_threshold', 0)
        
        # 상태별 이모지
        status_emoji = {
            'LIQUIDATION_IMMINENT': '🚨',
            'DANGER': '⚠️',
            'WARNING': '⚠️',
            'SAFE': '✅'
        }
        
        emoji = status_emoji.get(status, '❓')
        
        message = f"""
{emoji} <b>Suilend LTV 긴급 알림</b> {emoji}

<b>지갑:</b> {wallet[:10]}...
<b>현재 LTV:</b> {ltv:.2%}
<b>상태:</b> {status}
<b>헬스 팩터:</b> {health_factor:.2f}

<b>가중 대출 정보:</b>
• 총 가중 대출: ${total_weighted_borrows:,.2f}
• 총 청산 임계값: {total_liq_threshold:.2%}

<b>시간:</b> {timestamp}

"""
        
        if status == 'LIQUIDATION_IMMINENT':
            message += "🚨 <b>청산 위험!</b> 즉시 조치가 필요합니다! 🚨"
        elif status == 'DANGER':
            message += "⚠️ <b>위험 수준!</b> LTV가 위험 수준에 도달했습니다!"
        elif status == 'WARNING':
            message += "⚠️ <b>경고!</b> LTV가 경고 수준에 도달했습니다."
        
        return message
    
    def test_notifications(self):
        """모든 알림 채널을 테스트합니다."""
        print("🧪 알림 시스템 테스트 시작")
        print("=" * 40)
        
        test_data = {
            'wallet_address': '0x5a1051f618466d097272d1cc961f24ded3ebcc6e98384b5d06cadfd960ca58be',
            'ltv': 0.85,
            'status': 'WARNING',
            'health_factor': 1.2,
            'total_weighted_borrows': 1400.0,
            'total_liq_threshold': 0.90
        }
        
        # 각 알림 방법 테스트
        print("📱 텔레그램 테스트...")
        if self.send_telegram_message("🧪 테스트 메시지입니다."):
            print("✅ 텔레그램 테스트 성공")
        else:
            print("❌ 텔레그램 테스트 실패")
        
        print("\n🔔 소리 알림 테스트...")
        if self.play_alarm_sound("warning"):
            print("✅ 소리 알림 테스트 성공")
        else:
            print("❌ 소리 알림 테스트 실패")
        
        print("\n🖥️ 데스크톱 알림 테스트...")
        if self.show_desktop_notification("테스트", "알림 시스템 테스트입니다."):
            print("✅ 데스크톱 알림 테스트 성공")
        else:
            print("❌ 데스크톱 알림 테스트 실패")
        
        print("\n🚨 긴급 알림 테스트...")
        if self.send_emergency_alert(test_data):
            print("✅ 긴급 알림 테스트 성공")
        else:
            print("❌ 긴급 알림 테스트 실패")

def main():
    """메인 함수"""
    print("🔔 알림 시스템 테스트")
    print("=" * 30)
    
    # 환경 변수 확인
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        print("⚠️  TELEGRAM_BOT_TOKEN 환경 변수가 설정되지 않았습니다.")
        print("📝 env_template.txt를 참고하여 .env 파일을 생성하세요.")
        return
    
    # 알림 시스템 생성 및 테스트
    notification_system = NotificationSystem()
    notification_system.test_notifications()

if __name__ == "__main__":
    main() 