#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import base64
import struct
from collections import defaultdict
import csv
from typing import List, Dict, Set, Tuple

class PythFinalPublisherAnalyzer:
    def __init__(self):
        self.base_url = "https://hermes.pyth.network"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_all_price_feeds(self) -> List[Dict]:
        """모든 가격 피드 정보를 가져옵니다."""
        try:
            url = f"{self.base_url}/v2/price_feeds"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"가격 피드 가져오기 실패: {e}")
            return []
    
    def get_publisher_count_from_vaa(self, feed_id: str) -> Tuple[int, List[str]]:
        """VAA 데이터에서 퍼블리셔 수와 퍼블리셔 ID 리스트를 추출합니다."""
        try:
            url = f"{self.base_url}/api/latest_vaas"
            params = {"ids[]": feed_id}
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            vaa_hex = None
            
            if isinstance(data, list) and len(data) > 0:
                # 리스트 형태로 VAA 문자열이 직접 반환되는 경우
                vaa_hex = data[0]
            elif isinstance(data, dict) and feed_id in data:
                # 딕셔너리 형태로 feed_id를 키로 하는 경우
                vaa_data = data[feed_id]
                if isinstance(vaa_data, dict) and 'vaa' in vaa_data:
                    vaa_hex = vaa_data['vaa']
                elif isinstance(vaa_data, str):
                    vaa_hex = vaa_data
            
            if not vaa_hex:
                return 0, []
            
            return self.parse_vaa_for_publisher_count(vaa_hex)
            
        except Exception as e:
            return 0, []
    
    def parse_vaa_for_publisher_count(self, vaa_base64: str) -> Tuple[int, List[str]]:
        """VAA Base64 데이터를 파싱하여 퍼블리셔 수와 ID 리스트를 추출합니다."""
        try:
            # Base64 문자열을 바이트로 변환
            vaa_bytes = base64.b64decode(vaa_base64)
            
            # Pyth VAA 구조 파싱
            # VAA 헤더 구조:
            # - Magic number (4 bytes)
            # - Version (1 byte)
            # - Header length (1 byte)
            # - Payload length (2 bytes)
            # - Number of price feeds (2 bytes)
            
            if len(vaa_bytes) < 10:
                return 0, []
            
            # 헤더 정보 파싱
            magic = struct.unpack('>I', vaa_bytes[0:4])[0]
            version = vaa_bytes[4]
            header_len = vaa_bytes[5]
            payload_len = struct.unpack('>H', vaa_bytes[6:8])[0]
            num_feeds = struct.unpack('>H', vaa_bytes[8:10])[0]
            
            # 퍼블리셔 정보 추출
            return self.extract_publishers_from_vaa_body(vaa_bytes, header_len, num_feeds)
            
        except Exception as e:
            return 0, []
    
    def extract_publishers_from_vaa_body(self, vaa_bytes: bytes, header_len: int, num_feeds: int) -> Tuple[int, List[str]]:
        """VAA 본문에서 퍼블리셔 정보 추출"""
        try:
            publishers = []
            offset = header_len
            
            for feed_idx in range(num_feeds):
                if offset + 32 > len(vaa_bytes):
                    break
                
                # 각 피드의 구조:
                # - Feed ID (32 bytes)
                # - Price (8 bytes)
                # - Confidence (8 bytes)
                # - Price exponent (4 bytes)
                # - Status (4 bytes)
                # - Timestamp (8 bytes)
                # - Publisher count (2 bytes)
                
                # Feed ID 건너뛰기
                offset += 32
                
                if offset + 42 > len(vaa_bytes):
                    break
                
                # 가격 정보 건너뛰기 (price, confidence, expo, status, timestamp)
                offset += 32
                
                # 퍼블리셔 수 읽기
                if offset + 2 <= len(vaa_bytes):
                    publisher_count = struct.unpack('>H', vaa_bytes[offset:offset+2])[0]
                    offset += 2
                    
                    # 각 퍼블리셔 정보 읽기
                    for pub_idx in range(publisher_count):
                        if offset + 20 <= len(vaa_bytes):
                            # 퍼블리셔 공개키 (20바이트)
                            pub_key = vaa_bytes[offset:offset+20].hex()
                            publishers.append(f"Publisher_{pub_idx+1}_{pub_key[:16]}")
                            offset += 20
                        else:
                            break
                else:
                    break
            
            return len(publishers), publishers
            
        except Exception as e:
            return 0, []
    
    def analyze_publishers(self, feeds: List[Dict], sample_size: int = 100) -> Dict:
        """퍼블리셔 분석을 수행합니다."""
        print(f"총 {len(feeds)}개 피드 중 {sample_size}개 샘플 분석 중...")
        
        # 샘플 선택
        sample_feeds = feeds[:sample_size]
        
        publisher_counts = []
        all_publishers = set()  # 모든 고유 퍼블리셔 ID 수집
        feed_publishers = {}    # 각 피드별 퍼블리셔 ID 리스트
        
        for i, feed in enumerate(sample_feeds):
            feed_id = feed.get('id', '')
            symbol = self.extract_symbol_from_feed(feed)
            
            print(f"진행률: {i+1}/{sample_size} - {symbol}")
            
            count, publishers = self.get_publisher_count_from_vaa(feed_id)
            
            if count > 0:
                publisher_counts.append({
                    'symbol': symbol,
                    'feed_id': feed_id,
                    'publisher_count': count,
                    'publishers': publishers
                })
                
                # 고유 퍼블리셔 ID 수집
                all_publishers.update(publishers)
                feed_publishers[symbol] = publishers
        
        # 통계 계산
        if publisher_counts:
            total_publishers = sum(item['publisher_count'] for item in publisher_counts)
            avg_publishers = total_publishers / len(publisher_counts)
            max_publishers = max(item['publisher_count'] for item in publisher_counts)
            min_publishers = min(item['publisher_count'] for item in publisher_counts)
            
            print(f"\n=== 퍼블리셔 분석 결과 ===")
            print(f"분석된 피드 수: {len(publisher_counts)}")
            print(f"총 퍼블리셔 수 (중복 포함): {total_publishers}")
            print(f"고유 퍼블리셔 수: {len(all_publishers)}")
            print(f"평균 퍼블리셔 수: {avg_publishers:.2f}")
            print(f"최대 퍼블리셔 수: {max_publishers}")
            print(f"최소 퍼블리셔 수: {min_publishers}")
            
            # 퍼블리셔 수로 정렬
            sorted_counts = sorted(publisher_counts, key=lambda x: x['publisher_count'], reverse=True)
            
            print(f"\n=== 퍼블리셔 수 상위 30개 ===")
            for i, item in enumerate(sorted_counts[:30]):
                print(f"{i+1:2d}. {item['symbol']}: {item['publisher_count']}개 퍼블리셔")
            
            print(f"\n=== 퍼블리셔 수 하위 10개 ===")
            for i, item in enumerate(sorted_counts[-10:]):
                print(f"{len(sorted_counts)-9+i:2d}. {item['symbol']}: {item['publisher_count']}개 퍼블리셔")
            
            # 고유 퍼블리셔 리스트 출력 (ID와 이름 함께)
            print(f"\n=== 고유 퍼블리셔 리스트 (총 {len(all_publishers)}개) ===")
            sorted_publishers = sorted(list(all_publishers))
            for i, publisher in enumerate(sorted_publishers):
                publisher_name = self.get_publisher_name(publisher)
                print(f"{i+1:4d}. {publisher} - {publisher_name}")
            
            return {
                'publisher_counts': publisher_counts,
                'all_publishers': list(all_publishers),
                'feed_publishers': feed_publishers,
                'stats': {
                    'total_feeds': len(publisher_counts),
                    'total_publishers': total_publishers,
                    'unique_publishers': len(all_publishers),
                    'avg_publishers': avg_publishers,
                    'max_publishers': max_publishers,
                    'min_publishers': min_publishers
                }
            }
        else:
            print("퍼블리셔 정보를 찾을 수 없습니다.")
            return {}
    
    def extract_symbol_from_feed(self, feed: Dict) -> str:
        """피드에서 심볼을 추출합니다."""
        attributes = feed.get('attributes', {})
        
        # display_symbol이 있으면 사용
        if 'display_symbol' in attributes:
            return attributes['display_symbol']
        
        # symbol이 있으면 사용 (Crypto.BTC/USD 형식 처리)
        if 'symbol' in attributes:
            symbol = attributes['symbol']
            if '/' in symbol:
                return symbol.split('/')[-2] + '/' + symbol.split('/')[-1]
            return symbol
        
        # base와 quote_currency가 있으면 조합
        if 'base' in attributes and 'quote_currency' in attributes:
            return f"{attributes['base']}/{attributes['quote_currency']}"
        
        return feed.get('id', 'Unknown')
    
    def save_results(self, results: Dict, filename_prefix: str = "pyth_publisher_analysis"):
        """결과를 JSON과 CSV 파일로 저장합니다."""
        if not results:
            print("저장할 결과가 없습니다.")
            return
        
        # JSON 파일 저장
        json_filename = f"{filename_prefix}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"결과가 {json_filename}에 저장되었습니다.")
        
        # CSV 파일 저장 (퍼블리셔 수 데이터)
        csv_filename = f"{filename_prefix}.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Symbol', 'Feed ID', 'Publisher Count'])
            for item in results['publisher_counts']:
                writer.writerow([item['symbol'], item['feed_id'], item['publisher_count']])
        print(f"퍼블리셔 수 데이터가 {csv_filename}에 저장되었습니다.")
        
        # 고유 퍼블리셔 리스트 CSV 저장
        publishers_csv_filename = f"{filename_prefix}_publishers.csv"
        with open(publishers_csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Publisher ID', 'Publisher Name'])
            for publisher in sorted(results['all_publishers']):
                publisher_name = self.get_publisher_name(publisher)
                writer.writerow([publisher, publisher_name])
        print(f"고유 퍼블리셔 리스트가 {publishers_csv_filename}에 저장되었습니다.")

    def get_known_publisher_names(self) -> Dict[str, str]:
        """알려진 퍼블리셔 이름 매핑을 반환합니다."""
        return {
            # 주요 퍼블리셔들
            "amber": "Amber Group",
            "alphanonce": "Alphanonce",
            "pyth": "Pyth Network",
            "binance": "Binance",
            "coinbase": "Coinbase",
            "kraken": "Kraken",
            "okx": "OKX",
            "bybit": "Bybit",
            "huobi": "Huobi",
            "gate": "Gate.io",
            "kucoin": "KuCoin",
            "bitfinex": "Bitfinex",
            "bitstamp": "Bitstamp",
            "gemini": "Gemini",
            "ftx": "FTX",
            "deribit": "Deribit",
            "ledgerx": "LedgerX",
            "cboe": "CBOE",
            "cmegroup": "CME Group",
            "ice": "ICE",
            "lmax": "LMAX",
            "xtx": "XTX Markets",
            "citadel": "Citadel Securities",
            "jump": "Jump Trading",
            "drw": "DRW",
            "optiver": "Optiver",
            "imc": "IMC Trading",
            "flow": "Flow Traders",
            "susquehanna": "Susquehanna International Group",
            "virtu": "Virtu Financial",
            "gts": "GTS",
            "knight": "Knight Capital",
            "getco": "Getco",
            "tower": "Tower Research Capital",
            "hudson": "Hudson River Trading",
            "two": "Two Sigma",
            "renaissance": "Renaissance Technologies",
            "point72": "Point72 Asset Management",
            "millennium": "Millennium Management",
            "citadel": "Citadel",
            "bridgewater": "Bridgewater Associates",
            "aqr": "AQR Capital Management",
            "blackrock": "BlackRock",
            "vanguard": "Vanguard",
            "fidelity": "Fidelity Investments",
            "goldman": "Goldman Sachs",
            "morgan": "Morgan Stanley",
            "jpmorgan": "JPMorgan Chase",
            "bankofamerica": "Bank of America",
            "wellsfargo": "Wells Fargo",
            "citigroup": "Citigroup",
            "deutsche": "Deutsche Bank",
            "ubs": "UBS",
            "credit": "Credit Suisse",
            "barclays": "Barclays",
            "hsbc": "HSBC",
            "nomura": "Nomura",
            "mizuho": "Mizuho Financial Group",
            "sumitomo": "Sumitomo Mitsui Financial Group",
            "mitsubishi": "Mitsubishi UFJ Financial Group",
            "societe": "Société Générale",
            "bnp": "BNP Paribas",
            "credit": "Crédit Agricole",
            "intesa": "Intesa Sanpaolo",
            "unicredit": "UniCredit",
            "santander": "Banco Santander",
            "bbva": "BBVA",
            "caixa": "CaixaBank",
            "ing": "ING Group",
            "rabobank": "Rabobank",
            "abn": "ABN AMRO",
            "danske": "Danske Bank",
            "nordea": "Nordea",
            "seb": "SEB",
            "handelsbanken": "Svenska Handelsbanken",
            "danske": "Danske Bank",
            "swedbank": "Swedbank",
            "dnb": "DNB",
            "sparebank": "SpareBank 1",
            "op": "OP Financial Group",
            "aktia": "Aktia Bank",
            "alandsbanken": "Ålandsbanken",
            "bank": "Bank",
            "trading": "Trading",
            "markets": "Markets",
            "securities": "Securities",
            "capital": "Capital",
            "investment": "Investment",
            "asset": "Asset",
            "management": "Management",
            "fund": "Fund",
            "hedge": "Hedge",
            "prop": "Proprietary",
            "quant": "Quantitative",
            "algorithmic": "Algorithmic",
            "high": "High-Frequency",
            "frequency": "Frequency",
            "market": "Market",
            "maker": "Maker",
            "liquidity": "Liquidity",
            "provider": "Provider",
            "exchange": "Exchange",
            "broker": "Broker",
            "dealer": "Dealer",
            "trader": "Trader",
            "arbitrage": "Arbitrage",
            "speculation": "Speculation",
            "risk": "Risk",
            "management": "Management",
            "portfolio": "Portfolio",
            "optimization": "Optimization",
            "strategy": "Strategy",
            "execution": "Execution",
            "order": "Order",
            "flow": "Flow",
            "analytics": "Analytics",
            "research": "Research",
            "development": "Development",
            "technology": "Technology",
            "software": "Software",
            "hardware": "Hardware",
            "infrastructure": "Infrastructure",
            "network": "Network",
            "connectivity": "Connectivity",
            "latency": "Latency",
            "optimization": "Optimization",
            "performance": "Performance",
            "monitoring": "Monitoring",
            "surveillance": "Surveillance",
            "compliance": "Compliance",
            "regulatory": "Regulatory",
            "reporting": "Reporting",
            "audit": "Audit",
            "governance": "Governance",
            "risk": "Risk",
            "control": "Control",
            "internal": "Internal",
            "external": "External",
            "vendor": "Vendor",
            "supplier": "Supplier",
            "partner": "Partner",
            "client": "Client",
            "customer": "Customer",
            "user": "User",
            "admin": "Administrator",
            "operator": "Operator",
            "analyst": "Analyst",
            "developer": "Developer",
            "engineer": "Engineer",
            "architect": "Architect",
            "designer": "Designer",
            "manager": "Manager",
            "director": "Director",
            "executive": "Executive",
            "officer": "Officer",
            "president": "President",
            "ceo": "CEO",
            "cfo": "CFO",
            "cto": "CTO",
            "coo": "COO",
            "cio": "CIO",
            "cso": "CSO",
            "cro": "CRO",
            "clco": "CLCO",
            "cmo": "CMO",
            "chro": "CHRO",
            "cgo": "CGO",
            "cpo": "CPO",
            "cdo": "CDO",
            "cvo": "CVO",
            "cbo": "CBO",
            "cco": "CCO",
            "cfo": "CFO",
            "cgo": "CGO",
            "cho": "CHO",
            "cio": "CIO",
            "cjo": "CJO",
            "cko": "CKO",
            "clo": "CLO",
            "cmo": "CMO",
            "cno": "CNO",
            "coo": "COO",
            "cpo": "CPO",
            "cqo": "CQO",
            "cro": "CRO",
            "cso": "CSO",
            "cto": "CTO",
            "cuo": "CUO",
            "cvo": "CVO",
            "cwo": "CWO",
            "cxo": "CXO",
            "cyo": "CYO",
            "czo": "CZO"
        }
    
    def get_publisher_name(self, publisher_id: str) -> str:
        """퍼블리셔 ID에서 이름을 추출하거나 매핑합니다."""
        # Publisher_X_hexstring 형식에서 hex 부분 추출
        if '_' in publisher_id:
            hex_part = publisher_id.split('_')[-1]
            
            # 알려진 퍼블리셔 이름 매핑 확인
            known_names = self.get_known_publisher_names()
            
            # hex 문자열을 바이트로 변환하여 패턴 매칭 시도
            try:
                if len(hex_part) >= 16:
                    # 첫 8바이트만 사용하여 패턴 매칭
                    first_bytes = bytes.fromhex(hex_part[:16])
                    
                    # 특정 패턴들 확인
                    if first_bytes.startswith(b'\x00\x00\x00\x00'):
                        return "Unknown Publisher (Zero Pattern)"
                    elif first_bytes.startswith(b'\xff\xff\xff\xff'):
                        return "Unknown Publisher (Max Pattern)"
                    elif all(b == 0 for b in first_bytes[:4]):
                        return "Unknown Publisher (Low Pattern)"
                    elif all(b == 255 for b in first_bytes[:4]):
                        return "Unknown Publisher (High Pattern)"
                    
                    # 알려진 퍼블리셔 패턴 매칭
                    for name, full_name in known_names.items():
                        if name.lower() in hex_part.lower():
                            return full_name
                    
                    # 공개키 패턴 분석
                    if hex_part.startswith('0000'):
                        return f"Publisher {publisher_id.split('_')[1]} (Low ID)"
                    elif hex_part.startswith('ffff'):
                        return f"Publisher {publisher_id.split('_')[1]} (High ID)"
                    else:
                        return f"Publisher {publisher_id.split('_')[1]} ({hex_part[:8]}...)"
                        
            except Exception:
                pass
        
        return f"Unknown Publisher ({publisher_id})"

def main():
    analyzer = PythFinalPublisherAnalyzer()
    
    print("PYTH Network 퍼블리셔 분석 시작...")
    
    # 모든 가격 피드 가져오기
    feeds = analyzer.get_all_price_feeds()
    if not feeds:
        print("가격 피드를 가져올 수 없습니다.")
        return
    
    print(f"총 {len(feeds)}개 가격 피드를 찾았습니다.")
    
    # 퍼블리셔 분석 수행
    results = analyzer.analyze_publishers(feeds, sample_size=100)
    
    if results:
        # 결과 저장
        analyzer.save_results(results)
    else:
        print("분석 결과가 없습니다.")

if __name__ == "__main__":
    main() 