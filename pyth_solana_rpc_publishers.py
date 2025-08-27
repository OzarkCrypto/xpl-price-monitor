#!/usr/bin/env python3
"""
Solana RPC를 사용한 PYTH 퍼블리셔 정보 가져오기
Solana RPC를 통해 Pyth 프로그램 계정 정보를 가져와서 퍼블리셔 정보를 추출합니다.
"""

import requests
import json
import time
import csv
import base64
import struct
from typing import Dict, List, Optional

class PythSolanaRPCPublishers:
    def __init__(self):
        self.rpc_url = "https://api.mainnet-beta.solana.com"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
        
        # Pyth 프로그램 ID
        self.pyth_program_id = "Pyth11111111111111111111111111111111111111112"
    
    def call_solana_rpc(self, method: str, params: List) -> Dict:
        """Solana RPC를 호출합니다."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        
        try:
            response = self.session.post(self.rpc_url, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ RPC 호출 실패: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"💥 RPC 호출 오류: {e}")
            return None
    
    def get_pyth_program_accounts(self) -> Dict:
        """Pyth 프로그램의 모든 계정을 가져옵니다."""
        print("🔍 Pyth 프로그램 계정 가져오는 중...")
        
        params = [
            self.pyth_program_id,
            {
                "encoding": "base64",
                "filters": [
                    {
                        "dataSize": 1000  # 큰 데이터 크기의 계정들
                    }
                ]
            }
        ]
        
        result = self.call_solana_rpc("getProgramAccounts", params)
        
        if result and 'result' in result:
            accounts = result['result']
            print(f"✅ {len(accounts)}개의 Pyth 계정을 찾았습니다.")
            return accounts
        else:
            print("❌ Pyth 계정을 가져올 수 없습니다.")
            return []
    
    def get_pyth_price_accounts(self) -> Dict:
        """Pyth 가격 계정들을 가져옵니다."""
        print("🔍 Pyth 가격 계정 가져오는 중...")
        
        # 더 구체적인 필터로 가격 계정 찾기
        params = [
            self.pyth_program_id,
            {
                "encoding": "base64",
                "filters": [
                    {
                        "dataSize": 2000  # 가격 계정은 더 큼
                    }
                ]
            }
        ]
        
        result = self.call_solana_rpc("getProgramAccounts", params)
        
        if result and 'result' in result:
            accounts = result['result']
            print(f"✅ {len(accounts)}개의 가격 계정을 찾았습니다.")
            return accounts
        else:
            print("❌ 가격 계정을 가져올 수 없습니다.")
            return []
    
    def parse_pyth_account_data(self, account_data: str) -> Dict:
        """Pyth 계정 데이터를 파싱합니다."""
        try:
            # Base64 디코딩
            decoded_data = base64.b64decode(account_data)
            
            if len(decoded_data) < 8:
                return {}
            
            # Pyth 계정 구조 분석
            # 첫 8바이트는 계정 타입
            account_type = decoded_data[:8]
            
            # 계정 타입에 따른 파싱
            if account_type == b'price\x00\x00\x00':
                return self.parse_price_account(decoded_data)
            elif account_type == b'product\x00':
                return self.parse_product_account(decoded_data)
            elif account_type == b'mapping\x00':
                return self.parse_mapping_account(decoded_data)
            else:
                return {
                    'account_type': account_type.hex(),
                    'data_size': len(decoded_data)
                }
                
        except Exception as e:
            print(f"💥 계정 데이터 파싱 실패: {e}")
            return {}
    
    def parse_price_account(self, data: bytes) -> Dict:
        """가격 계정 데이터를 파싱합니다."""
        try:
            if len(data) < 100:
                return {}
            
            # 가격 계정 구조 (간단한 버전)
            result = {
                'account_type': 'price',
                'data_size': len(data),
                'publishers': []
            }
            
            # 퍼블리셔 정보 추출 시도
            # 실제 Pyth 구조에서는 퍼블리셔 정보가 특정 위치에 있음
            publisher_count = 0
            
            # 데이터에서 32바이트 청크들을 퍼블리셔 공개키로 간주
            for i in range(0, min(len(data), 1000), 32):
                if i + 32 <= len(data):
                    chunk = data[i:i+32]
                    if any(b != 0 for b in chunk):  # 0이 아닌 바이트가 있는 경우
                        publisher_count += 1
                        result['publishers'].append({
                            'index': publisher_count,
                            'public_key': chunk.hex(),
                            'public_key_short': chunk.hex()[:16] + "..."
                        })
            
            result['publisher_count'] = publisher_count
            return result
            
        except Exception as e:
            print(f"💥 가격 계정 파싱 실패: {e}")
            return {}
    
    def parse_product_account(self, data: bytes) -> Dict:
        """상품 계정 데이터를 파싱합니다."""
        return {
            'account_type': 'product',
            'data_size': len(data)
        }
    
    def parse_mapping_account(self, data: bytes) -> Dict:
        """매핑 계정 데이터를 파싱합니다."""
        return {
            'account_type': 'mapping',
            'data_size': len(data)
        }
    
    def find_btc_price_account(self, accounts: List[Dict]) -> Optional[Dict]:
        """BTC 가격 계정을 찾습니다."""
        print("🔍 BTC 가격 계정 찾는 중...")
        
        for account in accounts:
            try:
                # 계정 데이터 파싱
                account_data = account.get('account', {}).get('data', [])
                if isinstance(account_data, list) and len(account_data) > 0:
                    parsed_data = self.parse_pyth_account_data(account_data[0])
                    
                    # BTC 관련 계정 찾기
                    if parsed_data.get('account_type') == 'price':
                        # 계정 크기나 다른 속성으로 BTC 계정 식별
                        if parsed_data.get('data_size', 0) > 1000:
                            print(f"✅ 잠재적 BTC 가격 계정 발견: {account.get('pubkey', 'Unknown')}")
                            return {
                                'account': account,
                                'parsed_data': parsed_data
                            }
            except Exception as e:
                continue
        
        print("❌ BTC 가격 계정을 찾을 수 없습니다.")
        return None
    
    def get_btc_publishers(self) -> Dict:
        """BTC 피드의 퍼블리셔 정보를 가져옵니다."""
        print("🚀 Solana RPC를 사용한 BTC 피드 퍼블리셔 정보 가져오기")
        print("=" * 70)
        
        # 1. Pyth 프로그램 계정 가져오기
        pyth_accounts = self.get_pyth_program_accounts()
        if not pyth_accounts:
            return {
                'success': False,
                'error': 'Pyth 프로그램 계정을 가져올 수 없습니다.',
                'publishers': [],
                'analysis': {}
            }
        
        # 2. 가격 계정 가져오기
        price_accounts = self.get_pyth_price_accounts()
        
        # 3. BTC 가격 계정 찾기
        btc_account = self.find_btc_price_account(price_accounts)
        
        # 4. 모든 계정에서 퍼블리셔 정보 추출
        all_publishers = []
        account_types = {}
        
        print("🔍 모든 계정에서 퍼블리셔 정보 추출 중...")
        
        for i, account in enumerate(pyth_accounts[:50]):  # 처음 50개만 처리
            try:
                account_data = account.get('account', {}).get('data', [])
                if isinstance(account_data, list) and len(account_data) > 0:
                    parsed_data = self.parse_pyth_account_data(account_data[0])
                    
                    account_type = parsed_data.get('account_type', 'unknown')
                    if account_type not in account_types:
                        account_types[account_type] = 0
                    account_types[account_type] += 1
                    
                    # 퍼블리셔 정보가 있는 경우
                    if parsed_data.get('publishers'):
                        all_publishers.extend(parsed_data['publishers'])
                        print(f"✅ 계정 {i+1}에서 {len(parsed_data['publishers'])}개 퍼블리셔 발견")
                        
            except Exception as e:
                continue
        
        # 중복 제거
        unique_publishers = []
        seen_keys = set()
        
        for pub in all_publishers:
            pub_key = pub.get('public_key', '')
            if pub_key not in seen_keys:
                seen_keys.add(pub_key)
                unique_publishers.append(pub)
        
        print(f"✅ 총 {len(unique_publishers)}개의 고유 퍼블리셔를 찾았습니다.")
        
        return {
            'success': True,
            'publishers': unique_publishers,
            'total_publishers': len(unique_publishers),
            'account_types': account_types,
            'btc_account': btc_account,
            'total_accounts': len(pyth_accounts)
        }
    
    def save_results(self, results: Dict, filename: str = "pyth_solana_rpc_publishers.json"):
        """결과를 파일로 저장합니다."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 JSON 결과가 {filename}에 저장되었습니다.")
        
        # CSV로도 저장
        if results.get('success') and results.get('publishers'):
            csv_filename = filename.replace('.json', '.csv')
            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Index', 'Public Key', 'Public Key (Short)'])
                
                for i, pub in enumerate(results['publishers'], 1):
                    writer.writerow([
                        i,
                        pub['public_key'],
                        pub['public_key_short']
                    ])
            
            print(f"📊 CSV 결과가 {csv_filename}에 저장되었습니다.")
    
    def print_summary(self, results: Dict):
        """결과 요약을 출력합니다."""
        if not results.get('success'):
            print(f"❌ 실패: {results.get('error', '알 수 없는 오류')}")
            return
        
        print("\n" + "="*60)
        print("📊 Solana RPC Pyth 퍼블리셔 분석 결과")
        print("="*60)
        
        publishers = results.get('publishers', [])
        account_types = results.get('account_types', {})
        total_accounts = results.get('total_accounts', 0)
        
        print(f"📈 기본 통계:")
        print(f"  • 총 Pyth 계정 수: {total_accounts:,}개")
        print(f"  • 총 퍼블리셔 수: {len(publishers):,}개")
        
        if account_types:
            print(f"\n📊 계정 유형별 분포:")
            for account_type, count in account_types.items():
                print(f"  • {account_type}: {count}개")
        
        if publishers:
            print(f"\n🏆 퍼블리셔 리스트 (상위 15개):")
            for i, pub in enumerate(publishers[:15], 1):
                key_short = pub['public_key_short']
                print(f"  {i:2d}. {key_short}")
            
            if len(publishers) > 15:
                print(f"  ... 그리고 {len(publishers) - 15}개 더")
        
        btc_account = results.get('btc_account')
        if btc_account:
            print(f"\n📊 BTC 계정 정보:")
            parsed_data = btc_account.get('parsed_data', {})
            print(f"  • 계정 타입: {parsed_data.get('account_type', 'Unknown')}")
            print(f"  • 데이터 크기: {parsed_data.get('data_size', 0):,} 바이트")
            print(f"  • 퍼블리셔 수: {parsed_data.get('publisher_count', 0)}개")

def main():
    print("🚀 Solana RPC를 사용한 Pyth 퍼블리셔 정보 가져오기")
    print("=" * 70)
    
    rpc_publishers = PythSolanaRPCPublishers()
    
    # BTC 피드 퍼블리셔 가져오기
    results = rpc_publishers.get_btc_publishers()
    
    if results.get('success'):
        # 결과 출력
        rpc_publishers.print_summary(results)
        
        # 결과 저장
        rpc_publishers.save_results(results)
        
        print(f"\n✅ 분석 완료!")
        total_publishers = len(results.get('publishers', []))
        print(f"📊 결과: Solana RPC를 통해 {total_publishers}개의 퍼블리셔를 발견했습니다.")
    else:
        print(f"❌ 실패: {results.get('error', '알 수 없는 오류')}")

if __name__ == "__main__":
    main() 