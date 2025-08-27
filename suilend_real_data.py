#!/usr/bin/env python3
"""
실제 SUI 체인에서 Suilend 포지션 데이터를 가져오는 스크립트
"""

import requests
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class RealPosition:
    """실제 포지션 정보"""
    asset: str
    collateral_amount: float
    borrowed_amount: float
    ltv: float
    liquidation_threshold: float
    health_factor: float
    weighted_borrows: float
    liq_threshold: float

@dataclass
class RealWalletSummary:
    """실제 지갑 요약 정보"""
    total_collateral_usd: float
    total_borrowed_usd: float
    total_ltv: float
    health_factor: float
    positions: List[RealPosition]
    total_weighted_borrows: float
    total_liq_threshold: float

class SuilendRealDataFetcher:
    def __init__(self):
        self.rpc_url = "https://fullnode.mainnet.sui.io:443"
        self.wallet_address = "0x5a1051f618466d097272d1cc961f24ded3ebcc6e98384b5d06cadfd960ca58be"
        
        # Suilend 프로토콜 관련 주소들 (실제 주소로 업데이트 필요)
        self.suilend_package = "0x..."  # Suilend 패키지 주소
        self.market_registry = "0x..."  # 마켓 레지스트리
        
        # 자산별 가격 정보 (실제로는 Oracle에서 가져와야 함)
        self.asset_prices = {
            "USDC": 1.0,  # USDC는 1달러
            "ALKIMI": 0.0,  # ALKIMI 가격은 Oracle에서 가져와야 함
            "SUI": 0.0,  # SUI 가격은 Oracle에서 가져와야 함
        }
    
    def get_wallet_balance(self) -> List[Dict[str, Any]]:
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
            
            return []
            
        except Exception as e:
            print(f"잔액 조회 오류: {e}")
            return []
    
    def get_suilend_positions_from_events(self) -> List[Dict[str, Any]]:
        """Suilend 이벤트 로그에서 포지션 정보를 가져옵니다."""
        try:
            # Suilend 관련 이벤트 조회
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "suix_queryEvents",
                "params": [
                    {
                        "query": {
                            "MoveModule": {
                                "package": "0x...",  # Suilend 패키지 주소
                                "module": "market"
                            }
                        },
                        "limit": 100
                    }
                ]
            }
            
            response = requests.post(self.rpc_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data and 'data' in data['result']:
                    return data['result']['data']
            
            return []
            
        except Exception as e:
            print(f"Suilend 이벤트 조회 오류: {e}")
            return []
    
    def get_asset_price_from_oracle(self, asset: str) -> float:
        """Oracle에서 자산 가격을 가져옵니다."""
        try:
            # Pyth Network나 다른 Oracle에서 가격 가져오기
            if asset == "USDC":
                return 1.0
            elif asset == "ALKIMI":
                # ALKIMI 가격 조회 (실제 Oracle 주소 필요)
                return 0.0
            elif asset == "SUI":
                # SUI 가격 조회 (실제 Oracle 주소 필요)
                return 0.0
            else:
                return 0.0
                
        except Exception as e:
            print(f"가격 조회 오류: {e}")
            return 0.0
    
    def analyze_actual_position(self) -> RealWalletSummary:
        """실제 포지션을 분석합니다."""
        print("🔍 실제 Suilend 포지션 분석 중...")
        
        # 1. 지갑 잔액 확인
        balances = self.get_wallet_balance()
        
        # 2. Suilend 이벤트에서 포지션 정보 추출
        events = self.get_suilend_positions_from_events()
        
        # 3. 실제 포지션 분석 (현재는 잔액 기반으로 추정)
        positions = []
        total_collateral = 0.0
        total_borrowed = 0.0
        
        for balance in balances:
            coin_type = balance.get('coinType', '')
            total_balance = int(balance.get('totalBalance', '0'))
            
            if 'usdc::USDC' in coin_type.lower():
                # USDC는 담보로 사용됨
                usdc_amount = total_balance / 1e6  # USDC는 6자리 소수점
                collateral_value = usdc_amount * self.get_asset_price_from_oracle("USDC")
                total_collateral += collateral_value
                
                positions.append(RealPosition(
                    asset="USDC",
                    collateral_amount=collateral_value,
                    borrowed_amount=0.0,
                    ltv=0.0,
                    liquidation_threshold=0.85,  # 예상값
                    health_factor=1.0,
                    weighted_borrows=0.0,
                    liq_threshold=0.85
                ))
                
            elif 'alkimi::ALKIMI' in coin_type.lower():
                # ALKIMI는 대출받은 자산
                alkimi_amount = total_balance / 1e9  # ALKIMI는 9자리 소수점
                borrowed_value = alkimi_amount * self.get_asset_price_from_oracle("ALKIMI")
                total_borrowed += borrowed_value
                
                positions.append(RealPosition(
                    asset="ALKIMI",
                    collateral_amount=0.0,
                    borrowed_amount=borrowed_value,
                    ltv=0.0,
                    liquidation_threshold=0.0,
                    health_factor=0.0,
                    weighted_borrows=borrowed_value,
                    liq_threshold=0.0
                ))
        
        # LTV 계산
        total_ltv = total_borrowed / total_collateral if total_collateral > 0 else 0.0
        
        # 헬스 팩터 계산 (예상값)
        health_factor = 1.5 if total_ltv < 0.8 else 1.2 if total_ltv < 0.9 else 1.0
        
        return RealWalletSummary(
            total_collateral_usd=total_collateral,
            total_borrowed_usd=total_borrowed,
            total_ltv=total_ltv,
            health_factor=health_factor,
            positions=positions,
            total_weighted_borrows=total_borrowed,
            total_liq_threshold=0.85
        )
    
    def display_real_position(self):
        """실제 포지션을 표시합니다."""
        print(f"🔍 지갑 {self.wallet_address} 실제 Suilend 포지션")
        print("=" * 60)
        
        # 실제 포지션 분석
        summary = self.analyze_actual_position()
        
        print(f"💰 포지션 요약:")
        print(f"  • 총 담보: ${summary.total_collateral_usd:,.2f}")
        print(f"  • 총 대출: ${summary.total_borrowed_usd:,.2f}")
        print(f"  • 전체 LTV: {summary.total_ltv:.2%}")
        print(f"  • 헬스 팩터: {summary.health_factor:.2f}")
        print(f"  • 총 가중 대출: ${summary.total_weighted_borrows:,.2f}")
        print(f"  • 총 청산 임계값: {summary.total_liq_threshold:.2%}")
        
        print(f"\n📊 개별 포지션:")
        for i, pos in enumerate(summary.positions, 1):
            print(f"  {i}. {pos.asset}:")
            print(f"     • 담보: ${pos.collateral_amount:,.2f}")
            print(f"     • 대출: ${pos.borrowed_amount:,.2f}")
            print(f"     • LTV: {pos.ltv:.2%}")
            print(f"     • 청산 임계값: {pos.liquidation_threshold:.2%}")
            print(f"     • 헬스 팩터: {pos.health_factor:.2f}")
            print(f"     • 가중 대출: ${pos.weighted_borrows:,.2f}")
            print(f"     • 청산 임계값: {pos.liq_threshold:.2%}")
        
        print(f"\n⚠️  주의사항:")
        print(f"  • 현재는 잔액 기반으로 추정한 데이터입니다")
        print(f"  • 정확한 LTV와 헬스 팩터는 Suilend 컨트랙트에서 가져와야 합니다")
        print(f"  • 자산 가격은 Oracle에서 실시간으로 가져와야 합니다")

def main():
    fetcher = SuilendRealDataFetcher()
    fetcher.display_real_position()

if __name__ == "__main__":
    main() 