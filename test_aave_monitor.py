#!/usr/bin/env python3
"""
Aave 거버넌스 모니터링 봇 테스트 스크립트
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def test_telegram_bot():
    """텔레그램 봇 테스트"""
    print("🤖 텔레그램 봇 테스트")
    print("=" * 40)
    
    token = "8253278813:AAH5I5cMlu6N7srGDNl8LkPnW2PUJRPPTTI"
    chat_id = "1339285013"
    
    try:
        # 봇 정보 가져오기
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        bot_info = response.json()
        if bot_info.get('ok'):
            bot = bot_info['result']
            print(f"✅ 봇 이름: {bot['first_name']}")
            print(f"✅ 봇 사용자명: @{bot['username']}")
            print(f"✅ 봇 ID: {bot['id']}")
        else:
            print("❌ 봇 정보를 가져올 수 없습니다.")
            return False
        
        # 테스트 메시지 전송
        test_url = f"https://api.telegram.org/bot{token}/sendMessage"
        test_data = {
            'chat_id': chat_id,
            'text': f"🧪 Aave 거버넌스 모니터링 봇 테스트\n\n⏰ 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n✅ 봇이 정상적으로 작동합니다!",
            'parse_mode': 'HTML'
        }
        
        response = requests.post(test_url, data=test_data, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get('ok'):
            print("✅ 테스트 메시지 전송 성공!")
            return True
        else:
            print(f"❌ 테스트 메시지 전송 실패: {result}")
            return False
            
    except Exception as e:
        print(f"❌ 텔레그램 봇 테스트 오류: {e}")
        return False

def test_aave_page():
    """Aave 페이지 접근 테스트"""
    print("\n🌐 Aave 페이지 접근 테스트")
    print("=" * 40)
    
    url = "https://governance.aave.com/t/arfc-onboard-usde-july-expiry-pt-tokens-on-aave-v3-core-instance/22041"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"✅ 페이지 접근 성공: {response.status_code}")
        print(f"✅ 페이지 크기: {len(response.text)} bytes")
        
        # HTML 파싱 테스트
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 제목 확인
        title = soup.find('title')
        if title:
            print(f"✅ 페이지 제목: {title.get_text(strip=True)}")
        
        # 댓글 요소 확인
        posts = soup.find_all('div', class_='topic-body')
        print(f"✅ 댓글 수: {len(posts)}")
        
        if posts:
            # 첫 번째 댓글 정보
            first_post = posts[0]
            author_element = first_post.find('span', class_='creator')
            if author_element:
                author_link = author_element.find('a')
                author = author_link.get_text(strip=True) if author_link else "Unknown"
            else:
                author = "Unknown"
            
            content = first_post.find('div', class_='post')
            
            if author:
                print(f"✅ 첫 번째 댓글 작성자: {author}")
            if content:
                content_text = content.get_text(strip=True)[:100]
                print(f"✅ 첫 번째 댓글 내용: {content_text}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Aave 페이지 테스트 오류: {e}")
        return False

def test_parsing():
    """파싱 기능 테스트"""
    print("\n🔍 파싱 기능 테스트")
    print("=" * 40)
    
    url = "https://governance.aave.com/t/arfc-onboard-usde-july-expiry-pt-tokens-on-aave-v3-core-instance/22041"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 댓글 파싱 테스트
        comments = []
        comment_elements = soup.find_all('div', class_='topic-body')
        
        for element in comment_elements[:3]:  # 처음 3개만 테스트
            try:
                comment_id = element.get('id', '')
                if comment_id.startswith('post_'):
                    comment_id = comment_id.replace('post_', '')
                
                author_element = element.find('span', class_='creator')
                if author_element:
                    author_link = author_element.find('a')
                    author = author_link.get_text(strip=True) if author_link else "Unknown"
                else:
                    author = "Unknown"
                
                content_element = element.find('div', class_='post')
                content = content_element.get_text(strip=True) if content_element else ""
                
                if comment_id and content:
                    comments.append({
                        'id': comment_id,
                        'author': author,
                        'content': content[:100] + "..." if len(content) > 100 else content
                    })
                    
            except Exception as e:
                print(f"⚠️  댓글 파싱 경고: {e}")
                continue
        
        print(f"✅ 파싱된 댓글 수: {len(comments)}")
        
        for i, comment in enumerate(comments):
            print(f"  {i+1}. ID: {comment['id']}, 작성자: {comment['author']}")
            print(f"     내용: {comment['content']}")
        
        return len(comments) > 0
        
    except Exception as e:
        print(f"❌ 파싱 테스트 오류: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🧪 Aave 거버넌스 모니터링 봇 테스트")
    print("=" * 50)
    
    tests = [
        ("텔레그램 봇", test_telegram_bot),
        ("Aave 페이지 접근", test_aave_page),
        ("파싱 기능", test_parsing)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 오류: {e}")
            results.append((test_name, False))
    
    print("\n📊 테스트 결과 요약")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{test_name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    print(f"\n📈 전체 결과: {success_count}/{total_count} 성공")
    
    if success_count == total_count:
        print("🎉 모든 테스트가 성공했습니다!")
        print("✅ 모니터링 봇을 실행할 수 있습니다.")
    else:
        print("⚠️  일부 테스트가 실패했습니다.")
        print("🔧 문제를 해결한 후 다시 테스트해주세요.")

if __name__ == "__main__":
    main()
