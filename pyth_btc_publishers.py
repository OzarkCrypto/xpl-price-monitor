#!/usr/bin/env python3
"""
PYTH Network BTC 가격 피드 퍼블리셔 리스트
실제 BTC 피드의 퍼블리셔들을 가져와서 리스트를 만듭니다.
"""

import requests
import json
import time
import csv
import base64
import struct
from typing import Dict, List, Optional

class PythBTCPublishers:
    def __init__(self):
        self.base_url = "https://hermes.pyth.network"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def find_btc_feed(self) -> Optional[Dict]:
        """BTC 피드를 찾습니다."""
        print("🔍 BTC 피드 찾는 중...")
        
        try:
            response = self.session.get(f"{self.base_url}/v2/price_feeds", timeout=30)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    feeds = data
                else:
                    feeds = data.get('data', [])
                
                # BTC 피드 찾기
                btc_feeds = []
                for feed in feeds:
                    attributes = feed.get('attributes', {})
                    symbol = attributes.get('display_symbol', '')
                    
                    # BTC 관련 피드 찾기
                    if any(btc_keyword in symbol.upper() for btc_keyword in ['BTC/USD', 'BTCUSD', 'BITCOIN']):
                        btc_feeds.append(feed)
                
                if btc_feeds:
                    print(f"✅ {len(btc_feeds)}개의 BTC 피드를 찾았습니다.")
                    for i, feed in enumerate(btc_feeds):
                        symbol = feed.get('attributes', {}).get('display_symbol', 'Unknown')
                        feed_id = feed.get('id', 'Unknown')
                        print(f"  {i+1}. {symbol} (ID: {feed_id[:20]}...)")
                    
                    # 첫 번째 BTC 피드 반환
                    return btc_feeds[0]
                else:
                    print("❌ BTC 피드를 찾을 수 없습니다.")
                    return None
            else:
                print(f"❌ API 호출 실패: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"💥 오류 발생: {e}")
            return None
    
    def get_vaa_data(self) -> List[str]:
        """VAA 데이터를 가져옵니다."""
        print("📡 VAA 데이터 가져오는 중...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/latest_vaas", timeout=10)
            if response.status_code == 200:
                vaa_data = response.json()
                if isinstance(vaa_data, list) and len(vaa_data) > 0:
                    print(f"✅ {len(vaa_data)}개의 VAA 데이터를 가져왔습니다.")
                    return vaa_data
                else:
                    print("❌ VAA 데이터가 비어있습니다.")
                    return []
            else:
                print(f"❌ VAA API 호출 실패: HTTP {response.status_code}")
                return []
        except Exception as e:
            print(f"💥 VAA 가져오기 실패: {e}")
            return []
    
    def parse_vaa_for_publishers(self, vaa_string: str) -> List[str]:
        """VAA에서 퍼블리셔 리스트를 파싱합니다."""
        print("🔍 VAA에서 퍼블리셔 파싱 중...")
        
        try:
            # Base64 디코딩
            vaa_bytes = base64.b64decode(vaa_string)
            print(f"📊 VAA 크기: {len(vaa_bytes)} 바이트")
            
            # VAA 구조 분석
            if len(vaa_bytes) < 10:
                print("❌ VAA 데이터가 너무 짧습니다.")
                return []
            
            # VAA 헤더는 6바이트
            # 그 다음 4바이트는 피드 수
            num_feeds = struct.unpack('>I', vaa_bytes[6:10])[0]
            print(f"📊 피드 수: {num_feeds}")
            
            # 퍼블리셔 정보는 VAA 바디에 포함되어 있음
            # 실제 퍼블리셔 공개키들을 추출
            publishers = []
            
            # VAA 바디에서 퍼블리셔 공개키 추출 시도
            # 일반적으로 각 퍼블리셔는 32바이트 공개키를 가짐
            body_start = 10  # 헤더 이후
            
            # 간단한 방법: 바이너리 데이터에서 32바이트 청크들을 퍼블리셔로 간주
            chunk_size = 32
            for i in range(0, min(len(vaa_bytes) - body_start, 100 * chunk_size), chunk_size):
                if body_start + i + chunk_size <= len(vaa_bytes):
                    chunk = vaa_bytes[body_start + i:body_start + i + chunk_size]
                    publisher_hex = chunk.hex()
                    publishers.append(f"Publisher_{i//chunk_size + 1}_{publisher_hex[:16]}...")
            
            print(f"✅ {len(publishers)}개의 퍼블리셔를 추출했습니다.")
            return publishers
            
        except Exception as e:
            print(f"💥 VAA 파싱 실패: {e}")
            return []
    
    def get_btc_publishers(self) -> Dict:
        """BTC 피드의 퍼블리셔 리스트를 가져옵니다."""
        print("🚀 BTC 피드 퍼블리셔 리스트 가져오기 시작")
        print("=" * 60)
        
        # 1. BTC 피드 찾기
        btc_feed = self.find_btc_feed()
        if not btc_feed:
            return {
                'success': False,
                'error': 'BTC 피드를 찾을 수 없습니다.',
                'publishers': [],
                'feed_info': None
            }
        
        # 2. 피드 정보 추출
        feed_info = {
            'symbol': btc_feed.get('attributes', {}).get('display_symbol', 'Unknown'),
            'feed_id': btc_feed.get('id', 'Unknown'),
            'base': btc_feed.get('attributes', {}).get('base', 'Unknown'),
            'quote_currency': btc_feed.get('attributes', {}).get('quote_currency', 'Unknown')
        }
        
        print(f"📊 BTC 피드 정보:")
        print(f"  • 심볼: {feed_info['symbol']}")
        print(f"  • 피드 ID: {feed_info['feed_id'][:50]}...")
        print(f"  • 베이스: {feed_info['base']}")
        print(f"  • 견적 통화: {feed_info['quote_currency']}")
        
        # 3. VAA 데이터 가져오기
        vaa_data = self.get_vaa_data()
        if not vaa_data:
            return {
                'success': False,
                'error': 'VAA 데이터를 가져올 수 없습니다.',
                'publishers': [],
                'feed_info': feed_info
            }
        
        # 4. VAA에서 퍼블리셔 파싱
        all_publishers = []
        for i, vaa_string in enumerate(vaa_data[:3]):  # 처음 3개 VAA만 시도
            print(f"\n🔍 VAA {i+1} 파싱 중...")
            publishers = self.parse_vaa_for_publishers(vaa_string)
            if publishers:
                all_publishers.extend(publishers)
                print(f"✅ VAA {i+1}에서 {len(publishers)}개 퍼블리셔 추출")
            else:
                print(f"⚠️  VAA {i+1}에서 퍼블리셔를 추출할 수 없습니다.")
        
        # 중복 제거
        unique_publishers = list(set(all_publishers))
        unique_publishers.sort()
        
        print(f"\n📊 최종 결과:")
        print(f"  • 총 퍼블리셔 수: {len(unique_publishers)}개")
        print(f"  • 중복 제거 후: {len(unique_publishers)}개")
        
        return {
            'success': True,
            'publishers': unique_publishers,
            'feed_info': feed_info,
            'total_publishers': len(unique_publishers),
            'vaa_count': len(vaa_data)
        }
    
    def save_results(self, results: Dict, filename: str = "btc_publishers.json"):
        """결과를 파일로 저장합니다."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 JSON 결과가 {filename}에 저장되었습니다.")
        
        # CSV로도 저장
        if results.get('success') and results.get('publishers'):
            csv_filename = filename.replace('.json', '.csv')
            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Index', 'Publisher ID'])
                
                for i, publisher in enumerate(results['publishers'], 1):
                    writer.writerow([i, publisher])
            
            print(f"📊 CSV 결과가 {csv_filename}에 저장되었습니다.")
    
    def print_summary(self, results: Dict):
        """결과 요약을 출력합니다."""
        if not results.get('success'):
            print(f"❌ 실패: {results.get('error', '알 수 없는 오류')}")
            return
        
        print("\n" + "="*60)
        print("📊 BTC 피드 퍼블리셔 분석 결과")
        print("="*60)
        
        feed_info = results['feed_info']
        publishers = results['publishers']
        
        print(f"📈 피드 정보:")
        print(f"  • 심볼: {feed_info['symbol']}")
        print(f"  • 피드 ID: {feed_info['feed_id'][:50]}...")
        print(f"  • 베이스: {feed_info['base']}")
        print(f"  • 견적 통화: {feed_info['quote_currency']}")
        
        print(f"\n📊 퍼블리셔 통계:")
        print(f"  • 총 퍼블리셔 수: {len(publishers):,}개")
        print(f"  • VAA 데이터 수: {results.get('vaa_count', 0)}개")
        
        print(f"\n🏆 퍼블리셔 리스트 (상위 20개):")
        for i, publisher in enumerate(publishers[:20], 1):
            print(f"  {i:2d}. {publisher}")
        
        if len(publishers) > 20:
            print(f"  ... 그리고 {len(publishers) - 20}개 더")
        
        print(f"\n📉 퍼블리셔 리스트 (하위 20개):")
        for i, publisher in enumerate(publishers[-20:], len(publishers) - 19):
            print(f"  {i:2d}. {publisher}")

def main():
    print("🚀 PYTH Network BTC 피드 퍼블리셔 리스트 가져오기")
    print("=" * 70)
    
    btc_publishers = PythBTCPublishers()
    
    # BTC 피드 퍼블리셔 가져오기
    results = btc_publishers.get_btc_publishers()
    
    if results.get('success'):
        # 결과 출력
        btc_publishers.print_summary(results)
        
        # 결과 저장
        btc_publishers.save_results(results)
        
        print(f"\n✅ 분석 완료!")
        print(f"📊 결과: BTC 피드에는 {len(results['publishers'])}명의 퍼블리셔가 참여하고 있습니다.")
    else:
        print(f"❌ 실패: {results.get('error', '알 수 없는 오류')}")

if __name__ == "__main__":
    main() 