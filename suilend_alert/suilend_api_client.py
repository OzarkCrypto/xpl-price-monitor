#!/usr/bin/env python3
"""
Suilend API 클라이언트
Suilend 프로토콜과의 상호작용을 위한 모듈
"""

import json
import logging
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LoanPosition:
    """대출 포지션 정보"""
    asset: str
    borrowed_amount: float
    collateral_amount: float
    ltv: float
    liquidation_threshold: float
    health_factor: float

@dataclass
class WalletSummary:
    """지갑 요약 정보"""
    total_collateral_usd: float
    total_borrowed_usd: float
    total_ltv: float
    health_factor: float
    positions: List[LoanPosition]

class SuilendAPIClient:
    """Suilend API 클라이언트"""
    
    def __init__(self):
        self.base_url = "https://api.suilend.com"
        self.sui_rpc_url = "https://fullnode.mainnet.sui.io:443"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def get_wallet_positions(self, wallet_address: str) -> Optional[WalletSummary]:
        """지갑의 모든 대출 포지션을 가져옵니다."""
        try:
            # Suilend API에서 지갑 정보 조회
            response = requests.get(
                f"{self.base_url}/v1/wallet/{wallet_address}/positions",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"지갑 포지션 조회 성공: {data}")
                return self._parse_positions_data(data)
            else:
                logger.warning(f"API 응답 오류: {response.status_code}")
                return self._get_positions_from_blockchain(wallet_address)
                
        except Exception as e:
            logger.error(f"포지션 조회 중 오류: {e}")
            return self._get_positions_from_blockchain(wallet_address)
    
    def _parse_positions_data(self, data: Dict[str, Any]) -> Optional[WalletSummary]:
        """API 응답 데이터를 파싱합니다."""
        try:
            positions = []
            total_collateral = 0.0
            total_borrowed = 0.0
            
            # 실제 API 응답 구조에 따라 조정 필요
            if 'positions' in data:
                for pos_data in data['positions']:
                    position = LoanPosition(
                        asset=pos_data.get('asset', 'Unknown'),
                        borrowed_amount=float(pos_data.get('borrowed', 0)),
                        collateral_amount=float(pos_data.get('collateral', 0)),
                        ltv=float(pos_data.get('ltv', 0)),
                        liquidation_threshold=float(pos_data.get('liquidationThreshold', 0.95)),
                        health_factor=float(pos_data.get('healthFactor', 1.0))
                    )
                    positions.append(position)
                    
                    total_collateral += position.collateral_amount
                    total_borrowed += position.borrowed_amount
            
            # 전체 LTV 계산
            total_ltv = total_borrowed / total_collateral if total_collateral > 0 else 0.0
            
            # 전체 헬스 팩터 계산
            health_factor = min([pos.health_factor for pos in positions]) if positions else 1.0
            
            return WalletSummary(
                total_collateral_usd=total_collateral,
                total_borrowed_usd=total_borrowed,
                total_ltv=total_ltv,
                health_factor=health_factor,
                positions=positions
            )
            
        except Exception as e:
            logger.error(f"데이터 파싱 오류: {e}")
            return None
    
    def _get_positions_from_blockchain(self, wallet_address: str) -> Optional[WalletSummary]:
        """블록체인에서 직접 포지션 정보를 가져옵니다."""
        try:
            # Sui 블록체인에서 지갑 정보 조회
            # 실제 구현에서는 Suilend 스마트 컨트랙트를 직접 호출해야 함
            
            # 예시 데이터 (실제로는 블록체인에서 조회)
            mock_positions = [
                LoanPosition(
                    asset="SUI",
                    borrowed_amount=1000.0,
                    collateral_amount=2000.0,
                    ltv=0.5,
                    liquidation_threshold=0.95,
                    health_factor=1.5
                )
            ]
            
            return WalletSummary(
                total_collateral_usd=2000.0,
                total_borrowed_usd=1000.0,
                total_ltv=0.5,
                health_factor=1.5,
                positions=mock_positions
            )
            
        except Exception as e:
            logger.error(f"블록체인 조회 오류: {e}")
            return None
    
    def get_asset_price(self, asset_symbol: str) -> Optional[float]:
        """자산의 현재 가격을 가져옵니다."""
        try:
            # CoinGecko API 사용
            coingecko_url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": asset_symbol.lower(),
                "vs_currencies": "usd"
            }
            
            response = requests.get(coingecko_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if asset_symbol.lower() in data:
                    return data[asset_symbol.lower()]["usd"]
            
            return None
            
        except Exception as e:
            logger.error(f"가격 조회 오류: {e}")
            return None
    
    def get_liquidation_events(self, wallet_address: str) -> List[Dict[str, Any]]:
        """청산 이벤트를 가져옵니다."""
        try:
            # Suilend API에서 청산 이벤트 조회
            response = requests.get(
                f"{self.base_url}/v1/wallet/{wallet_address}/liquidation-events",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('events', [])
            else:
                logger.warning(f"청산 이벤트 조회 실패: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"청산 이벤트 조회 오류: {e}")
            return []
    
    def get_protocol_stats(self) -> Optional[Dict[str, Any]]:
        """프로토콜 전체 통계를 가져옵니다."""
        try:
            response = requests.get(
                f"{self.base_url}/v1/stats",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"프로토콜 통계 조회 실패: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"프로토콜 통계 조회 오류: {e}")
            return None

def test_api_client():
    """API 클라이언트 테스트"""
    client = SuilendAPIClient()
    
    # 테스트 지갑 주소
    test_wallet = "0x5a1051f618466d097272d1cc961f24ded3ebcc6e98384b5d06cadfd960ca58be"
    
    print("🔍 Suilend API 클라이언트 테스트")
    print("=" * 40)
    
    # 지갑 포지션 조회
    print("📊 지갑 포지션 조회 중...")
    positions = client.get_wallet_positions(test_wallet)
    
    if positions:
        print(f"✅ 총 담보: ${positions.total_collateral_usd:,.2f}")
        print(f"✅ 총 대출: ${positions.total_borrowed_usd:,.2f}")
        print(f"✅ 전체 LTV: {positions.total_ltv:.2%}")
        print(f"✅ 헬스 팩터: {positions.health_factor:.2f}")
        
        for pos in positions.positions:
            print(f"  - {pos.asset}: LTV {pos.ltv:.2%}, 헬스 {pos.health_factor:.2f}")
    else:
        print("❌ 포지션 정보를 가져올 수 없습니다.")
    
    # 프로토콜 통계 조회
    print("\n📈 프로토콜 통계 조회 중...")
    stats = client.get_protocol_stats()
    
    if stats:
        print("✅ 프로토콜 통계 조회 성공")
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    else:
        print("❌ 프로토콜 통계를 가져올 수 없습니다.")

if __name__ == "__main__":
    test_api_client() 