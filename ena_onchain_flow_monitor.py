#!/usr/bin/env python3
"""
ENA 온체인 유통량 모니터링
거래소 유입/유출을 time series로 추적하고 분석
"""

import requests
import time
import logging
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ena_onchain_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ENAOnchainFlowMonitor:
    def __init__(self):
        # ENA 토큰 컨트랙트 주소 (Ethereum) - Ethena 프로젝트
        self.ena_contract = "0x183015a9bA6Ff6D4A0c8C0c0c0c0c0c0c0c0c0c0"  # 실제 ENA 컨트랙트 주소로 교체 필요
        
        # 주요 거래소 주소들 (실제 주소들)
        self.exchange_addresses = {
            'Binance': '0x28C6c06298d514Db089934071355E5743bf21d60',
            'Coinbase': '0xA090e606E30bD747d4E6245a1517EbE430F0057e',
            'Kraken': '0x2910543Af39abA0Cd09dBb2D50200b3E800A63D2',
            'OKX': '0x6cC5F688a315f3dC28A7781717a9A798aF8e0387',
            'Bybit': '0x0639556F03714A74a5fEEaF5736a4A64fF70D206',
            'KuCoin': '0x2B5634C42055806a59e9107ED44D43c426E58258',
            'Gate.io': '0x0D0707963952f2fBA59dD06f2b425ace40b492Fe',
            'Bitfinex': '0x876EabF441B2EE5B5b0554Fd502a8E0600950cFa',
            'Gemini': '0x07ee55aA4f356cFba34D1c477D93A8Faf4f2c409',
            'Uniswap V3': '0xE592427A0AEce92De3Edee1F18E0157C05861564',
            'Uniswap V2': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
            'SushiSwap': '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F',
            '1inch': '0x1111111254EEB25477B68fb85Ed929f73A960582'
        }
        
        # API 키들
        self.etherscan_api_key = os.getenv("ETHERSCAN_API_KEY")
        self.etherscan_base_url = "https://api.etherscan.io/api"
        
        # 데이터 저장소
        self.flow_data = []
        self.last_block = 0
        
        logger.info(f"🚀 ENA 온체인 유통량 모니터링 시작")
        logger.info(f"📊 모니터링 거래소: {len(self.exchange_addresses)}개")
        logger.info(f"🔗 ENA 컨트랙트: {self.ena_contract}")
    
    def get_latest_block(self) -> Optional[int]:
        """최신 블록 번호를 가져옵니다."""
        try:
            params = {
                'module': 'proxy',
                'action': 'eth_blockNumber',
                'apikey': self.etherscan_api_key
            }
            
            response = requests.get(self.etherscan_base_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            if data['status'] == '1':
                block_number = int(data['result'], 16)
                logger.info(f"📦 최신 블록: {block_number:,}")
                return block_number
            else:
                logger.error(f"Etherscan API 오류: {data.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"최신 블록 조회 오류: {e}")
            return None
    
    def get_ena_transfers(self, start_block: int, end_block: int) -> List[Dict]:
        """ENA 토큰 전송 내역을 가져옵니다."""
        try:
            params = {
                'module': 'account',
                'action': 'tokentx',
                'contractaddress': self.ena_contract,
                'startblock': start_block,
                'endblock': end_block,
                'sort': 'asc',
                'apikey': self.etherscan_api_key
            }
            
            response = requests.get(self.etherscan_base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data['status'] == '1':
                transfers = data['result']
                logger.info(f"📊 {start_block:,} ~ {end_block:,} 블록에서 {len(transfers)}개 전송 발견")
                return transfers
            else:
                logger.error(f"Etherscan API 오류: {data.get('message', 'Unknown error')}")
                return []
                
        except Exception as e:
            logger.error(f"ENA 전송 내역 조회 오류: {e}")
            return []
    
    def analyze_transfer_flow(self, transfers: List[Dict]) -> Dict:
        """전송 내역을 분석하여 유입/유출 패턴을 파악합니다."""
        flow_analysis = {
            'total_transfers': len(transfers),
            'total_volume': 0,
            'exchange_inflows': {},
            'exchange_outflows': {},
            'large_transfers': [],
            'time_distribution': {},
            'gas_analysis': {
                'total_gas_used': 0,
                'avg_gas_price': 0,
                'gas_costs': []
            }
        }
        
        if not transfers:
            return flow_analysis
        
        gas_prices = []
        gas_used = []
        
        for transfer in transfers:
            try:
                # 전송량 계산 (18 decimals 가정)
                value = float(transfer['value']) / (10 ** 18)
                flow_analysis['total_volume'] += value
                
                # 가스 분석
                if 'gasPrice' in transfer and 'gasUsed' in transfer:
                    gas_price = int(transfer['gasPrice'], 16) / (10 ** 9)  # Gwei
                    gas_used_val = int(transfer['gasUsed'], 16)
                    
                    gas_prices.append(gas_price)
                    gas_used.append(gas_used_val)
                    flow_analysis['gas_analysis']['total_gas_used'] += gas_used_val
                
                # 거래소 유입/유출 분석
                from_addr = transfer['from'].lower()
                to_addr = transfer['to'].lower()
                
                # 거래소에서 유출 (거래소 -> 일반 주소)
                if from_addr in [addr.lower() for addr in self.exchange_addresses.values()]:
                    exchange_name = [name for name, addr in self.exchange_addresses.items() 
                                   if addr.lower() == from_addr][0]
                    
                    if exchange_name not in flow_analysis['exchange_outflows']:
                        flow_analysis['exchange_outflows'][exchange_name] = {
                            'count': 0,
                            'volume': 0,
                            'transactions': []
                        }
                    
                    flow_analysis['exchange_outflows'][exchange_name]['count'] += 1
                    flow_analysis['exchange_outflows'][exchange_name]['volume'] += value
                    flow_analysis['exchange_outflows'][exchange_name]['transactions'].append({
                        'hash': transfer['hash'],
                        'value': value,
                        'timestamp': int(transfer['timeStamp']),
                        'to': to_addr
                    })
                
                # 거래소로 유입 (일반 주소 -> 거래소)
                if to_addr in [addr.lower() for addr in self.exchange_addresses.values()]:
                    exchange_name = [name for name, addr in self.exchange_addresses.items() 
                                   if addr.lower() == to_addr][0]
                    
                    if exchange_name not in flow_analysis['exchange_inflows']:
                        flow_analysis['exchange_inflows'][exchange_name] = {
                            'count': 0,
                            'volume': 0,
                            'transactions': []
                        }
                    
                    flow_analysis['exchange_inflows'][exchange_name]['count'] += 1
                    flow_analysis['exchange_inflows'][exchange_name]['volume'] += value
                    flow_analysis['exchange_inflows'][exchange_name]['transactions'].append({
                        'hash': transfer['hash'],
                        'value': value,
                        'timestamp': int(transfer['timeStamp']),
                        'from': from_addr
                    })
                
                # 대량 전송 분석 (1000 ENA 이상)
                if value >= 1000:
                    flow_analysis['large_transfers'].append({
                        'hash': transfer['hash'],
                        'from': from_addr,
                        'to': to_addr,
                        'value': value,
                        'timestamp': int(transfer['timeStamp'])
                    })
                
                # 시간 분포 분석
                timestamp = int(transfer['timeStamp'])
                hour = datetime.fromtimestamp(timestamp).hour
                if hour not in flow_analysis['time_distribution']:
                    flow_analysis['time_distribution'][hour] = {
                        'count': 0,
                        'volume': 0
                    }
                flow_analysis['time_distribution'][hour]['count'] += 1
                flow_analysis['time_distribution'][hour]['volume'] += value
                
            except Exception as e:
                logger.warning(f"전송 분석 중 오류: {e}")
                continue
        
        # 가스 분석 완성
        if gas_prices:
            flow_analysis['gas_analysis']['avg_gas_price'] = sum(gas_prices) / len(gas_prices)
            flow_analysis['gas_analysis']['gas_costs'] = [price * used for price, used in zip(gas_prices, gas_used)]
        
        return flow_analysis
    
    def get_ena_price_data(self) -> Optional[Dict]:
        """ENA 현재 가격 정보를 가져옵니다."""
        try:
            # CoinGecko API 사용
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': 'ena',
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_market_cap': 'true'
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            if 'ena' in data:
                ena_data = data['ena']
                return {
                    'price_usd': ena_data.get('usd', 0),
                    'price_change_24h': ena_data.get('usd_24h_change', 0),
                    'volume_24h': ena_data.get('usd_24h_vol', 0),
                    'market_cap': ena_data.get('usd_market_cap', 0)
                }
            else:
                logger.warning("CoinGecko에서 ENA 데이터를 찾을 수 없습니다.")
                return None
                
        except Exception as e:
            logger.error(f"ENA 가격 데이터 조회 오류: {e}")
            return None
    
    def monitor_flow_once(self, block_range: int = 1000) -> Optional[Dict]:
        """한 번의 유통량 모니터링을 수행합니다."""
        try:
            logger.info("🔄 ENA 온체인 유통량 모니터링 시작...")
            
            # 최신 블록 번호 가져오기
            latest_block = self.get_latest_block()
            if latest_block is None:
                return None
            
            # 블록 범위 설정
            if self.last_block == 0:
                start_block = max(0, latest_block - block_range)
            else:
                start_block = self.last_block + 1
            
            end_block = latest_block
            
            if start_block >= end_block:
                logger.info("새로운 블록이 없습니다.")
                return None
            
            logger.info(f"📊 블록 범위: {start_block:,} ~ {end_block:,}")
            
            # ENA 전송 내역 가져오기
            transfers = self.get_ena_transfers(start_block, end_block)
            
            if not transfers:
                logger.info("새로운 ENA 전송이 없습니다.")
                self.last_block = end_block
                return None
            
            # 전송 분석
            flow_analysis = self.analyze_transfer_flow(transfers)
            
            # 가격 데이터 추가
            price_data = self.get_ena_price_data()
            if price_data:
                flow_analysis['price_data'] = price_data
            
            # 타임스탬프 추가
            flow_analysis['timestamp'] = datetime.now().isoformat()
            flow_analysis['block_range'] = f"{start_block:,} ~ {end_block:,}"
            
            # 데이터 저장
            self.flow_data.append(flow_analysis)
            
            # 마지막 블록 업데이트
            self.last_block = end_block
            
            # 로그 출력
            self.log_flow_analysis(flow_analysis)
            
            return flow_analysis
            
        except Exception as e:
            logger.error(f"유통량 모니터링 중 오류: {e}")
            return None
    
    def log_flow_analysis(self, analysis: Dict):
        """유통량 분석 결과를 로그에 기록합니다."""
        logger.info("=" * 80)
        logger.info("📊 ENA 온체인 유통량 분석 결과")
        logger.info("=" * 80)
        logger.info(f"⏰ 시간: {analysis.get('timestamp', 'N/A')}")
        logger.info(f"📦 블록 범위: {analysis.get('block_range', 'N/A')}")
        logger.info(f"🔄 총 전송 수: {analysis['total_transfers']:,}")
        logger.info(f"💰 총 전송량: {analysis['total_volume']:,.2f} ENA")
        
        # 가격 정보
        if 'price_data' in analysis:
            price = analysis['price_data']
            logger.info(f"💵 현재 가격: ${price['price_usd']:.6f}")
            logger.info(f"📈 24시간 변화: {price['price_change_24h']:.2f}%")
            logger.info(f"📊 24시간 거래량: ${price['volume_24h']:,.0f}")
            logger.info(f"🏦 시가총액: ${price['market_cap']:,.0f}")
        
        # 거래소 유입/유출 요약
        total_inflow = sum(ex['volume'] for ex in analysis['exchange_inflows'].values())
        total_outflow = sum(ex['volume'] for ex in analysis['exchange_outflows'].values())
        
        logger.info(f"📥 거래소 총 유입: {total_inflow:,.2f} ENA")
        logger.info(f"📤 거래소 총 유출: {total_outflow:,.2f} ENA")
        logger.info(f"📊 순 유입: {total_inflow - total_outflow:,.2f} ENA")
        
        # 대량 전송
        if analysis['large_transfers']:
            logger.info(f"🐋 대량 전송 (1000+ ENA): {len(analysis['large_transfers'])}건")
        
        # 가스 분석
        gas_analysis = analysis['gas_analysis']
        if gas_analysis['total_gas_used'] > 0:
            logger.info(f"⛽ 총 가스 사용량: {gas_analysis['total_gas_used']:,}")
            logger.info(f"💰 평균 가스 가격: {gas_analysis['avg_gas_price']:.2f} Gwei")
        
        logger.info("=" * 80)
    
    def get_flow_summary(self, hours: int = 24) -> Dict:
        """지정된 시간 동안의 유통량 요약을 제공합니다."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            recent_data = [
                data for data in self.flow_data 
                if datetime.fromisoformat(data['timestamp']) > cutoff_time
            ]
            
            if not recent_data:
                return {"error": "데이터가 없습니다."}
            
            summary = {
                'period_hours': hours,
                'total_flows': len(recent_data),
                'total_volume': sum(data['total_volume'] for data in recent_data),
                'total_transfers': sum(data['total_transfers'] for data in recent_data),
                'exchange_summary': {},
                'hourly_distribution': {},
                'large_transfers_count': sum(len(data['large_transfers']) for data in recent_data)
            }
            
            # 거래소별 요약
            all_exchanges = set()
            for data in recent_data:
                all_exchanges.update(data['exchange_inflows'].keys())
                all_exchanges.update(data['exchange_outflows'].keys())
            
            for exchange in all_exchanges:
                total_inflow = sum(
                    data['exchange_inflows'].get(exchange, {}).get('volume', 0) 
                    for data in recent_data
                )
                total_outflow = sum(
                    data['exchange_outflows'].get(exchange, {}).get('volume', 0) 
                    for data in recent_data
                )
                
                summary['exchange_summary'][exchange] = {
                    'total_inflow': total_inflow,
                    'total_outflow': total_outflow,
                    'net_flow': total_inflow - total_outflow
                }
            
            # 시간별 분포
            for data in recent_data:
                for hour, hour_data in data['time_distribution'].items():
                    if hour not in summary['hourly_distribution']:
                        summary['hourly_distribution'][hour] = {'count': 0, 'volume': 0}
                    summary['hourly_distribution'][hour]['count'] += hour_data['count']
                    summary['hourly_distribution'][hour]['volume'] += hour_data['volume']
            
            return summary
            
        except Exception as e:
            logger.error(f"유통량 요약 생성 오류: {e}")
            return {"error": str(e)}
    
    def export_raw_data(self, filename: str = None) -> str:
        """원시 데이터를 JSON 파일로 내보냅니다."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ena_flow_data_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.flow_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📁 원시 데이터 내보내기 완료: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"데이터 내보내기 오류: {e}")
            return None
    
    def export_summary_csv(self, filename: str = None) -> str:
        """요약 데이터를 CSV 파일로 내보냅니다."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ena_flow_summary_{timestamp}.csv"
        
        try:
            # 24시간 요약 데이터
            summary_24h = self.get_flow_summary(24)
            summary_7d = self.get_flow_summary(168)  # 7일
            
            # CSV 데이터 준비
            csv_data = []
            
            # 24시간 요약
            csv_data.append({
                'period': '24h',
                'total_flows': summary_24h.get('total_flows', 0),
                'total_volume': summary_24h.get('total_volume', 0),
                'total_transfers': summary_24h.get('total_transfers', 0),
                'large_transfers': summary_24h.get('large_transfers_count', 0)
            })
            
            # 7일 요약
            csv_data.append({
                'period': '7d',
                'total_flows': summary_7d.get('total_flows', 0),
                'total_volume': summary_7d.get('total_volume', 0),
                'total_transfers': summary_7d.get('total_transfers', 0),
                'large_transfers': summary_7d.get('large_transfers_count', 0)
            })
            
            # 거래소별 데이터
            for exchange, data in summary_24h.get('exchange_summary', {}).items():
                csv_data.append({
                    'period': f'24h_{exchange}',
                    'total_inflow': data['total_inflow'],
                    'total_outflow': data['total_outflow'],
                    'net_flow': data['net_flow']
                })
            
            # DataFrame으로 변환하여 CSV 저장
            df = pd.DataFrame(csv_data)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            
            logger.info(f"📊 요약 데이터 CSV 내보내기 완료: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"CSV 내보내기 오류: {e}")
            return None
    
    def start_monitoring(self, interval_seconds: int = 300, block_range: int = 1000):
        """지속적인 유통량 모니터링을 시작합니다."""
        logger.info(f"🚀 ENA 온체인 유통량 모니터링 시작")
        logger.info(f"⏰ 모니터링 간격: {interval_seconds}초")
        logger.info(f"📦 블록 범위: {block_range:,}")
        logger.info("=" * 60)
        
        # 즉시 한 번 실행
        self.monitor_flow_once(block_range)
        
        try:
            while True:
                time.sleep(interval_seconds)
                self.monitor_flow_once(block_range)
                
        except KeyboardInterrupt:
            logger.info("⏹️  모니터링 중단됨")
            
            # 종료 시 데이터 내보내기
            logger.info("📁 모니터링 종료, 데이터 내보내기 중...")
            self.export_raw_data()
            self.export_summary_csv()
            
        except Exception as e:
            logger.error(f"❌ 모니터링 루프 오류: {e}")

def main():
    """메인 함수"""
    print("🚀 ENA 온체인 유통량 모니터링 시작")
    print("=" * 50)
    
    # Etherscan API 키 확인
    if not os.getenv("ETHERSCAN_API_KEY"):
        print("⚠️  ETHERSCAN_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("📝 .env 파일에 Etherscan API 키를 추가하세요.")
        return
    
    # 모니터링 봇 생성
    monitor = ENAOnchainFlowMonitor()
    
    # 모니터링 간격 설정 (초 단위, 기본 5분)
    interval = int(os.getenv("ENA_MONITORING_INTERVAL", "300"))
    
    # 블록 범위 설정
    block_range = int(os.getenv("ENA_BLOCK_RANGE", "1000"))
    
    try:
        # 한 번 실행하여 데이터 수집
        print("📊 초기 데이터 수집 중...")
        initial_data = monitor.monitor_flow_once(block_range)
        
        if initial_data:
            print("✅ 초기 데이터 수집 완료")
            
            # 요약 정보 출력
            summary_24h = monitor.get_flow_summary(24)
            if 'error' not in summary_24h:
                print(f"\n📊 24시간 요약:")
                print(f"   총 유통량: {summary_24h['total_volume']:,.2f} ENA")
                print(f"   총 전송 수: {summary_24h['total_transfers']:,}")
                print(f"   대량 전송: {summary_24h['large_transfers_count']}건")
            
            # 원시 데이터 내보내기
            raw_file = monitor.export_raw_data()
            csv_file = monitor.export_summary_csv()
            
            if raw_file:
                print(f"📁 원시 데이터: {raw_file}")
            if csv_file:
                print(f"📊 요약 데이터: {csv_file}")
            
            # 지속 모니터링 시작 여부 확인
            if os.getenv("ENA_CONTINUOUS_MONITORING", "false").lower() == "true":
                print(f"\n🔄 지속 모니터링 시작 (간격: {interval}초)")
                monitor.start_monitoring(interval, block_range)
            else:
                print("\n✅ 일회성 모니터링 완료")
                
        else:
            print("❌ 초기 데이터 수집 실패")
            
    except Exception as e:
        logger.error(f"모니터링 시작 실패: {e}")

if __name__ == "__main__":
    main() 