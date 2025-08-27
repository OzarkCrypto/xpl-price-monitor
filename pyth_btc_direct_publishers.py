#!/usr/bin/env python3
"""
PYTH Network BTC/USD 피드 퍼블리셔 직접 접근
BTC/USD 피드를 직접 찾아서 퍼블리셔 정보를 가져옵니다.
"""

import requests
import json
import time
import csv
from typing import Dict, List, Optional

class PythBTCDirectPublishers:
    def __init__(self):
        self.base_url = "https://hermes.pyth.network"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def find_btc_usd_feed(self) -> Optional[Dict]:
        """BTC/USD 피드를 찾습니다."""
        print("🔍 BTC/USD 피드 찾는 중...")
        
        try:
            response = self.session.get(f"{self.base_url}/v2/price_feeds", timeout=30)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    feeds = data
                else:
                    feeds = data.get('data', [])
                
                # BTC/USD 피드 찾기
                btc_usd_feed = None
                for feed in feeds:
                    attributes = feed.get('attributes', {})
                    symbol = attributes.get('display_symbol', '')
                    
                    if symbol == 'BTC/USD':
                        btc_usd_feed = feed
                        break
                
                if btc_usd_feed:
                    print(f"✅ BTC/USD 피드를 찾았습니다!")
                    return btc_usd_feed
                else:
                    print("❌ BTC/USD 피드를 찾을 수 없습니다.")
                    return None
            else:
                print(f"❌ API 호출 실패: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"💥 오류 발생: {e}")
            return None
    
    def get_feed_details(self, feed_id: str) -> Dict:
        """피드 상세 정보를 가져옵니다."""
        print(f"📊 피드 상세 정보 가져오는 중... (ID: {feed_id[:20]}...)")
        
        # 여러 엔드포인트 시도
        endpoints = [
            f"/v2/updates/price/latest?ids[]={feed_id}",
            f"/v2/price_feeds/{feed_id}",
            f"/api/price_feeds/{feed_id}",
            f"/v2/updates/price/latest?ids[]={feed_id}&parsed=true",
            f"/v2/updates/price/latest?ids[]={feed_id}&verbose=true"
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {endpoint} 성공")
                    return {
                        'endpoint': endpoint,
                        'data': data,
                        'status': 'success'
                    }
                else:
                    print(f"❌ {endpoint} 실패: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"💥 {endpoint} 오류: {e}")
        
        return {
            'endpoint': 'none',
            'data': None,
            'status': 'failed'
        }
    
    def try_vaa_endpoints(self, feed_id: str) -> Dict:
        """VAA 관련 엔드포인트들을 시도합니다."""
        print(f"📡 VAA 엔드포인트 시도 중...")
        
        vaa_endpoints = [
            "/api/latest_vaas",
            "/v2/vaas/latest",
            "/api/vaas/latest",
            f"/api/latest_vaas?feed_id={feed_id}",
            f"/v2/vaas/latest?feed_id={feed_id}"
        ]
        
        for endpoint in vaa_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {endpoint} 성공")
                    return {
                        'endpoint': endpoint,
                        'data': data,
                        'status': 'success'
                    }
                else:
                    print(f"❌ {endpoint} 실패: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"💥 {endpoint} 오류: {e}")
        
        return {
            'endpoint': 'none',
            'data': None,
            'status': 'failed'
        }
    
    def extract_publishers_from_data(self, data: Dict) -> List[str]:
        """데이터에서 퍼블리셔 정보를 추출합니다."""
        publishers = []
        
        def search_publishers(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # 퍼블리셔 관련 키워드 검색
                    if any(pub_keyword in key.lower() for pub_keyword in ['publisher', 'authority', 'validator']):
                        if isinstance(value, str):
                            publishers.append(f"{current_path}: {value}")
                        elif isinstance(value, list):
                            for i, item in enumerate(value):
                                publishers.append(f"{current_path}[{i}]: {item}")
                        else:
                            publishers.append(f"{current_path}: {value}")
                    
                    # 재귀적으로 검색
                    search_publishers(value, current_path)
                    
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]"
                    search_publishers(item, current_path)
        
        search_publishers(data)
        return publishers
    
    def get_btc_publishers(self) -> Dict:
        """BTC/USD 피드의 퍼블리셔 정보를 가져옵니다."""
        print("🚀 BTC/USD 피드 퍼블리셔 정보 가져오기 시작")
        print("=" * 60)
        
        # 1. BTC/USD 피드 찾기
        btc_feed = self.find_btc_usd_feed()
        if not btc_feed:
            return {
                'success': False,
                'error': 'BTC/USD 피드를 찾을 수 없습니다.',
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
        
        print(f"📊 BTC/USD 피드 정보:")
        print(f"  • 심볼: {feed_info['symbol']}")
        print(f"  • 피드 ID: {feed_info['feed_id']}")
        print(f"  • 베이스: {feed_info['base']}")
        print(f"  • 견적 통화: {feed_info['quote_currency']}")
        
        # 3. 피드 상세 정보 가져오기
        feed_details = self.get_feed_details(feed_info['feed_id'])
        
        # 4. VAA 엔드포인트 시도
        vaa_data = self.try_vaa_endpoints(feed_info['feed_id'])
        
        # 5. 퍼블리셔 정보 추출
        all_publishers = []
        
        if feed_details['status'] == 'success':
            print(f"\n🔍 피드 상세 정보에서 퍼블리셔 검색 중...")
            feed_publishers = self.extract_publishers_from_data(feed_details['data'])
            all_publishers.extend(feed_publishers)
            print(f"✅ 피드 상세 정보에서 {len(feed_publishers)}개 퍼블리셔 정보 발견")
        
        if vaa_data['status'] == 'success':
            print(f"\n🔍 VAA 데이터에서 퍼블리셔 검색 중...")
            vaa_publishers = self.extract_publishers_from_data(vaa_data['data'])
            all_publishers.extend(vaa_publishers)
            print(f"✅ VAA 데이터에서 {len(vaa_publishers)}개 퍼블리셔 정보 발견")
        
        # 중복 제거
        unique_publishers = list(set(all_publishers))
        unique_publishers.sort()
        
        print(f"\n📊 최종 결과:")
        print(f"  • 총 퍼블리셔 정보: {len(unique_publishers)}개")
        
        return {
            'success': True,
            'publishers': unique_publishers,
            'feed_info': feed_info,
            'feed_details': feed_details,
            'vaa_data': vaa_data,
            'total_publishers': len(unique_publishers)
        }
    
    def save_results(self, results: Dict, filename: str = "btc_direct_publishers.json"):
        """결과를 파일로 저장합니다."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 JSON 결과가 {filename}에 저장되었습니다.")
        
        # CSV로도 저장
        if results.get('success') and results.get('publishers'):
            csv_filename = filename.replace('.json', '.csv')
            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Index', 'Publisher Info'])
                
                for i, publisher in enumerate(results['publishers'], 1):
                    writer.writerow([i, publisher])
            
            print(f"📊 CSV 결과가 {csv_filename}에 저장되었습니다.")
    
    def print_summary(self, results: Dict):
        """결과 요약을 출력합니다."""
        if not results.get('success'):
            print(f"❌ 실패: {results.get('error', '알 수 없는 오류')}")
            return
        
        print("\n" + "="*60)
        print("📊 BTC/USD 피드 퍼블리셔 분석 결과")
        print("="*60)
        
        feed_info = results['feed_info']
        publishers = results['publishers']
        
        print(f"📈 피드 정보:")
        print(f"  • 심볼: {feed_info['symbol']}")
        print(f"  • 피드 ID: {feed_info['feed_id']}")
        print(f"  • 베이스: {feed_info['base']}")
        print(f"  • 견적 통화: {feed_info['quote_currency']}")
        
        print(f"\n📊 API 호출 결과:")
        print(f"  • 피드 상세 정보: {results['feed_details']['status']}")
        print(f"  • VAA 데이터: {results['vaa_data']['status']}")
        
        print(f"\n📊 퍼블리셔 통계:")
        print(f"  • 총 퍼블리셔 정보: {len(publishers):,}개")
        
        if publishers:
            print(f"\n🏆 퍼블리셔 정보 (상위 20개):")
            for i, publisher in enumerate(publishers[:20], 1):
                print(f"  {i:2d}. {publisher}")
            
            if len(publishers) > 20:
                print(f"  ... 그리고 {len(publishers) - 20}개 더")
        else:
            print(f"\n⚠️  퍼블리셔 정보를 찾을 수 없습니다.")
        
        # API 응답 구조 분석
        if results['feed_details']['status'] == 'success':
            print(f"\n🔍 피드 상세 정보 구조:")
            data = results['feed_details']['data']
            if isinstance(data, dict):
                print(f"  • 최상위 키: {list(data.keys())[:10]}")
            elif isinstance(data, list):
                print(f"  • 리스트 길이: {len(data)}")
                if data and isinstance(data[0], dict):
                    print(f"  • 첫 번째 항목 키: {list(data[0].keys())[:10]}")

def main():
    print("🚀 PYTH Network BTC/USD 피드 퍼블리셔 직접 접근")
    print("=" * 70)
    
    btc_publishers = PythBTCDirectPublishers()
    
    # BTC/USD 피드 퍼블리셔 가져오기
    results = btc_publishers.get_btc_publishers()
    
    if results.get('success'):
        # 결과 출력
        btc_publishers.print_summary(results)
        
        # 결과 저장
        btc_publishers.save_results(results)
        
        print(f"\n✅ 분석 완료!")
        print(f"📊 결과: BTC/USD 피드에서 {len(results['publishers'])}개의 퍼블리셔 정보를 발견했습니다.")
    else:
        print(f"❌ 실패: {results.get('error', '알 수 없는 오류')}")

if __name__ == "__main__":
    main() 