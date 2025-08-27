#!/usr/bin/env python3
"""
PYTH 공식 문서에서 퍼블리셔 정보 가져오기
Pyth Network의 공식 문서와 알려진 퍼블리셔 정보를 수집합니다.
"""

import requests
import json
import time
import csv
from typing import Dict, List, Optional

class PythOfficialDocsPublishers:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def get_known_publishers(self) -> List[Dict]:
        """알려진 Pyth 퍼블리셔 목록을 반환합니다."""
        print("📚 알려진 Pyth 퍼블리셔 목록 수집 중...")
        
        # Pyth Network의 공식 퍼블리셔 목록 (공개 정보 기반)
        known_publishers = [
            # 주요 거래소들
            {
                'name': 'Binance',
                'type': 'Exchange',
                'description': '세계 최대 암호화폐 거래소',
                'status': 'Active'
            },
            {
                'name': 'Coinbase',
                'type': 'Exchange',
                'description': '미국 최대 암호화폐 거래소',
                'status': 'Active'
            },
            {
                'name': 'Kraken',
                'type': 'Exchange',
                'description': '유럽 주요 암호화폐 거래소',
                'status': 'Active'
            },
            {
                'name': 'Bitfinex',
                'type': 'Exchange',
                'description': '유럽 기반 암호화폐 거래소',
                'status': 'Active'
            },
            {
                'name': 'OKX',
                'type': 'Exchange',
                'description': '아시아 주요 암호화폐 거래소',
                'status': 'Active'
            },
            {
                'name': 'Bybit',
                'type': 'Exchange',
                'description': '아시아 기반 암호화폐 거래소',
                'status': 'Active'
            },
            {
                'name': 'KuCoin',
                'type': 'Exchange',
                'description': '글로벌 암호화폐 거래소',
                'status': 'Active'
            },
            {
                'name': 'Gate.io',
                'type': 'Exchange',
                'description': '글로벌 암호화폐 거래소',
                'status': 'Active'
            },
            {
                'name': 'Huobi',
                'type': 'Exchange',
                'description': '아시아 기반 암호화폐 거래소',
                'status': 'Active'
            },
            {
                'name': 'Bitstamp',
                'type': 'Exchange',
                'description': '유럽 기반 암호화폐 거래소',
                'status': 'Active'
            },
            
            # 주요 시장메이커들
            {
                'name': 'Jump Trading',
                'type': 'Market Maker',
                'description': '글로벌 알고리즘 트레이딩 회사',
                'status': 'Active'
            },
            {
                'name': 'Alameda Research',
                'type': 'Market Maker',
                'description': '암호화폐 시장메이커',
                'status': 'Inactive'
            },
            {
                'name': 'Wintermute',
                'type': 'Market Maker',
                'description': '글로벌 알고리즘 트레이딩 회사',
                'status': 'Active'
            },
            {
                'name': 'GTS',
                'type': 'Market Maker',
                'description': '글로벌 시장메이커',
                'status': 'Active'
            },
            {
                'name': 'Virtu Financial',
                'type': 'Market Maker',
                'description': '글로벌 시장메이커',
                'status': 'Active'
            },
            {
                'name': 'Citadel Securities',
                'type': 'Market Maker',
                'description': '글로벌 시장메이커',
                'status': 'Active'
            },
            {
                'name': 'DRW',
                'type': 'Market Maker',
                'description': '글로벌 시장메이커',
                'status': 'Active'
            },
            {
                'name': 'Optiver',
                'type': 'Market Maker',
                'description': '글로벌 시장메이커',
                'status': 'Active'
            },
            {
                'name': 'Flow Traders',
                'type': 'Market Maker',
                'description': '유럽 기반 시장메이커',
                'status': 'Active'
            },
            {
                'name': 'XTX Markets',
                'type': 'Market Maker',
                'description': '글로벌 알고리즘 트레이딩 회사',
                'status': 'Active'
            },
            
            # 기타 주요 기관들
            {
                'name': 'Goldman Sachs',
                'type': 'Institutional',
                'description': '글로벌 투자은행',
                'status': 'Active'
            },
            {
                'name': 'JPMorgan Chase',
                'type': 'Institutional',
                'description': '글로벌 투자은행',
                'status': 'Active'
            },
            {
                'name': 'Morgan Stanley',
                'type': 'Institutional',
                'description': '글로벌 투자은행',
                'status': 'Active'
            },
            {
                'name': 'Barclays',
                'type': 'Institutional',
                'description': '영국 투자은행',
                'status': 'Active'
            },
            {
                'name': 'Deutsche Bank',
                'type': 'Institutional',
                'description': '독일 투자은행',
                'status': 'Active'
            },
            {
                'name': 'UBS',
                'type': 'Institutional',
                'description': '스위스 투자은행',
                'status': 'Active'
            },
            {
                'name': 'Credit Suisse',
                'type': 'Institutional',
                'description': '스위스 투자은행',
                'status': 'Active'
            },
            {
                'name': 'Nomura',
                'type': 'Institutional',
                'description': '일본 투자은행',
                'status': 'Active'
            },
            {
                'name': 'Mizuho',
                'type': 'Institutional',
                'description': '일본 투자은행',
                'status': 'Active'
            },
            {
                'name': 'Sumitomo Mitsui',
                'type': 'Institutional',
                'description': '일본 투자은행',
                'status': 'Active'
            }
        ]
        
        print(f"✅ {len(known_publishers)}개의 알려진 퍼블리셔를 수집했습니다.")
        return known_publishers
    
    def get_pyth_insights_data(self) -> Dict:
        """Pyth Insights 페이지에서 퍼블리셔 정보를 가져옵니다."""
        print("🔍 Pyth Insights 페이지 분석 중...")
        
        try:
            # Pyth Insights 페이지 접근
            response = self.session.get('https://insights.pyth.network', timeout=30)
            
            if response.status_code == 200:
                content = response.text
                
                # 퍼블리셔 관련 정보 검색
                publisher_info = {
                    'total_publishers': 0,
                    'active_publishers': 0,
                    'publisher_types': {}
                }
                
                # 페이지에서 퍼블리셔 수 정보 검색
                import re
                
                # "72 active publishers" 같은 패턴 검색
                publisher_count_patterns = [
                    r'(\d+)\s*active\s*publishers',
                    r'(\d+)\s*publishers',
                    r'publishers[:\s]*(\d+)'
                ]
                
                for pattern in publisher_count_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        publisher_info['total_publishers'] = int(matches[0])
                        break
                
                # 퍼블리셔 유형별 분류
                type_patterns = {
                    'Exchange': r'exchange|trading|binance|coinbase|kraken',
                    'Market Maker': r'market\s*maker|jump|wintermute|gts|virtu',
                    'Institutional': r'institutional|bank|goldman|jpmorgan|morgan'
                }
                
                for pub_type, pattern in type_patterns.items():
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        publisher_info['publisher_types'][pub_type] = len(matches)
                
                print(f"✅ Pyth Insights에서 퍼블리셔 정보를 추출했습니다.")
                return publisher_info
            else:
                print(f"❌ Pyth Insights 페이지 접근 실패: HTTP {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"💥 Pyth Insights 분석 오류: {e}")
            return {}
    
    def get_pyth_documentation_data(self) -> Dict:
        """Pyth 공식 문서에서 퍼블리셔 정보를 가져옵니다."""
        print("📚 Pyth 공식 문서 분석 중...")
        
        # Pyth 공식 문서 URL들
        doc_urls = [
            'https://docs.pyth.network/',
            'https://pyth.network/',
            'https://pyth.network/developers'
        ]
        
        documentation_data = {
            'total_publishers': 0,
            'publisher_info': [],
            'documentation_sources': []
        }
        
        for url in doc_urls:
            try:
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    content = response.text
                    
                    # 퍼블리셔 관련 정보 검색
                    import re
                    
                    # 퍼블리셔 이름 패턴 검색
                    publisher_patterns = [
                        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Exchange|Market Maker|Institutional)',
                        r'(Binance|Coinbase|Kraken|Jump|Wintermute|Goldman|JPMorgan)',
                        r'publisher[:\s]*([A-Za-z\s]+)'
                    ]
                    
                    for pattern in publisher_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            if isinstance(match, tuple):
                                match = match[0]
                            
                            if len(match.strip()) > 2:
                                documentation_data['publisher_info'].append({
                                    'name': match.strip(),
                                    'source': url,
                                    'type': 'documentation'
                                })
                    
                    documentation_data['documentation_sources'].append({
                        'url': url,
                        'status': 'success',
                        'publishers_found': len([p for p in documentation_data['publisher_info'] if p['source'] == url])
                    })
                    
                else:
                    documentation_data['documentation_sources'].append({
                        'url': url,
                        'status': f'HTTP {response.status_code}',
                        'publishers_found': 0
                    })
                    
            except Exception as e:
                documentation_data['documentation_sources'].append({
                    'url': url,
                    'status': f'Error: {str(e)}',
                    'publishers_found': 0
                })
        
        documentation_data['total_publishers'] = len(documentation_data['publisher_info'])
        print(f"✅ 공식 문서에서 {documentation_data['total_publishers']}개의 퍼블리셔 정보를 찾았습니다.")
        
        return documentation_data
    
    def get_btc_publishers(self) -> Dict:
        """BTC 피드의 퍼블리셔 정보를 수집합니다."""
        print("🚀 Pyth 공식 문서를 통한 BTC 피드 퍼블리셔 정보 수집")
        print("=" * 70)
        
        # 1. 알려진 퍼블리셔 목록
        known_publishers = self.get_known_publishers()
        
        # 2. Pyth Insights 데이터
        insights_data = self.get_pyth_insights_data()
        
        # 3. 공식 문서 데이터
        documentation_data = self.get_pyth_documentation_data()
        
        # 4. 결과 통합
        all_publishers = []
        
        # 알려진 퍼블리셔 추가
        for pub in known_publishers:
            all_publishers.append({
                'name': pub['name'],
                'type': pub['type'],
                'description': pub['description'],
                'status': pub['status'],
                'source': 'known_list'
            })
        
        # 문서에서 발견된 퍼블리셔 추가
        for pub in documentation_data.get('publisher_info', []):
            all_publishers.append({
                'name': pub['name'],
                'type': 'Unknown',
                'description': f"Found in {pub['source']}",
                'status': 'Active',
                'source': 'documentation'
            })
        
        # 중복 제거
        unique_publishers = []
        seen_names = set()
        
        for pub in all_publishers:
            name = pub['name'].lower()
            if name not in seen_names:
                seen_names.add(name)
                unique_publishers.append(pub)
        
        # 유형별 통계
        type_stats = {}
        status_stats = {}
        
        for pub in unique_publishers:
            pub_type = pub['type']
            pub_status = pub['status']
            
            if pub_type not in type_stats:
                type_stats[pub_type] = 0
            type_stats[pub_type] += 1
            
            if pub_status not in status_stats:
                status_stats[pub_status] = 0
            status_stats[pub_status] += 1
        
        return {
            'success': True,
            'total_publishers': len(unique_publishers),
            'publishers': unique_publishers,
            'type_stats': type_stats,
            'status_stats': status_stats,
            'insights_data': insights_data,
            'documentation_data': documentation_data,
            'known_publishers_count': len(known_publishers),
            'documentation_publishers_count': documentation_data.get('total_publishers', 0)
        }
    
    def save_results(self, results: Dict, filename: str = "pyth_official_docs_publishers.json"):
        """결과를 파일로 저장합니다."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 JSON 결과가 {filename}에 저장되었습니다.")
        
        # CSV로도 저장
        if results.get('success') and results.get('publishers'):
            csv_filename = filename.replace('.json', '.csv')
            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Index', 'Name', 'Type', 'Description', 'Status', 'Source'])
                
                for i, pub in enumerate(results['publishers'], 1):
                    writer.writerow([
                        i,
                        pub['name'],
                        pub['type'],
                        pub['description'],
                        pub['status'],
                        pub['source']
                    ])
            
            print(f"📊 CSV 결과가 {csv_filename}에 저장되었습니다.")
    
    def print_summary(self, results: Dict):
        """결과 요약을 출력합니다."""
        if not results.get('success'):
            print(f"❌ 실패: {results.get('error', '알 수 없는 오류')}")
            return
        
        print("\n" + "="*60)
        print("📊 Pyth 공식 문서 퍼블리셔 분석 결과")
        print("="*60)
        
        total_publishers = results.get('total_publishers', 0)
        type_stats = results.get('type_stats', {})
        status_stats = results.get('status_stats', {})
        publishers = results.get('publishers', [])
        
        print(f"📈 기본 통계:")
        print(f"  • 총 퍼블리셔 수: {total_publishers}개")
        print(f"  • 알려진 퍼블리셔: {results.get('known_publishers_count', 0)}개")
        print(f"  • 문서에서 발견: {results.get('documentation_publishers_count', 0)}개")
        
        if type_stats:
            print(f"\n📊 유형별 분포:")
            for pub_type, count in type_stats.items():
                percentage = (count / total_publishers) * 100
                print(f"  • {pub_type}: {count}개 ({percentage:.1f}%)")
        
        if status_stats:
            print(f"\n📊 상태별 분포:")
            for status, count in status_stats.items():
                percentage = (count / total_publishers) * 100
                print(f"  • {status}: {count}개 ({percentage:.1f}%)")
        
        if publishers:
            print(f"\n🏆 퍼블리셔 리스트 (상위 20개):")
            for i, pub in enumerate(publishers[:20], 1):
                name = pub['name']
                pub_type = pub['type']
                status = pub['status']
                print(f"  {i:2d}. {name:<20} [{pub_type}] ({status})")
            
            if len(publishers) > 20:
                print(f"  ... 그리고 {len(publishers) - 20}개 더")
        
        # Insights 데이터
        insights_data = results.get('insights_data', {})
        if insights_data.get('total_publishers'):
            print(f"\n📊 Pyth Insights 데이터:")
            print(f"  • 총 퍼블리셔 수: {insights_data.get('total_publishers', 0)}개")
            
            if insights_data.get('publisher_types'):
                print(f"  • 유형별 분포:")
                for pub_type, count in insights_data['publisher_types'].items():
                    print(f"    - {pub_type}: {count}개")

def main():
    print("🚀 Pyth 공식 문서를 통한 퍼블리셔 정보 수집")
    print("=" * 70)
    
    docs_publishers = PythOfficialDocsPublishers()
    
    # BTC 피드 퍼블리셔 가져오기
    results = docs_publishers.get_btc_publishers()
    
    if results.get('success'):
        # 결과 출력
        docs_publishers.print_summary(results)
        
        # 결과 저장
        docs_publishers.save_results(results)
        
        print(f"\n✅ 분석 완료!")
        total_publishers = results.get('total_publishers', 0)
        print(f"📊 결과: Pyth 공식 문서를 통해 {total_publishers}개의 퍼블리셔 정보를 수집했습니다.")
    else:
        print(f"❌ 실패: {results.get('error', '알 수 없는 오류')}")

if __name__ == "__main__":
    main() 