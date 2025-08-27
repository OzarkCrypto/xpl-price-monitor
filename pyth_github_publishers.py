#!/usr/bin/env python3
"""
GitHub를 통한 PYTH 퍼블리셔 정보 검색
GitHub에서 Pyth 관련 저장소를 검색하여 퍼블리셔 정보를 찾습니다.
"""

import requests
import json
import time
import csv
import re
from typing import Dict, List, Optional

class PythGitHubPublishers:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # GitHub API 토큰 (선택사항)
        self.github_token = None
    
    def search_github_repos(self, query: str) -> List[Dict]:
        """GitHub 저장소를 검색합니다."""
        print(f"🔍 GitHub 저장소 검색: {query}")
        
        url = "https://api.github.com/search/repositories"
        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': 10
        }
        
        if self.github_token:
            headers = {'Authorization': f'token {self.github_token}'}
        else:
            headers = {}
        
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                repos = data.get('items', [])
                print(f"✅ {len(repos)}개의 저장소를 찾았습니다.")
                return repos
            else:
                print(f"❌ GitHub API 호출 실패: HTTP {response.status_code}")
                return []
        except Exception as e:
            print(f"💥 GitHub 검색 오류: {e}")
            return []
    
    def get_repo_content(self, owner: str, repo: str, path: str = "") -> List[Dict]:
        """저장소의 파일 목록을 가져옵니다."""
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        
        if self.github_token:
            headers = {'Authorization': f'token {self.github_token}'}
        else:
            headers = {}
        
        try:
            response = self.session.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 저장소 내용 가져오기 실패: HTTP {response.status_code}")
                return []
        except Exception as e:
            print(f"💥 저장소 내용 가져오기 오류: {e}")
            return []
    
    def get_file_content(self, owner: str, repo: str, path: str) -> Optional[str]:
        """파일 내용을 가져옵니다."""
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        
        if self.github_token:
            headers = {'Authorization': f'token {self.github_token}'}
        else:
            headers = {}
        
        try:
            response = self.session.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get('type') == 'file':
                    import base64
                    content = base64.b64decode(data['content']).decode('utf-8')
                    return content
            else:
                print(f"❌ 파일 내용 가져오기 실패: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"💥 파일 내용 가져오기 오류: {e}")
            return None
    
    def search_publisher_info_in_content(self, content: str) -> List[Dict]:
        """파일 내용에서 퍼블리셔 정보를 검색합니다."""
        publishers = []
        
        # 퍼블리셔 관련 키워드 검색
        publisher_patterns = [
            r'publisher["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'authority["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'validator["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'([A-Za-z0-9]{32,})["\']?\s*[:=]\s*["\']?publisher["\']?',
            r'([A-Za-z0-9]{32,})["\']?\s*[:=]\s*["\']?authority["\']?'
        ]
        
        for pattern in publisher_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                
                if len(match) > 10:  # 의미있는 길이
                    publishers.append({
                        'type': 'pattern_match',
                        'value': match,
                        'pattern': pattern
                    })
        
        # 알려진 퍼블리셔 이름 검색
        known_publishers = [
            'binance', 'coinbase', 'kraken', 'bitfinex', 'okx', 'bybit',
            'jump', 'alameda', 'wintermute', 'gts', 'virtu', 'citadel',
            'drw', 'optiver', 'flow', 'xtx', 'goldman', 'jpmorgan'
        ]
        
        for pub in known_publishers:
            if pub.lower() in content.lower():
                publishers.append({
                    'type': 'known_publisher',
                    'value': pub,
                    'context': self.extract_context(content, pub)
                })
        
        return publishers
    
    def extract_context(self, content: str, keyword: str, context_size: int = 100) -> str:
        """키워드 주변의 컨텍스트를 추출합니다."""
        try:
            index = content.lower().find(keyword.lower())
            if index != -1:
                start = max(0, index - context_size)
                end = min(len(content), index + len(keyword) + context_size)
                return content[start:end].replace('\n', ' ').strip()
        except:
            pass
        return ""
    
    def search_pyth_repos(self) -> List[Dict]:
        """Pyth 관련 저장소들을 검색합니다."""
        print("🔍 Pyth 관련 GitHub 저장소 검색 중...")
        
        search_queries = [
            'pyth network',
            'pyth oracle',
            'pyth price feed',
            'pyth publisher',
            'pyth solana'
        ]
        
        all_repos = []
        
        for query in search_queries:
            repos = self.search_github_repos(query)
            all_repos.extend(repos)
            time.sleep(1)  # GitHub API 레이트 리밋 방지
        
        # 중복 제거
        unique_repos = []
        seen_repos = set()
        
        for repo in all_repos:
            repo_id = repo.get('full_name', '')
            if repo_id not in seen_repos:
                seen_repos.add(repo_id)
                unique_repos.append(repo)
        
        print(f"✅ 총 {len(unique_repos)}개의 고유 저장소를 찾았습니다.")
        return unique_repos
    
    def analyze_pyth_repos(self, repos: List[Dict]) -> Dict:
        """Pyth 저장소들을 분석합니다."""
        print("🔍 Pyth 저장소 분석 중...")
        
        publisher_info = []
        analyzed_repos = []
        
        for i, repo in enumerate(repos[:10]):  # 처음 10개만 분석
            owner = repo.get('owner', {}).get('login', '')
            repo_name = repo.get('name', '')
            full_name = repo.get('full_name', '')
            
            print(f"📊 저장소 {i+1}/10 분석 중: {full_name}")
            
            # 저장소 내용 가져오기
            contents = self.get_repo_content(owner, repo_name)
            
            if contents:
                repo_publishers = []
                
                # 주요 파일들 검색
                important_files = [
                    'README.md', 'publishers.md', 'publisher.md',
                    'src/publishers.ts', 'src/publisher.ts',
                    'lib/publishers.js', 'lib/publisher.js',
                    'docs/publishers.md', 'docs/publisher.md'
                ]
                
                for file_info in contents:
                    if isinstance(file_info, dict):
                        file_name = file_info.get('name', '')
                        file_path = file_info.get('path', '')
                        
                        # 중요 파일이나 퍼블리셔 관련 파일 검색
                        if any(important in file_name.lower() for important in ['publisher', 'authority', 'validator']):
                            print(f"  📄 파일 분석: {file_path}")
                            
                            file_content = self.get_file_content(owner, repo_name, file_path)
                            if file_content:
                                publishers = self.search_publisher_info_in_content(file_content)
                                repo_publishers.extend(publishers)
                                print(f"    ✅ {len(publishers)}개 퍼블리셔 정보 발견")
                
                if repo_publishers:
                    analyzed_repos.append({
                        'repo': full_name,
                        'description': repo.get('description', ''),
                        'stars': repo.get('stargazers_count', 0),
                        'publishers': repo_publishers
                    })
                    publisher_info.extend(repo_publishers)
        
        return {
            'analyzed_repos': analyzed_repos,
            'total_publishers': len(publisher_info),
            'publishers': publisher_info
        }
    
    def search_pyth_documentation(self) -> Dict:
        """Pyth 공식 문서에서 퍼블리셔 정보를 검색합니다."""
        print("🔍 Pyth 공식 문서 검색 중...")
        
        # Pyth 공식 저장소들
        official_repos = [
            {'owner': 'pyth-network', 'repo': 'pyth-client-js'},
            {'owner': 'pyth-network', 'repo': 'pyth-sdk-js'},
            {'owner': 'pyth-network', 'repo': 'pyth-client-py'},
            {'owner': 'pyth-network', 'repo': 'pyth-sdk-py'},
            {'owner': 'pyth-network', 'repo': 'pyth-crosschain'},
            {'owner': 'pyth-network', 'repo': 'pyth-docs'}
        ]
        
        documentation_publishers = []
        
        for repo_info in official_repos:
            owner = repo_info['owner']
            repo = repo_info['repo']
            
            print(f"📊 공식 저장소 분석: {owner}/{repo}")
            
            # 저장소 내용 가져오기
            contents = self.get_repo_content(owner, repo)
            
            if contents:
                for file_info in contents:
                    if isinstance(file_info, dict):
                        file_name = file_info.get('name', '')
                        file_path = file_info.get('path', '')
                        
                        # 문서나 코드 파일 검색
                        if any(ext in file_name for ext in ['.md', '.ts', '.js', '.py', '.txt']):
                            file_content = self.get_file_content(owner, repo, file_path)
                            if file_content:
                                publishers = self.search_publisher_info_in_content(file_content)
                                if publishers:
                                    documentation_publishers.extend(publishers)
                                    print(f"  ✅ {file_path}에서 {len(publishers)}개 퍼블리셔 정보 발견")
        
        return {
            'documentation_publishers': documentation_publishers,
            'total_documentation_publishers': len(documentation_publishers)
        }
    
    def get_btc_publishers(self) -> Dict:
        """BTC 피드의 퍼블리셔 정보를 GitHub에서 검색합니다."""
        print("🚀 GitHub를 통한 BTC 피드 퍼블리셔 정보 검색")
        print("=" * 70)
        
        # 1. Pyth 관련 저장소 검색
        repos = self.search_pyth_repos()
        
        # 2. 저장소 분석
        repo_analysis = self.analyze_pyth_repos(repos)
        
        # 3. 공식 문서 검색
        doc_analysis = self.search_pyth_documentation()
        
        # 4. 결과 통합
        all_publishers = []
        all_publishers.extend(repo_analysis.get('publishers', []))
        all_publishers.extend(doc_analysis.get('documentation_publishers', []))
        
        # 중복 제거
        unique_publishers = []
        seen_values = set()
        
        for pub in all_publishers:
            value = pub.get('value', '')
            if value and value not in seen_values:
                seen_values.add(value)
                unique_publishers.append(pub)
        
        return {
            'success': True,
            'repos_analyzed': len(repo_analysis.get('analyzed_repos', [])),
            'total_repo_publishers': repo_analysis.get('total_publishers', 0),
            'total_doc_publishers': doc_analysis.get('total_documentation_publishers', 0),
            'unique_publishers': unique_publishers,
            'repo_analysis': repo_analysis,
            'doc_analysis': doc_analysis
        }
    
    def save_results(self, results: Dict, filename: str = "pyth_github_publishers.json"):
        """결과를 파일로 저장합니다."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 JSON 결과가 {filename}에 저장되었습니다.")
        
        # CSV로도 저장
        if results.get('success') and results.get('unique_publishers'):
            csv_filename = filename.replace('.json', '.csv')
            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Index', 'Type', 'Value', 'Pattern/Context'])
                
                for i, pub in enumerate(results['unique_publishers'], 1):
                    writer.writerow([
                        i,
                        pub.get('type', 'Unknown'),
                        pub.get('value', ''),
                        pub.get('pattern', pub.get('context', ''))[:100]
                    ])
            
            print(f"📊 CSV 결과가 {csv_filename}에 저장되었습니다.")
    
    def print_summary(self, results: Dict):
        """결과 요약을 출력합니다."""
        if not results.get('success'):
            print(f"❌ 실패: {results.get('error', '알 수 없는 오류')}")
            return
        
        print("\n" + "="*60)
        print("📊 GitHub Pyth 퍼블리셔 검색 결과")
        print("="*60)
        
        repos_analyzed = results.get('repos_analyzed', 0)
        total_repo_publishers = results.get('total_repo_publishers', 0)
        total_doc_publishers = results.get('total_doc_publishers', 0)
        unique_publishers = results.get('unique_publishers', [])
        
        print(f"📈 기본 통계:")
        print(f"  • 분석된 저장소 수: {repos_analyzed}개")
        print(f"  • 저장소에서 발견된 퍼블리셔: {total_repo_publishers}개")
        print(f"  • 문서에서 발견된 퍼블리셔: {total_doc_publishers}개")
        print(f"  • 고유 퍼블리셔 수: {len(unique_publishers)}개")
        
        if unique_publishers:
            print(f"\n🏆 퍼블리셔 리스트 (상위 15개):")
            for i, pub in enumerate(unique_publishers[:15], 1):
                pub_type = pub.get('type', 'Unknown')
                value = pub.get('value', 'Unknown')
                print(f"  {i:2d}. [{pub_type}] {value}")
            
            if len(unique_publishers) > 15:
                print(f"  ... 그리고 {len(unique_publishers) - 15}개 더")
        
        # 저장소별 분석 결과
        repo_analysis = results.get('repo_analysis', {})
        analyzed_repos = repo_analysis.get('analyzed_repos', [])
        
        if analyzed_repos:
            print(f"\n📊 저장소별 분석 결과:")
            for repo in analyzed_repos[:5]:  # 상위 5개만
                repo_name = repo.get('repo', 'Unknown')
                stars = repo.get('stars', 0)
                pub_count = len(repo.get('publishers', []))
                print(f"  • {repo_name} (⭐{stars}): {pub_count}개 퍼블리셔")

def main():
    print("🚀 GitHub를 통한 Pyth 퍼블리셔 정보 검색")
    print("=" * 70)
    
    github_publishers = PythGitHubPublishers()
    
    # BTC 피드 퍼블리셔 가져오기
    results = github_publishers.get_btc_publishers()
    
    if results.get('success'):
        # 결과 출력
        github_publishers.print_summary(results)
        
        # 결과 저장
        github_publishers.save_results(results)
        
        print(f"\n✅ 분석 완료!")
        unique_count = len(results.get('unique_publishers', []))
        print(f"📊 결과: GitHub 검색을 통해 {unique_count}개의 퍼블리셔 정보를 발견했습니다.")
    else:
        print(f"❌ 실패: {results.get('error', '알 수 없는 오류')}")

if __name__ == "__main__":
    main() 