"""
探索 NET 網站結構 - 找到配件和鞋類的正確 URL
"""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}

def explore_net_structure():
    """探索 NET 官網結構"""
    try:
        url = "https://www.net-fashion.net"
        print(f"正在訪問: {url}\n")
        
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有導航連結
        print("=" * 80)
        print("所有導航連結:")
        print("=" * 80)
        
        nav_links = soup.find_all('a', href=True)
        
        keywords = ['accessories', 'shoes', '配件', '鞋', 'accessory', 'shoe', '包', 'bag']
        
        found_links = {}
        for link in nav_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # 檢查是否包含關鍵字
            for keyword in keywords:
                if keyword.lower() in href.lower() or keyword in text.lower():
                    if keyword not in found_links:
                        found_links[keyword] = []
                    
                    full_url = href if href.startswith('http') else f"https://www.net-fashion.net{href}"
                    found_links[keyword].append({
                        'text': text,
                        'url': full_url
                    })
        
        # 顯示結果
        for keyword, links in found_links.items():
            print(f"\n關鍵字: {keyword}")
            for link in links[:5]:  # 只顯示前5個
                print(f"  - {link['text']}: {link['url']}")
        
        # 如果找到配件或鞋類頁面，進一步探索
        print("\n" + "=" * 80)
        print("建議的 URL:")
        print("=" * 80)
        
        if 'accessories' in found_links and found_links['accessories']:
            print(f"\n配件頁面: {found_links['accessories'][0]['url']}")
        
        if 'shoes' in found_links and found_links['shoes']:
            print(f"鞋類頁面: {found_links['shoes'][0]['url']}")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")

if __name__ == '__main__':
    explore_net_structure()
