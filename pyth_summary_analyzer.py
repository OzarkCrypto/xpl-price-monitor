#!/usr/bin/env python3
"""
PYTH Network 퍼블리셔 분석 결과 요약
기존 분석 결과를 바탕으로 전체적인 요약을 제공합니다.
"""

import json
import csv
from typing import Dict, List

def analyze_publisher_results():
    """기존 퍼블리셔 분석 결과를 분석합니다."""
    print("📊 PYTH Network 퍼블리셔 분석 결과 요약")
    print("=" * 60)
    
    # JSON 파일에서 데이터 읽기
    try:
        with open('pyth_publisher_analysis.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ pyth_publisher_analysis.json 파일을 찾을 수 없습니다.")
        return
    
    print(f"📈 분석된 피드 수: {len(data)}개")
    
    # 퍼블리셔 수별 분포 분석
    publisher_counts = [item['publisher_count'] for item in data]
    unique_counts = sorted(set(publisher_counts))
    
    print(f"\n📊 퍼블리셔 수별 분포:")
    for count in unique_counts:
        count_feeds = sum(1 for item in data if item['publisher_count'] == count)
        percentage = (count_feeds / len(data)) * 100
        print(f"  • {count:,}개 퍼블리셔: {count_feeds}개 피드 ({percentage:.1f}%)")
    
    # 통계 계산
    total_publishers = sum(publisher_counts)
    avg_publishers = total_publishers / len(data) if data else 0
    max_publishers = max(publisher_counts) if publisher_counts else 0
    min_publishers = min(publisher_counts) if publisher_counts else 0
    
    print(f"\n📈 통계 정보:")
    print(f"  • 총 퍼블리셔 수: {total_publishers:,}개")
    print(f"  • 평균 퍼블리셔 수: {avg_publishers:.1f}개")
    print(f"  • 최대 퍼블리셔 수: {max_publishers:,}개")
    print(f"  • 최소 퍼블리셔 수: {min_publishers:,}개")
    
    # 상위 20개 피드
    sorted_data = sorted(data, key=lambda x: x['publisher_count'], reverse=True)
    
    print(f"\n🏆 퍼블리셔 수 상위 20개 피드:")
    for i, item in enumerate(sorted_data[:20]):
        symbol = item['symbol']
        count = item['publisher_count']
        print(f"  {i+1:2d}. {symbol:<20} : {count:,}개 퍼블리셔")
    
    # 하위 20개 피드
    print(f"\n📉 퍼블리셔 수 하위 20개 피드:")
    for i, item in enumerate(sorted_data[-20:]):
        symbol = item['symbol']
        count = item['publisher_count']
        print(f"  {i+1:2d}. {symbol:<20} : {count:,}개 퍼블리셔")
    
    # 자산 유형별 분석
    asset_types = {}
    for item in data:
        symbol = item['symbol']
        count = item['publisher_count']
        
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
                asset_types[asset_type] = {'count': 0, 'total_publishers': 0, 'avg_publishers': 0}
            
            asset_types[asset_type]['count'] += 1
            asset_types[asset_type]['total_publishers'] += count
    
    # 평균 계산
    for asset_type in asset_types:
        stats = asset_types[asset_type]
        stats['avg_publishers'] = stats['total_publishers'] / stats['count']
    
    print(f"\n📊 자산 유형별 분석:")
    for asset_type, stats in sorted(asset_types.items(), key=lambda x: x[1]['count'], reverse=True):
        print(f"  • {asset_type}: {stats['count']}개 피드, 평균 {stats['avg_publishers']:.1f}개 퍼블리셔")
    
    # 주요 발견사항
    print(f"\n🔍 주요 발견사항:")
    
    # 0개 퍼블리셔 피드
    zero_publishers = sum(1 for item in data if item['publisher_count'] == 0)
    if zero_publishers > 0:
        print(f"  • {zero_publishers}개 피드가 0개 퍼블리셔를 가짐")
    
    # 가장 많은 퍼블리셔를 가진 피드
    top_feed = sorted_data[0]
    print(f"  • 가장 많은 퍼블리셔: {top_feed['symbol']} ({top_feed['publisher_count']:,}개)")
    
    # 가장 적은 퍼블리셔를 가진 피드 (0이 아닌 경우)
    non_zero_feeds = [item for item in data if item['publisher_count'] > 0]
    if non_zero_feeds:
        min_feed = min(non_zero_feeds, key=lambda x: x['publisher_count'])
        print(f"  • 가장 적은 퍼블리셔: {min_feed['symbol']} ({min_feed['publisher_count']:,}개)")
    
    # 퍼블리셔 수 범위
    print(f"  • 퍼블리셔 수 범위: {min_publishers:,}개 ~ {max_publishers:,}개")
    
    # 평균 이상 퍼블리셔를 가진 피드
    above_avg = sum(1 for item in data if item['publisher_count'] > avg_publishers)
    print(f"  • 평균 이상 퍼블리셔: {above_avg}개 피드 ({above_avg/len(data)*100:.1f}%)")
    
    return data

def create_summary_report(data: List[Dict]):
    """요약 보고서를 생성합니다."""
    print(f"\n📄 요약 보고서 생성 중...")
    
    # CSV 요약 파일 생성
    summary_filename = "pyth_publisher_summary.csv"
    with open(summary_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Category', 'Value', 'Description'])
        
        # 기본 통계
        total_feeds = len(data)
        total_publishers = sum(item['publisher_count'] for item in data)
        avg_publishers = total_publishers / total_feeds if total_feeds > 0 else 0
        max_publishers = max(item['publisher_count'] for item in data)
        min_publishers = min(item['publisher_count'] for item in data)
        
        writer.writerow(['Total Feeds', total_feeds, '분석된 총 피드 수'])
        writer.writerow(['Total Publishers', total_publishers, '총 퍼블리셔 수'])
        writer.writerow(['Average Publishers', f"{avg_publishers:.1f}", '피드당 평균 퍼블리셔 수'])
        writer.writerow(['Max Publishers', max_publishers, '최대 퍼블리셔 수'])
        writer.writerow(['Min Publishers', min_publishers, '최소 퍼블리셔 수'])
        
        # 퍼블리셔 수별 분포
        publisher_counts = [item['publisher_count'] for item in data]
        unique_counts = sorted(set(publisher_counts))
        
        for count in unique_counts:
            count_feeds = sum(1 for item in data if item['publisher_count'] == count)
            percentage = (count_feeds / total_feeds) * 100
            writer.writerow([f'{count} Publishers', count_feeds, f'{percentage:.1f}% of feeds'])
    
    print(f"✅ 요약 보고서가 {summary_filename}에 저장되었습니다.")

def main():
    print("🚀 PYTH Network 퍼블리셔 분석 결과 요약 시작")
    print("=" * 70)
    
    # 기존 분석 결과 분석
    data = analyze_publisher_results()
    
    if data:
        # 요약 보고서 생성
        create_summary_report(data)
        
        print(f"\n✅ 분석 완료!")
        print(f"📊 결과: PYTH Network의 각 자산별 피드에는 평균적으로 {sum(item['publisher_count'] for item in data)/len(data):.1f}명의 퍼블리셔가 참여하고 있습니다.")
    else:
        print("❌ 분석할 데이터가 없습니다.")

if __name__ == "__main__":
    main() 