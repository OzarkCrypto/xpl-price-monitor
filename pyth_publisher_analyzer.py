import requests
import json
from typing import List, Dict, Tuple
import time
from collections import defaultdict

class PythPublisherAnalyzer:
    def __init__(self):
        self.base_url = "https://hermes.pyth.network"
    
    def get_all_price_feeds(self):
        """
        v2/price_feeds 엔드포인트에서 모든 가격 피드를 가져옵니다.
        """
        print("🔍 Pyth Network v2 API에서 모든 가격 피드 가져오기...")
        
        try:
            url = f"{self.base_url}/v2/price_feeds"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 성공! {len(data)}개의 가격 피드를 가져왔습니다.")
                return data
            else:
                print(f"❌ 상태 코드: {response.status_code}")
        except Exception as e:
            print(f"❌ 오류: {e}")
        
        return []
    
    def get_latest_price_feeds_with_publishers(self, feed_ids, batch_size=50):
        """
        특정 피드 ID들의 최신 가격 정보와 퍼블리셔 정보를 가져옵니다.
        """
        print(f"💰 최신 가격 정보와 퍼블리셔 정보 가져오기 (배치 크기: {batch_size})...")
        
        all_results = []
        
        # 배치로 나누어 처리
        for i in range(0, len(feed_ids), batch_size):
            batch_ids = feed_ids[i:i + batch_size]
            print(f"  배치 {i//batch_size + 1}/{(len(feed_ids) + batch_size - 1)//batch_size} 처리 중... ({len(batch_ids)}개)")
            
            try:
                url = f"{self.base_url}/v2/updates/price/latest"
                params = {'ids[]': batch_ids}
                response = requests.get(url, params=params, timeout=20)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and 'parsed' in data:
                        parsed_data = data['parsed']
                        if isinstance(parsed_data, list):
                            all_results.extend(parsed_data)
                        else:
                            all_results.append(parsed_data)
                    elif isinstance(data, list):
                        all_results.extend(data)
                    else:
                        all_results.append(data)
                    
                    print(f"    ✅ {len(batch_ids)}개 처리 완료")
                else:
                    print(f"    ❌ 배치 {i//batch_size + 1} 실패 - 상태 코드: {response.status_code}")
                
                # API 요청 간격 조절
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    ❌ 배치 {i//batch_size + 1} 오류: {e}")
                continue
        
        print(f"✅ 총 {len(all_results)}개의 가격 피드 정보를 가져왔습니다.")
        return all_results
    
    def extract_symbol_and_publishers(self, feed_data, price_data_list):
        """
        피드 데이터와 가격 데이터에서 심볼과 퍼블리셔 정보를 추출합니다.
        """
        symbol_publishers = []
        
        # 피드 ID를 키로 하는 딕셔너리 생성
        price_data_dict = {}
        for price_data in price_data_list:
            if isinstance(price_data, dict) and 'id' in price_data:
                price_data_dict[price_data['id']] = price_data
        
        for feed in feed_data:
            if not isinstance(feed, dict):
                continue
            
            feed_id = feed.get('id')
            if not feed_id:
                continue
            
            # 심볼 추출
            symbol = self.extract_symbol_from_feed(feed)
            if not symbol:
                continue
            
            # 퍼블리셔 정보 추출
            publisher_count = 0
            publishers = []
            
            if feed_id in price_data_dict:
                price_data = price_data_dict[feed_id]
                
                # price_feed에서 퍼블리셔 정보 확인
                if 'price_feed' in price_data:
                    price_feed = price_data['price_feed']
                    
                    # price_components에서 퍼블리셔 확인
                    if 'price_components' in price_feed:
                        price_components = price_feed['price_components']
                        if isinstance(price_components, list):
                            publisher_count = len(price_components)
                            for component in price_components:
                                if isinstance(component, dict) and 'publisher' in component:
                                    publishers.append(component['publisher'])
                
                # vaa에서 퍼블리셔 정보 확인 (백업)
                elif 'vaa' in price_data:
                    vaa = price_data['vaa']
                    if isinstance(vaa, dict) and 'parsed' in vaa:
                        parsed_vaa = vaa['parsed']
                        if isinstance(parsed_vaa, dict) and 'price_feed' in parsed_vaa:
                            price_feed = parsed_vaa['price_feed']
                            if 'price_components' in price_feed:
                                price_components = price_feed['price_components']
                                if isinstance(price_components, list):
                                    publisher_count = len(price_components)
                                    for component in price_components:
                                        if isinstance(component, dict) and 'publisher' in component:
                                            publishers.append(component['publisher'])
            
            symbol_publishers.append({
                'symbol': symbol,
                'feed_id': feed_id,
                'publisher_count': publisher_count,
                'publishers': publishers,
                'asset_type': feed.get('attributes', {}).get('asset_type', 'Unknown')
            })
        
        return symbol_publishers
    
    def extract_symbol_from_feed(self, feed):
        """
        개별 피드에서 심볼을 추출합니다.
        """
        if not isinstance(feed, dict):
            return None
        
        # attributes 필드에서 심볼 정보 추출
        if 'attributes' in feed and isinstance(feed['attributes'], dict):
            attrs = feed['attributes']
            
            # display_symbol이 있으면 사용
            if 'display_symbol' in attrs and attrs['display_symbol']:
                return attrs['display_symbol']
            
            # symbol이 있으면 사용
            if 'symbol' in attrs and attrs['symbol']:
                symbol = attrs['symbol']
                # "Crypto.BTC/USD" 형태에서 "BTC/USD" 추출
                if '.' in symbol:
                    return symbol.split('.', 1)[1]
                return symbol
            
            # base와 quote_currency로 조합
            if 'base' in attrs and 'quote_currency' in attrs:
                base = attrs['base']
                quote = attrs['quote_currency']
                if base and quote:
                    return f"{base}/{quote}"
        
        return None
    
    def analyze_publishers(self, symbol_publishers):
        """
        퍼블리셔 분석을 수행합니다.
        """
        print("\n📊 퍼블리셔 분석 중...")
        
        # 퍼블리셔 수별로 정렬
        sorted_by_publishers = sorted(symbol_publishers, 
                                    key=lambda x: x['publisher_count'], 
                                    reverse=True)
        
        # 통계 계산
        total_symbols = len(symbol_publishers)
        symbols_with_publishers = len([s for s in symbol_publishers if s['publisher_count'] > 0])
        symbols_without_publishers = total_symbols - symbols_with_publishers
        
        publisher_counts = [s['publisher_count'] for s in symbol_publishers]
        avg_publishers = sum(publisher_counts) / len(publisher_counts) if publisher_counts else 0
        max_publishers = max(publisher_counts) if publisher_counts else 0
        min_publishers = min(publisher_counts) if publisher_counts else 0
        
        print(f"\n📈 퍼블리셔 통계:")
        print(f"  • 전체 심볼: {total_symbols}개")
        print(f"  • 퍼블리셔가 있는 심볼: {symbols_with_publishers}개")
        print(f"  • 퍼블리셔가 없는 심볼: {symbols_without_publishers}개")
        print(f"  • 평균 퍼블리셔 수: {avg_publishers:.2f}")
        print(f"  • 최대 퍼블리셔 수: {max_publishers}")
        print(f"  • 최소 퍼블리셔 수: {min_publishers}")
        
        return sorted_by_publishers
    
    def print_top_publishers(self, sorted_symbols, top_n=50):
        """
        퍼블리셔가 많은 상위 심볼들을 출력합니다.
        """
        print(f"\n🏆 퍼블리셔가 많은 상위 {top_n}개 심볼:")
        print("-" * 80)
        print(f"{'순위':<4} {'심볼':<20} {'퍼블리셔 수':<12} {'자산 유형':<12} {'피드 ID'}")
        print("-" * 80)
        
        for i, symbol_data in enumerate(sorted_symbols[:top_n], 1):
            symbol = symbol_data['symbol']
            publisher_count = symbol_data['publisher_count']
            asset_type = symbol_data['asset_type']
            feed_id = symbol_data['feed_id'][:20] + "..." if len(symbol_data['feed_id']) > 20 else symbol_data['feed_id']
            
            print(f"{i:<4} {symbol:<20} {publisher_count:<12} {asset_type:<12} {feed_id}")
    
    def print_publisher_distribution(self, sorted_symbols):
        """
        퍼블리셔 수별 분포를 출력합니다.
        """
        print(f"\n📊 퍼블리셔 수별 분포:")
        print("-" * 40)
        print(f"{'퍼블리셔 수':<12} {'심볼 수':<10} {'비율':<8}")
        print("-" * 40)
        
        publisher_distribution = defaultdict(int)
        total_symbols = len(sorted_symbols)
        
        for symbol_data in sorted_symbols:
            publisher_count = symbol_data['publisher_count']
            publisher_distribution[publisher_count] += 1
        
        # 퍼블리셔 수별로 정렬하여 출력
        for publisher_count in sorted(publisher_distribution.keys(), reverse=True):
            symbol_count = publisher_distribution[publisher_count]
            percentage = (symbol_count / total_symbols) * 100
            print(f"{publisher_count:<12} {symbol_count:<10} {percentage:.1f}%")
    
    def print_asset_type_analysis(self, sorted_symbols):
        """
        자산 유형별 퍼블리셔 분석을 출력합니다.
        """
        print(f"\n📊 자산 유형별 퍼블리셔 분석:")
        print("-" * 60)
        print(f"{'자산 유형':<12} {'심볼 수':<10} {'평균 퍼블리셔':<15} {'최대 퍼블리셔':<15}")
        print("-" * 60)
        
        asset_type_stats = defaultdict(lambda: {'count': 0, 'publishers': []})
        
        for symbol_data in sorted_symbols:
            asset_type = symbol_data['asset_type']
            publisher_count = symbol_data['publisher_count']
            
            asset_type_stats[asset_type]['count'] += 1
            asset_type_stats[asset_type]['publishers'].append(publisher_count)
        
        for asset_type, stats in asset_type_stats.items():
            count = stats['count']
            publishers = stats['publishers']
            avg_publishers = sum(publishers) / len(publishers) if publishers else 0
            max_publishers = max(publishers) if publishers else 0
            
            print(f"{asset_type:<12} {count:<10} {avg_publishers:<15.2f} {max_publishers:<15}")

def main():
    """
    메인 실행 함수
    """
    print("🚀 Pyth Network 퍼블리셔 분석\n")
    
    analyzer = PythPublisherAnalyzer()
    
    # 1. 모든 가격 피드 가져오기
    print("=== 1단계: 모든 가격 피드 가져오기 ===")
    all_feeds = analyzer.get_all_price_feeds()
    
    if not all_feeds:
        print("❌ 가격 피드를 가져올 수 없었습니다.")
        return
    
    # 2. 피드 ID 추출
    print("\n=== 2단계: 피드 ID 추출 ===")
    feed_ids = []
    for feed in all_feeds:
        if isinstance(feed, dict) and 'id' in feed:
            feed_ids.append(feed['id'])
    
    print(f"✅ {len(feed_ids)}개의 피드 ID를 추출했습니다.")
    
    # 3. 최신 가격 정보와 퍼블리셔 정보 가져오기
    print("\n=== 3단계: 퍼블리셔 정보 가져오기 ===")
    price_data_list = analyzer.get_latest_price_feeds_with_publishers(feed_ids, batch_size=30)
    
    # 4. 심볼과 퍼블리셔 정보 추출
    print("\n=== 4단계: 심볼과 퍼블리셔 정보 추출 ===")
    symbol_publishers = analyzer.extract_symbol_and_publishers(all_feeds, price_data_list)
    
    print(f"✅ {len(symbol_publishers)}개의 심볼에 대한 퍼블리셔 정보를 추출했습니다.")
    
    # 5. 퍼블리셔 분석
    print("\n=== 5단계: 퍼블리셔 분석 ===")
    sorted_symbols = analyzer.analyze_publishers(symbol_publishers)
    
    # 6. 결과 출력
    print("\n" + "="*80)
    analyzer.print_top_publishers(sorted_symbols, top_n=50)
    
    print("\n" + "="*80)
    analyzer.print_publisher_distribution(sorted_symbols)
    
    print("\n" + "="*80)
    analyzer.print_asset_type_analysis(sorted_symbols)
    
    print(f"\n✅ Pyth Network 퍼블리셔 분석 완료!")
    print(f"총 {len(sorted_symbols)}개의 심볼에 대한 퍼블리셔 정보를 분석했습니다.")

if __name__ == "__main__":
    main() 