#!/usr/bin/env python3
"""
Debug script to analyze website structure
"""
import requests
from bs4 import BeautifulSoup
import json

def debug_website():
    """Debug the website structure"""
    url = "https://crypto-fundraising.info/"
    
    print(f"🔍 Analyzing {url}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"✅ Page loaded successfully")
        print(f"📄 Content length: {len(response.content)} bytes")
        
        # Find all tables
        tables = soup.find_all('table')
        print(f"\n📊 Found {len(tables)} tables")
        
        for i, table in enumerate(tables):
            print(f"\n--- Table {i+1} ---")
            rows = table.find_all('tr')
            print(f"Rows: {len(rows)}")
            
            if rows:
                # Show first few rows
                for j, row in enumerate(rows[:3]):
                    cells = row.find_all(['td', 'th'])
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    print(f"Row {j+1}: {cell_texts}")
        
        # Look for specific content
        print(f"\n🔍 Looking for specific content...")
        
        # Check for fundraising-related text
        fundraising_keywords = ['fundraising', 'round', 'investor', 'amount', 'raised']
        page_text = soup.get_text().lower()
        
        for keyword in fundraising_keywords:
            if keyword in page_text:
                print(f"✅ Found keyword: {keyword}")
        
        # Look for divs with project-like content
        project_divs = soup.find_all('div', class_=lambda x: x and any(word in x.lower() for word in ['project', 'fund', 'round']))
        print(f"\n📦 Found {len(project_divs)} potential project divs")
        
        # Look for any elements with project names
        potential_names = soup.find_all(text=lambda text: text and len(text.strip()) > 3 and len(text.strip()) < 50)
        print(f"\n📝 Found {len(potential_names)} potential text elements")
        
        # Save HTML for manual inspection
        with open('website_debug.html', 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        
        print(f"\n💾 HTML saved to website_debug.html for manual inspection")
        
        # Look for JavaScript-rendered content
        scripts = soup.find_all('script')
        print(f"\n📜 Found {len(scripts)} script tags")
        
        for script in scripts:
            if script.string and 'fundraising' in script.string.lower():
                print("✅ Found fundraising-related JavaScript")
                break
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_website() 