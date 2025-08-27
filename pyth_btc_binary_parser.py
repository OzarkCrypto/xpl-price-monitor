#!/usr/bin/env python3
"""
PYTH Network BTC 피드 바이너리 데이터 파서
BTC 피드의 binary 데이터를 파싱하여 퍼블리셔 정보를 추출합니다.
"""

import requests
import json
import time
import csv
import base64
import struct
from typing import Dict, List, Optional

class PythBTCBinaryParser:
    def __init__(self):
        self.base_url = "https://hermes.pyth.network"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def get_btc_feed_data(self) -> Optional[Dict]:
        """BTC/USD 피드 데이터를 가져옵니다."""
        print("🔍 BTC/USD 피드 데이터 가져오는 중...")
        
        try:
            # 먼저 BTC/USD 피드 ID 찾기
            response = self.session.get(f"{self.base_url}/v2/price_feeds", timeout=30)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    feeds = data
                else:
                    feeds = data.get('data', [])
                
                # BTC/USD 피드 찾기
                btc_feed_id = None
                for feed in feeds:
                    attributes = feed.get('attributes', {})
                    symbol = attributes.get('display_symbol', '')
                    if symbol == 'BTC/USD':
                        btc_feed_id = feed.get('id')
                        break
                
                if not btc_feed_id:
                    print("❌ BTC/USD 피드를 찾을 수 없습니다.")
                    return None
                
                print(f"✅ BTC/USD 피드 ID: {btc_feed_id}")
                
                # 피드 상세 데이터 가져오기
                feed_response = self.session.get(
                    f"{self.base_url}/v2/updates/price/latest?ids[]={btc_feed_id}",
                    timeout=10
                )
                
                if feed_response.status_code == 200:
                    feed_data = feed_response.json()
                    print(f"✅ 피드 데이터 가져오기 성공")
                    return feed_data
                else:
                    print(f"❌ 피드 데이터 가져오기 실패: HTTP {feed_response.status_code}")
                    return None
            else:
                print(f"❌ 피드 목록 가져오기 실패: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"💥 오류 발생: {e}")
            return None
    
    def parse_binary_data(self, hex_data: str) -> Dict:
        """hex 인코딩된 바이너리 데이터를 파싱합니다."""
        print("🔍 바이너리 데이터 파싱 중...")
        
        try:
            # hex 문자열을 바이트로 변환
            binary_data = bytes.fromhex(hex_data)
            print(f"📊 바이너리 데이터 크기: {len(binary_data)} 바이트")
            
            # Pyth VAA 구조 분석
            # 참고: https://github.com/pyth-network/pyth-crosschain/blob/main/target_chains/ethereum/sdk/src/vaa.ts
            
            if len(binary_data) < 10:
                print("❌ 바이너리 데이터가 너무 짧습니다.")
                return {}
            
            # VAA 헤더 파싱 (첫 6바이트)
            header = binary_data[:6]
            print(f"📊 VAA 헤더: {header.hex()}")
            
            # 피드 수 (4바이트, big-endian)
            num_feeds = struct.unpack('>I', binary_data[6:10])[0]
            print(f"📊 피드 수: {num_feeds}")
            
            # VAA 바디 시작 위치
            body_start = 10
            
            # 각 피드의 퍼블리셔 정보 파싱
            publishers = []
            current_pos = body_start
            
            for feed_index in range(min(num_feeds, 10)):  # 최대 10개 피드만 파싱
                if current_pos + 4 > len(binary_data):
                    break
                
                # 피드 ID 길이 (4바이트)
                feed_id_len = struct.unpack('>I', binary_data[current_pos:current_pos+4])[0]
                current_pos += 4
                
                if current_pos + feed_id_len > len(binary_data):
                    break
                
                # 피드 ID
                feed_id = binary_data[current_pos:current_pos+feed_id_len]
                current_pos += feed_id_len
                
                if current_pos + 4 > len(binary_data):
                    break
                
                # 퍼블리셔 수 (4바이트)
                num_publishers = struct.unpack('>I', binary_data[current_pos:current_pos+4])[0]
                current_pos += 4
                
                print(f"📊 피드 {feed_index+1}: ID={feed_id.hex()[:16]}..., 퍼블리셔 수={num_publishers}")
                
                # 각 퍼블리셔의 공개키 파싱
                for pub_index in range(min(num_publishers, 100)):  # 최대 100개 퍼블리셔만 파싱
                    if current_pos + 32 > len(binary_data):
                        break
                    
                    # 퍼블리셔 공개키 (32바이트)
                    pub_key = binary_data[current_pos:current_pos+32]
                    current_pos += 32
                    
                    publisher_info = {
                        'feed_index': feed_index + 1,
                        'publisher_index': pub_index + 1,
                        'public_key': pub_key.hex(),
                        'public_key_short': pub_key.hex()[:16] + "..."
                    }
                    publishers.append(publisher_info)
                
                # 퍼블리셔 가격 데이터 건너뛰기 (복잡한 구조)
                # 실제로는 각 퍼블리셔마다 가격, 신뢰도, 지수 등의 데이터가 있음
                # 여기서는 간단히 32바이트씩 건너뛰기
                price_data_size = num_publishers * 32  # 간단한 추정
                current_pos += price_data_size
                
                if current_pos >= len(binary_data):
                    break
            
            print(f"✅ 총 {len(publishers)}개의 퍼블리셔 정보를 파싱했습니다.")
            
            return {
                'num_feeds': num_feeds,
                'publishers': publishers,
                'total_publishers': len(publishers),
                'binary_size': len(binary_data)
            }
            
        except Exception as e:
            print(f"💥 바이너리 파싱 실패: {e}")
            return {}
    
    def analyze_publishers(self, parsed_data: Dict) -> Dict:
        """파싱된 퍼블리셔 데이터를 분석합니다."""
        if not parsed_data.get('publishers'):
            return {'error': '퍼블리셔 데이터가 없습니다.'}
        
        publishers = parsed_data['publishers']
        
        # 피드별 퍼블리셔 수
        feed_publishers = {}
        for pub in publishers:
            feed_idx = pub['feed_index']
            if feed_idx not in feed_publishers:
                feed_publishers[feed_idx] = 0
            feed_publishers[feed_idx] += 1
        
        # 고유한 공개키 수
        unique_keys = set(pub['public_key'] for pub in publishers)
        
        return {
            'total_publishers': len(publishers),
            'unique_publishers': len(unique_keys),
            'feed_publishers': feed_publishers,
            'publishers_per_feed': feed_publishers,
            'sample_publishers': publishers[:20]  # 샘플 20개
        }
    
    def get_btc_publishers(self) -> Dict:
        """BTC 피드의 퍼블리셔 정보를 가져옵니다."""
        print("🚀 BTC 피드 퍼블리셔 정보 가져오기 시작")
        print("=" * 60)
        
        # 1. BTC 피드 데이터 가져오기
        feed_data = self.get_btc_feed_data()
        if not feed_data:
            return {
                'success': False,
                'error': 'BTC 피드 데이터를 가져올 수 없습니다.',
                'publishers': [],
                'analysis': {}
            }
        
        # 2. 바이너리 데이터 추출
        binary_data = feed_data.get('binary', {})
        hex_data = binary_data.get('data', [])
        
        if not hex_data:
            return {
                'success': False,
                'error': '바이너리 데이터가 없습니다.',
                'publishers': [],
                'analysis': {}
            }
        
        # 3. 바이너리 데이터 파싱
        parsed_data = self.parse_binary_data(hex_data[0])
        
        if not parsed_data:
            return {
                'success': False,
                'error': '바이너리 데이터 파싱에 실패했습니다.',
                'publishers': [],
                'analysis': {}
            }
        
        # 4. 퍼블리셔 분석
        analysis = self.analyze_publishers(parsed_data)
        
        return {
            'success': True,
            'publishers': parsed_data['publishers'],
            'analysis': analysis,
            'feed_data': feed_data,
            'parsed_data': parsed_data
        }
    
    def save_results(self, results: Dict, filename: str = "btc_binary_publishers.json"):
        """결과를 파일로 저장합니다."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 JSON 결과가 {filename}에 저장되었습니다.")
        
        # CSV로도 저장
        if results.get('success') and results.get('publishers'):
            csv_filename = filename.replace('.json', '.csv')
            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Feed Index', 'Publisher Index', 'Public Key', 'Public Key (Short)'])
                
                for pub in results['publishers']:
                    writer.writerow([
                        pub['feed_index'],
                        pub['publisher_index'],
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
        print("📊 BTC 피드 퍼블리셔 바이너리 분석 결과")
        print("="*60)
        
        analysis = results['analysis']
        publishers = results['publishers']
        
        print(f"📈 기본 통계:")
        print(f"  • 총 퍼블리셔 수: {analysis.get('total_publishers', 0):,}개")
        print(f"  • 고유 퍼블리셔 수: {analysis.get('unique_publishers', 0):,}개")
        
        if analysis.get('feed_publishers'):
            print(f"\n📊 피드별 퍼블리셔 수:")
            for feed_idx, count in analysis['feed_publishers'].items():
                print(f"  • 피드 {feed_idx}: {count}개 퍼블리셔")
        
        if publishers:
            print(f"\n🏆 퍼블리셔 샘플 (상위 10개):")
            for i, pub in enumerate(publishers[:10], 1):
                print(f"  {i:2d}. 피드{pub['feed_index']}-퍼블리셔{pub['publisher_index']}: {pub['public_key_short']}")
            
            if len(publishers) > 10:
                print(f"  ... 그리고 {len(publishers) - 10}개 더")

def main():
    print("🚀 PYTH Network BTC 피드 바이너리 파서")
    print("=" * 70)
    
    parser = PythBTCBinaryParser()
    
    # BTC 피드 퍼블리셔 가져오기
    results = parser.get_btc_publishers()
    
    if results.get('success'):
        # 결과 출력
        parser.print_summary(results)
        
        # 결과 저장
        parser.save_results(results)
        
        print(f"\n✅ 분석 완료!")
        total_publishers = results['analysis'].get('total_publishers', 0)
        print(f"📊 결과: BTC 피드에서 {total_publishers}개의 퍼블리셔 정보를 파싱했습니다.")
    else:
        print(f"❌ 실패: {results.get('error', '알 수 없는 오류')}")

if __name__ == "__main__":
    main() 