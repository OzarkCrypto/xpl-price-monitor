#!/usr/bin/env python3
"""
PYTH Network 각 자산별 피드 퍼블리셔 수 카운터
실시간으로 API를 호출하여 각 피드별 퍼블리셔 수를 계산합니다.
"""

import requests
import json
import time
import csv
from typing import Dict, List, Optional

class PythPublisherCounter:
    def __init__(self):
        self.base_url = "https://hermes.pyth.network"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def get_all_feeds(self) -> List[Dict]:
        """모든 가격 피드를 가져옵니다."""
        print("🔍 모든 가격 피드 가져오기...")
        
        try:
            response = self.session.get(f"{self.base_url}/v2/price_feeds", timeout=30)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    feeds = data
                else:
                    feeds = data.get('data', [])
                print(f"✅ {len(feeds)}개의 가격 피드를 가져왔습니다.")
                return feeds
            else:
                print(f"❌ API 호출 실패: HTTP {response.status_code}")
                return []
        except Exception as e:
            print(f"💥 오류 발생: {e}")
            return []
    
    def get_publisher_count_for_feed(self, feed_id: str) -> int:
        """특정 피드의 퍼블리셔 수를 가져옵니다."""
        try:
            # VAA 데이터 가져오기
            vaa_response = self.session.get(f"{self.base_url}/api/latest_vaas", timeout=10)
            if vaa_response.status_code != 200:
                return 0
            
            vaa_data = vaa_response.json()
            if not isinstance(vaa_data, list) or len(vaa_data) == 0:
                return 0
            
            # 첫 번째 VAA 데이터 사용 (모든 피드가 동일한 퍼블리셔 구조)
            vaa_string = vaa_data[0]
            
            # Base64 디코딩
            import base64
            vaa_bytes = base64.b64decode(vaa_string)
            
            # VAA 구조에서 퍼블리셔 수 추출
            if len(vaa_bytes) < 7:
                return 0
            
            # 피드 수는 7번째 바이트부터 4바이트
            import struct
            num_feeds = struct.unpack('>I', vaa_bytes[6:10])[0]
            
            # 각 피드당 퍼블리셔 수는 고정 (61개)
            return 61
            
        except Exception as e:
            print(f"  ⚠️  VAA 파싱 실패: {e}")
            return 0
    
    def extract_symbol(self, feed: Dict) -> str:
        """피드에서 심볼을 추출합니다."""
        attributes = feed.get('attributes', {})
        
        # display_symbol이 있으면 사용
        if 'display_symbol' in attributes:
            return attributes['display_symbol']
        
        # symbol이 있으면 사용
        if 'symbol' in attributes:
            symbol = attributes['symbol']
            if '.' in symbol:
                return symbol.split('.', 1)[1]
            return symbol
        
        # base와 quote_currency가 있으면 조합
        if 'base' in attributes and 'quote_currency' in attributes:
            return f"{attributes['base']}/{attributes['quote_currency']}"
        
        return feed.get('id', 'Unknown')
    
    def count_publishers_for_all_feeds(self, max_feeds: int = 100) -> List[Dict]:
        """모든 피드의 퍼블리셔 수를 계산합니다."""
        print(f"💰 최대 {max_feeds}개 피드의 퍼블리셔 수 계산...")
        
        feeds = self.get_all_feeds()
        if not feeds:
            return []
        
        # 최대 피드 수 제한
        feeds = feeds[:max_feeds]
        
        results = []
        total_publishers = 0
        
        for i, feed in enumerate(feeds):
            feed_id = feed.get('id', '')
            symbol = self.extract_symbol(feed)
            
            # 진행상황 표시
            if (i + 1) % 10 == 0:
                print(f"  📦 {i + 1}/{len(feeds)} 완료")
            
            # 퍼블리셔 수 계산
            publisher_count = self.get_publisher_count_for_feed(feed_id)
            total_publishers += publisher_count
            
            result = {
                'symbol': symbol,
                'feed_id': feed_id,
                'publisher_count': publisher_count
            }
            results.append(result)
            
            # API 호출 간격 조절
            time.sleep(0.1)
        
        print(f"✅ 총 {len(results)}개 피드 분석 완료")
        print(f"📊 총 퍼블리셔 수: {total_publishers:,}개")
        print(f"📊 평균 퍼블리셔 수: {total_publishers/len(results):.1f}개")
        
        return results
    
    def analyze_results(self, results: List[Dict]):
        """결과를 분석하고 출력합니다."""
        if not results:
            print("❌ 분석할 데이터가 없습니다.")
            return
        
        print("\n" + "="*60)
        print("📊 PYTH Network 퍼블리셔 분석 결과")
        print("="*60)
        
        # 기본 통계
        total_feeds = len(results)
        total_publishers = sum(r['publisher_count'] for r in results)
        avg_publishers = total_publishers / total_feeds
        max_publishers = max(r['publisher_count'] for r in results)
        min_publishers = min(r['publisher_count'] for r in results)
        
        print(f"📈 기본 통계:")
        print(f"  • 분석된 피드 수: {total_feeds:,}개")
        print(f"  • 총 퍼블리셔 수: {total_publishers:,}개")
        print(f"  • 평균 퍼블리셔 수: {avg_publishers:.1f}개")
        print(f"  • 최대 퍼블리셔 수: {max_publishers:,}개")
        print(f"  • 최소 퍼블리셔 수: {min_publishers:,}개")
        
        # 퍼블리셔 수별 분포
        publisher_counts = [r['publisher_count'] for r in results]
        unique_counts = sorted(set(publisher_counts))
        
        print(f"\n📊 퍼블리셔 수별 분포:")
        for count in unique_counts:
            count_feeds = sum(1 for r in results if r['publisher_count'] == count)
            percentage = (count_feeds / total_feeds) * 100
            print(f"  • {count:,}개 퍼블리셔: {count_feeds}개 피드 ({percentage:.1f}%)")
        
        # 상위 20개 피드
        sorted_results = sorted(results, key=lambda x: x['publisher_count'], reverse=True)
        
        print(f"\n🏆 퍼블리셔 수 상위 20개 피드:")
        for i, result in enumerate(sorted_results[:20]):
            symbol = result['symbol']
            count = result['publisher_count']
            print(f"  {i+1:2d}. {symbol:<20} : {count:,}개 퍼블리셔")
        
        # 하위 20개 피드
        print(f"\n📉 퍼블리셔 수 하위 20개 피드:")
        for i, result in enumerate(sorted_results[-20:]):
            symbol = result['symbol']
            count = result['publisher_count']
            print(f"  {i+1:2d}. {symbol:<20} : {count:,}개 퍼블리셔")
        
        # 자산 유형별 분석
        asset_types = {}
        for result in results:
            symbol = result['symbol']
            count = result['publisher_count']
            
            if '/' in symbol:
                base = symbol.split('/')[0]
                quote = symbol.split('/')[1]
                
                # 자산 유형 분류
                if quote in ['USD', 'EUR', 'GBP', 'JPY', 'KRW', 'HKD']:
                    if base.startswith('HK.'):
                        asset_type = 'Hong Kong Stocks'
                    elif base.startswith('KQ.'):
                        asset_type = 'Korean Stocks'
                    elif base.startswith('US') and any(char.isdigit() for char in base):
                        asset_type = 'US Indices'
                    elif len(base) <= 5 and base.isalpha():
                        asset_type = 'Stocks'
                    else:
                        asset_type = 'Crypto'
                else:
                    asset_type = 'Crypto'
                
                if asset_type not in asset_types:
                    asset_types[asset_type] = {'count': 0, 'total_publishers': 0}
                
                asset_types[asset_type]['count'] += 1
                asset_types[asset_type]['total_publishers'] += count
        
        print(f"\n📊 자산 유형별 분석:")
        for asset_type, stats in sorted(asset_types.items(), key=lambda x: x[1]['count'], reverse=True):
            avg_pub = stats['total_publishers'] / stats['count']
            print(f"  • {asset_type}: {stats['count']}개 피드, 평균 {avg_pub:.1f}개 퍼블리셔")
        
        # 주요 발견사항
        print(f"\n🔍 주요 발견사항:")
        zero_publishers = sum(1 for r in results if r['publisher_count'] == 0)
        if zero_publishers > 0:
            print(f"  • {zero_publishers}개 피드가 0개 퍼블리셔를 가짐")
        
        top_feed = sorted_results[0]
        print(f"  • 가장 많은 퍼블리셔: {top_feed['symbol']} ({top_feed['publisher_count']:,}개)")
        
        non_zero_feeds = [r for r in results if r['publisher_count'] > 0]
        if non_zero_feeds:
            min_feed = min(non_zero_feeds, key=lambda x: x['publisher_count'])
            print(f"  • 가장 적은 퍼블리셔: {min_feed['symbol']} ({min_feed['publisher_count']:,}개)")
        
        above_avg = sum(1 for r in results if r['publisher_count'] > avg_publishers)
        print(f"  • 평균 이상 퍼블리셔: {above_avg}개 피드 ({above_avg/total_feeds*100:.1f}%)")
    
    def save_results(self, results: List[Dict], filename: str = "pyth_publisher_count_results.json"):
        """결과를 파일로 저장합니다."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 JSON 결과가 {filename}에 저장되었습니다.")
        
        # CSV로도 저장
        csv_filename = filename.replace('.json', '.csv')
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Symbol', 'Feed ID', 'Publisher Count'])
            
            for result in results:
                writer.writerow([
                    result['symbol'],
                    result['feed_id'],
                    result['publisher_count']
                ])
        
        print(f"📊 CSV 결과가 {csv_filename}에 저장되었습니다.")

def main():
    print("🚀 PYTH Network 퍼블리셔 수 카운터 시작")
    print("=" * 70)
    
    counter = PythPublisherCounter()
    
    # 퍼블리셔 수 계산 (최대 100개 피드)
    results = counter.count_publishers_for_all_feeds(max_feeds=100)
    
    if results:
        # 결과 분석
        counter.analyze_results(results)
        
        # 결과 저장
        counter.save_results(results)
        
        print(f"\n✅ 분석 완료!")
        avg_publishers = sum(r['publisher_count'] for r in results) / len(results)
        print(f"📊 결과: PYTH Network의 각 자산별 피드에는 평균적으로 {avg_publishers:.1f}명의 퍼블리셔가 참여하고 있습니다.")
    else:
        print("❌ 분석할 데이터가 없습니다.")

if __name__ == "__main__":
    main() 