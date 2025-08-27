#!/usr/bin/env python3
"""
PYTH SDK를 사용한 퍼블리셔 정보 가져오기
Pyth SDK를 사용하여 BTC 피드의 퍼블리셔 정보를 가져옵니다.
"""

import requests
import json
import time
import csv
import subprocess
import sys
from typing import Dict, List, Optional

class PythSDKPublishers:
    def __init__(self):
        self.base_url = "https://hermes.pyth.network"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def install_pyth_sdk(self):
        """Pyth SDK를 설치합니다."""
        print("📦 Pyth SDK 설치 중...")
        
        try:
            # pyth-client 설치
            subprocess.run([sys.executable, "-m", "pip", "install", "pyth-client"], 
                         check=True, capture_output=True)
            print("✅ pyth-client 설치 완료")
            
            # pyth-sdk 설치
            subprocess.run([sys.executable, "-m", "pip", "install", "pyth-sdk"], 
                         check=True, capture_output=True)
            print("✅ pyth-sdk 설치 완료")
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ SDK 설치 실패: {e}")
            return False
    
    def get_btc_feed_id(self) -> Optional[str]:
        """BTC/USD 피드 ID를 가져옵니다."""
        print("🔍 BTC/USD 피드 ID 가져오는 중...")
        
        try:
            response = self.session.get(f"{self.base_url}/v2/price_feeds", timeout=30)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    feeds = data
                else:
                    feeds = data.get('data', [])
                
                # BTC/USD 피드 찾기
                for feed in feeds:
                    attributes = feed.get('attributes', {})
                    symbol = attributes.get('display_symbol', '')
                    if symbol == 'BTC/USD':
                        feed_id = feed.get('id')
                        print(f"✅ BTC/USD 피드 ID: {feed_id}")
                        return feed_id
                
                print("❌ BTC/USD 피드를 찾을 수 없습니다.")
                return None
            else:
                print(f"❌ API 호출 실패: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"💥 오류 발생: {e}")
            return None
    
    def create_pyth_sdk_script(self, feed_id: str) -> str:
        """Pyth SDK를 사용하는 Python 스크립트를 생성합니다."""
        script = f'''
#!/usr/bin/env python3
"""
Pyth SDK를 사용한 BTC 피드 퍼블리셔 정보 가져오기
"""

import asyncio
import json
from pyth_client import PythClient
from pyth_client.models import PriceIdentifier

async def get_btc_publishers():
    """BTC 피드의 퍼블리셔 정보를 가져옵니다."""
    print("🚀 Pyth SDK로 BTC 피드 퍼블리셔 정보 가져오기")
    
    try:
        # Pyth 클라이언트 생성
        client = PythClient()
        
        # BTC 피드 ID
        btc_feed_id = "{feed_id}"
        print(f"📊 BTC 피드 ID: {{btc_feed_id}}")
        
        # 피드 정보 가져오기
        print("🔍 피드 정보 가져오는 중...")
        
        # 모든 가격 피드 가져오기
        all_feeds = await client.get_all_price_feeds()
        print(f"✅ 총 {{len(all_feeds)}}개의 피드를 가져왔습니다.")
        
        # BTC 피드 찾기
        btc_feed = None
        for feed in all_feeds:
            if hasattr(feed, 'id') and str(feed.id) == btc_feed_id:
                btc_feed = feed
                break
        
        if not btc_feed:
            print("❌ BTC 피드를 찾을 수 없습니다.")
            return None
        
        print(f"✅ BTC 피드 발견: {{btc_feed}}")
        
        # 퍼블리셔 정보 가져오기
        print("🔍 퍼블리셔 정보 가져오는 중...")
        
        # 피드의 퍼블리셔 정보
        publishers = []
        
        # 피드 속성에서 퍼블리셔 정보 찾기
        if hasattr(btc_feed, 'price_feeds'):
            for price_feed in btc_feed.price_feeds:
                if hasattr(price_feed, 'publishers'):
                    for publisher in price_feed.publishers:
                        pub_info = {{
                            'id': str(publisher.id) if hasattr(publisher, 'id') else 'Unknown',
                            'name': getattr(publisher, 'name', 'Unknown'),
                            'authority': str(publisher.authority) if hasattr(publisher, 'authority') else 'Unknown'
                        }}
                        publishers.append(pub_info)
        
        # 피드 메타데이터에서 퍼블리셔 정보 찾기
        if hasattr(btc_feed, 'metadata'):
            metadata = btc_feed.metadata
            if hasattr(metadata, 'publishers'):
                for publisher in metadata.publishers:
                    pub_info = {{
                        'id': str(publisher.id) if hasattr(publisher, 'id') else 'Unknown',
                        'name': getattr(publisher, 'name', 'Unknown'),
                        'authority': str(publisher.authority) if hasattr(publisher, 'authority') else 'Unknown'
                    }}
                    publishers.append(pub_info)
        
        print(f"✅ {{len(publishers)}}개의 퍼블리셔 정보를 찾았습니다.")
        
        return {{
            'feed_id': btc_feed_id,
            'publishers': publishers,
            'total_publishers': len(publishers),
            'feed_info': str(btc_feed)
        }}
        
    except Exception as e:
        print(f"💥 오류 발생: {{e}}")
        return None

async def main():
    result = await get_btc_publishers()
    
    if result:
        print("\\n📊 결과:")
        print(json.dumps(result, indent=2, default=str))
        
        # 파일로 저장
        with open('pyth_sdk_publishers_result.json', 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print("\\n📄 결과가 pyth_sdk_publishers_result.json에 저장되었습니다.")
    else:
        print("❌ 퍼블리셔 정보를 가져올 수 없습니다.")

if __name__ == "__main__":
    asyncio.run(main())
'''
        return script
    
    def run_pyth_sdk_script(self, script: str) -> Dict:
        """Pyth SDK 스크립트를 실행합니다."""
        print("🚀 Pyth SDK 스크립트 실행 중...")
        
        try:
            # 스크립트를 임시 파일로 저장
            script_file = "temp_pyth_sdk_script.py"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script)
            
            # 스크립트 실행
            result = subprocess.run([sys.executable, script_file], 
                                  capture_output=True, text=True, timeout=60)
            
            print("📊 스크립트 실행 결과:")
            print(result.stdout)
            
            if result.stderr:
                print("⚠️  오류:")
                print(result.stderr)
            
            # 결과 파일 읽기
            try:
                with open('pyth_sdk_publishers_result.json', 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                return {'error': '결과 파일을 찾을 수 없습니다.'}
                
        except subprocess.TimeoutExpired:
            print("❌ 스크립트 실행 시간 초과")
            return {'error': '스크립트 실행 시간 초과'}
        except Exception as e:
            print(f"💥 스크립트 실행 실패: {e}")
            return {'error': str(e)}
    
    def try_alternative_sdk_approaches(self) -> Dict:
        """대안적인 SDK 접근 방법들을 시도합니다."""
        print("🔍 대안적인 SDK 접근 방법 시도 중...")
        
        approaches = [
            # 1. pyth-client 직접 사용
            '''
import asyncio
from pyth_client import PythClient

async def get_publishers():
    client = PythClient()
    feeds = await client.get_all_price_feeds()
    print(f"총 {len(feeds)}개 피드")
    return feeds

asyncio.run(get_publishers())
''',
            # 2. pyth-sdk 사용
            '''
import asyncio
from pyth_sdk import PythClient

async def get_publishers():
    client = PythClient()
    # SDK 메서드들 시도
    return "SDK 접근 시도"

asyncio.run(get_publishers())
''',
            # 3. Solana RPC 직접 사용
            '''
import requests
import json

def get_pyth_accounts():
    url = "https://api.mainnet-beta.solana.com"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getProgramAccounts",
        "params": [
            "Pyth11111111111111111111111111111111111111112",
            {
                "encoding": "base64",
                "filters": [
                    {
                        "dataSize": 1000
                    }
                ]
            }
        ]
    }
    
    response = requests.post(url, json=payload)
    return response.json()

result = get_pyth_accounts()
print(json.dumps(result, indent=2))
'''
        ]
        
        results = {}
        
        for i, approach in enumerate(approaches, 1):
            print(f"\n🔍 접근 방법 {i} 시도 중...")
            
            try:
                script_file = f"temp_approach_{i}.py"
                with open(script_file, 'w', encoding='utf-8') as f:
                    f.write(approach)
                
                result = subprocess.run([sys.executable, script_file], 
                                      capture_output=True, text=True, timeout=30)
                
                results[f'approach_{i}'] = {
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'return_code': result.returncode
                }
                
                print(f"✅ 접근 방법 {i} 완료")
                
            except Exception as e:
                results[f'approach_{i}'] = {
                    'error': str(e)
                }
                print(f"❌ 접근 방법 {i} 실패: {e}")
        
        return results
    
    def get_btc_publishers(self) -> Dict:
        """BTC 피드의 퍼블리셔 정보를 가져옵니다."""
        print("🚀 Pyth SDK를 사용한 BTC 피드 퍼블리셔 정보 가져오기")
        print("=" * 70)
        
        # 1. Pyth SDK 설치
        if not self.install_pyth_sdk():
            print("❌ SDK 설치에 실패했습니다.")
            return {'success': False, 'error': 'SDK 설치 실패'}
        
        # 2. BTC 피드 ID 가져오기
        feed_id = self.get_btc_feed_id()
        if not feed_id:
            return {'success': False, 'error': 'BTC 피드 ID를 찾을 수 없습니다.'}
        
        # 3. Pyth SDK 스크립트 생성 및 실행
        script = self.create_pyth_sdk_script(feed_id)
        sdk_result = self.run_pyth_sdk_script(script)
        
        # 4. 대안적인 접근 방법들 시도
        alternative_results = self.try_alternative_sdk_approaches()
        
        return {
            'success': True,
            'feed_id': feed_id,
            'sdk_result': sdk_result,
            'alternative_results': alternative_results
        }
    
    def save_results(self, results: Dict, filename: str = "pyth_sdk_publishers.json"):
        """결과를 파일로 저장합니다."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 JSON 결과가 {filename}에 저장되었습니다.")
    
    def print_summary(self, results: Dict):
        """결과 요약을 출력합니다."""
        print("\n" + "="*60)
        print("📊 Pyth SDK 퍼블리셔 분석 결과")
        print("="*60)
        
        if not results.get('success'):
            print(f"❌ 실패: {results.get('error', '알 수 없는 오류')}")
            return
        
        feed_id = results.get('feed_id', 'Unknown')
        sdk_result = results.get('sdk_result', {})
        alternative_results = results.get('alternative_results', {})
        
        print(f"📈 기본 정보:")
        print(f"  • BTC 피드 ID: {feed_id}")
        
        if 'error' not in sdk_result:
            publishers = sdk_result.get('publishers', [])
            total_publishers = sdk_result.get('total_publishers', 0)
            print(f"  • 총 퍼블리셔 수: {total_publishers}개")
            
            if publishers:
                print(f"\n🏆 퍼블리셔 리스트:")
                for i, pub in enumerate(publishers[:10], 1):
                    name = pub.get('name', 'Unknown')
                    pub_id = pub.get('id', 'Unknown')
                    print(f"  {i:2d}. {name} (ID: {pub_id})")
                
                if len(publishers) > 10:
                    print(f"  ... 그리고 {len(publishers) - 10}개 더")
            else:
                print(f"\n⚠️  퍼블리셔 정보를 찾을 수 없습니다.")
        else:
            print(f"  • SDK 결과: {sdk_result.get('error', '알 수 없는 오류')}")
        
        print(f"\n📊 대안적 접근 방법 결과:")
        for approach, result in alternative_results.items():
            if 'error' in result:
                print(f"  • {approach}: 실패 - {result['error']}")
            else:
                print(f"  • {approach}: 성공 (코드: {result.get('return_code', 'N/A')})")

def main():
    print("🚀 Pyth SDK를 사용한 퍼블리셔 정보 가져오기")
    print("=" * 70)
    
    sdk_publishers = PythSDKPublishers()
    
    # BTC 피드 퍼블리셔 가져오기
    results = sdk_publishers.get_btc_publishers()
    
    if results.get('success'):
        # 결과 출력
        sdk_publishers.print_summary(results)
        
        # 결과 저장
        sdk_publishers.save_results(results)
        
        print(f"\n✅ 분석 완료!")
    else:
        print(f"❌ 실패: {results.get('error', '알 수 없는 오류')}")

if __name__ == "__main__":
    main() 