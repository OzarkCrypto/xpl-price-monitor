#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
from typing import Dict, List, Any, Optional

class PythGitHubApproach:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def check_pyth_github_repos(self):
        """Pyth Network GitHub 저장소 확인"""
        print("🔍 Pyth Network GitHub 저장소 확인...")
        
        # Pyth Network 관련 GitHub 저장소들
        github_repos = [
            "https://api.github.com/repos/pyth-network/pyth-client-js",
            "https://api.github.com/repos/pyth-network/pyth-client-py",
            "https://api.github.com/repos/pyth-network/pyth-client-rs",
            "https://api.github.com/repos/pyth-network/pyth-client-go",
            "https://api.github.com/repos/pyth-network/pyth-client-java",
            "https://api.github.com/repos/pyth-network/pyth-sdk-js",
            "https://api.github.com/repos/pyth-network/pyth-sdk-py",
            "https://api.github.com/repos/pyth-network/pyth-sdk-rs",
            "https://api.github.com/repos/pyth-network/pyth-sdk-go",
            "https://api.github.com/repos/pyth-network/pyth-sdk-java"
        ]
        
        for repo_url in github_repos:
            try:
                print(f"  🔗 {repo_url} 확인...")
                response = self.session.get(repo_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"    ✅ 저장소 존재: {data.get('name', 'Unknown')}")
                    print(f"    📊 설명: {data.get('description', 'No description')}")
                    print(f"    🌟 스타: {data.get('stargazers_count', 0)}")
                    print(f"    🔗 URL: {data.get('html_url', 'No URL')}")
                else:
                    print(f"    ❌ 저장소 없음! 상태코드: {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ 오류: {str(e)[:50]}")
            
            time.sleep(0.5)
    
    def check_pyth_github_files(self):
        """Pyth Network GitHub 파일들 확인"""
        print("\n🔍 Pyth Network GitHub 파일들 확인...")
        
        # 주요 파일들 확인
        github_files = [
            "https://raw.githubusercontent.com/pyth-network/pyth-client-js/main/README.md",
            "https://raw.githubusercontent.com/pyth-network/pyth-client-py/main/README.md",
            "https://raw.githubusercontent.com/pyth-network/pyth-sdk-js/main/README.md",
            "https://raw.githubusercontent.com/pyth-network/pyth-sdk-py/main/README.md",
            "https://raw.githubusercontent.com/pyth-network/pyth-client-js/main/src/index.ts",
            "https://raw.githubusercontent.com/pyth-network/pyth-client-py/main/pyth/client.py",
            "https://raw.githubusercontent.com/pyth-network/pyth-sdk-js/main/src/index.ts",
            "https://raw.githubusercontent.com/pyth-network/pyth-sdk-py/main/pyth/sdk.py"
        ]
        
        for file_url in github_files:
            try:
                print(f"  🔗 {file_url} 확인...")
                response = self.session.get(file_url, timeout=10)
                
                if response.status_code == 200:
                    content = response.text
                    print(f"    ✅ 파일 접근 가능! (길이: {len(content)} 문자)")
                    
                    # 퍼블리셔 관련 내용 검색
                    publisher_keywords = ['publisher', 'authority', 'validator', 'amber', 'alphanonce']
                    found_keywords = []
                    
                    for keyword in publisher_keywords:
                        if keyword.lower() in content.lower():
                            found_keywords.append(keyword)
                    
                    if found_keywords:
                        print(f"    🔍 발견된 키워드: {found_keywords}")
                        
                        # 관련 라인들 추출
                        lines = content.split('\n')
                        relevant_lines = []
                        for i, line in enumerate(lines):
                            if any(keyword.lower() in line.lower() for keyword in found_keywords):
                                relevant_lines.append(f"      라인 {i+1}: {line.strip()[:100]}")
                                if len(relevant_lines) >= 3:  # 최대 3개 라인만
                                    break
                        
                        for line in relevant_lines:
                            print(line)
                    else:
                        print(f"    ❌ 퍼블리셔 관련 키워드 없음")
                else:
                    print(f"    ❌ 파일 접근 불가! 상태코드: {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ 오류: {str(e)[:50]}")
            
            time.sleep(0.5)
    
    def check_pyth_network_website(self):
        """Pyth Network 웹사이트 확인"""
        print("\n🔍 Pyth Network 웹사이트 확인...")
        
        # Pyth Network 웹사이트 페이지들
        website_pages = [
            "https://pyth.network/",
            "https://pyth.network/developers",
            "https://pyth.network/developers/price-feeds",
            "https://pyth.network/developers/api",
            "https://pyth.network/developers/sdk",
            "https://pyth.network/developers/guides",
            "https://pyth.network/developers/guides/price-feeds",
            "https://pyth.network/developers/guides/api"
        ]
        
        for page_url in website_pages:
            try:
                print(f"  🔗 {page_url} 확인...")
                response = self.session.get(page_url, timeout=10)
                
                if response.status_code == 200:
                    content = response.text
                    print(f"    ✅ 페이지 접근 가능! (길이: {len(content)} 문자)")
                    
                    # 퍼블리셔 관련 내용 검색
                    publisher_keywords = ['publisher', 'authority', 'validator', 'amber', 'alphanonce', 'pyth']
                    found_keywords = []
                    
                    for keyword in publisher_keywords:
                        if keyword.lower() in content.lower():
                            found_keywords.append(keyword)
                    
                    if found_keywords:
                        print(f"    🔍 발견된 키워드: {found_keywords}")
                        
                        # 관련 라인들 추출
                        lines = content.split('\n')
                        relevant_lines = []
                        for i, line in enumerate(lines):
                            if any(keyword.lower() in line.lower() for keyword in found_keywords):
                                relevant_lines.append(f"      라인 {i+1}: {line.strip()[:100]}")
                                if len(relevant_lines) >= 3:  # 최대 3개 라인만
                                    break
                        
                        for line in relevant_lines:
                            print(line)
                    else:
                        print(f"    ❌ 퍼블리셔 관련 키워드 없음")
                else:
                    print(f"    ❌ 페이지 접근 불가! 상태코드: {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ 오류: {str(e)[:50]}")
            
            time.sleep(0.5)
    
    def check_pyth_discord_github(self):
        """Pyth Discord GitHub 봇 확인"""
        print("\n🔍 Pyth Discord GitHub 봇 확인...")
        
        # Pyth Discord 봇 관련 저장소들
        discord_repos = [
            "https://api.github.com/repos/pyth-network/pyth-discord-bot",
            "https://api.github.com/repos/pyth-network/pyth-bot",
            "https://api.github.com/repos/pyth-network/discord-bot"
        ]
        
        for repo_url in discord_repos:
            try:
                print(f"  🔗 {repo_url} 확인...")
                response = self.session.get(repo_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"    ✅ 저장소 존재: {data.get('name', 'Unknown')}")
                    print(f"    📊 설명: {data.get('description', 'No description')}")
                    
                    # 저장소 내용 확인
                    contents_url = f"{repo_url}/contents"
                    contents_response = self.session.get(contents_url, timeout=10)
                    
                    if contents_response.status_code == 200:
                        contents = contents_response.json()
                        print(f"    📁 파일들:")
                        for item in contents[:5]:  # 최대 5개 파일만
                            print(f"      • {item.get('name', 'Unknown')} ({item.get('type', 'Unknown')})")
                    else:
                        print(f"    ❌ 파일 목록 접근 불가")
                        
                else:
                    print(f"    ❌ 저장소 없음! 상태코드: {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ 오류: {str(e)[:50]}")
            
            time.sleep(0.5)
    
    def check_pyth_community_sources(self):
        """Pyth 커뮤니티 소스 확인"""
        print("\n🔍 Pyth 커뮤니티 소스 확인...")
        
        # 커뮤니티 소스들
        community_sources = [
            "https://forum.pyth.network/",
            "https://discord.gg/pyth",
            "https://t.me/pyth_network",
            "https://twitter.com/PythNetwork",
            "https://medium.com/pyth-network"
        ]
        
        for source_url in community_sources:
            try:
                print(f"  🔗 {source_url} 확인...")
                response = self.session.get(source_url, timeout=10)
                
                if response.status_code == 200:
                    content = response.text
                    print(f"    ✅ 소스 접근 가능! (길이: {len(content)} 문자)")
                    
                    # 퍼블리셔 관련 내용 검색
                    publisher_keywords = ['publisher', 'authority', 'validator', 'amber', 'alphanonce']
                    found_keywords = []
                    
                    for keyword in publisher_keywords:
                        if keyword.lower() in content.lower():
                            found_keywords.append(keyword)
                    
                    if found_keywords:
                        print(f"    🔍 발견된 키워드: {found_keywords}")
                    else:
                        print(f"    ❌ 퍼블리셔 관련 키워드 없음")
                else:
                    print(f"    ❌ 소스 접근 불가! 상태코드: {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ 오류: {str(e)[:50]}")
            
            time.sleep(0.5)
    
    def run_comprehensive_analysis(self):
        """종합적인 분석 실행"""
        print("🚀 Pyth Network GitHub 및 커뮤니티 소스 기반 퍼블리셔 정보 분석")
        print("=" * 80)
        
        # 1. GitHub 저장소 확인
        self.check_pyth_github_repos()
        
        # 2. GitHub 파일들 확인
        self.check_pyth_github_files()
        
        # 3. Pyth Network 웹사이트 확인
        self.check_pyth_network_website()
        
        # 4. Pyth Discord GitHub 봇 확인
        self.check_pyth_discord_github()
        
        # 5. Pyth 커뮤니티 소스 확인
        self.check_pyth_community_sources()
        
        print("\n" + "=" * 80)
        print("📊 GitHub 및 커뮤니티 소스 기반 분석 완료!")

if __name__ == "__main__":
    analyzer = PythGitHubApproach()
    analyzer.run_comprehensive_analysis() 