#!/usr/bin/env python3
"""
SUI 체인에서 실제 지갑 정보를 확인하는 스크립트
"""

import requests
import json
from typing import Dict, Any, List

class SuiWalletChecker:
    def __init__(self):
        self.rpc_url = "https://fullnode.mainnet.sui.io:443"
        self.wallet_address = "0x5a1051f618466d097272d1cc961f24ded3ebcc6e98384b5d06cadfd960ca58be"
    
    def get_wallet_balance(self) -> Dict[str, Any]:
        """지갑의 모든 코인 잔액을 가져옵니다."""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "suix_getAllBalances",
                "params": [self.wallet_address]
            }
            
            response = requests.post(self.rpc_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    return data['result']
            
            return {}
            
        except Exception as e:
            print(f"잔액 조회 오류: {e}")
            return {}
    
    def check_actual_position(self):
        """실제 포지션을 확인합니다."""
        print(f"🔍 지갑 {self.wallet_address} 실제 상태 확인")
        print("=" * 60)
        
        # 1. 코인 잔액 확인
        print("💰 코인 잔액 확인 중...")
        balances = self.get_wallet_balance()
        
        if balances:
            print("✅ 코인 잔액 조회 성공:")
            for balance in balances:
                coin_type = balance.get('coinType', 'Unknown')
                total_balance = balance.get('totalBalance', '0')
                print(f"  - {coin_type}: {total_balance}")
        else:
            print("❌ 코인 잔액 조회 실패")
        
        # 2. 수동으로 알려주신 정보 표시
        print("\n📋 사용자가 알려주신 실제 포지션:")
        print("  - 담보: USDC")
        print("  - 대출: ALKIMI")
        print("  - 프로토콜: Suilend")
        
        print("\n⚠️  현재 코드는 모의 데이터를 사용하고 있습니다!")
        print("실제 데이터를 가져오려면 Suilend 프로토콜의 정확한 컨트랙트 주소가 필요합니다.")

def main():
    checker = SuiWalletChecker()
    checker.check_actual_position()

if __name__ == "__main__":
    main() 