import requests
import re
import yaml
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
}

def fetch_html(url):
    """Helper function to fetch and parse HTML content."""
    try:
        response = requests.get(url, headers=HEADERS, verify=False)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL '{url}': {e}")
        return None

def get_index_url(base_url, tag='h2', cls=''):
    soup = fetch_html(base_url)
    if not soup:
        return f"https://www.freeclashnode.com/free-node/{datetime.now().strftime('%Y-%m-%d')}-free-subscribe-node.htm"
    
    header_tags = soup.find_all(tag, class_=cls)
    for header_tag in header_tags:
        a_tag = header_tag.find('a')
        if a_tag:
            return a_tag['href']
    return f"https://www.freeclashnode.com/free-node/{datetime.now().strftime('%Y-%m-%d')}-free-subscribe-node.htm"

def extract_links(url):
    """Extract all .yaml URLs from the given page."""
    soup = fetch_html(url)
    if soup:
        return re.findall(r'https?://[^\s<]+\.yaml', soup.text, re.IGNORECASE)
    return []

def extract_yaml_data(url):
    """Fetch YAML data from the URL and parse the proxies."""
    try:
        response = requests.get(url, headers=HEADERS, verify=False)
        response.encoding = 'utf-8'
        yaml_content = response.text.replace('👉', '').replace('https://www.fuye.fun免费节点分享', '')
        data = yaml.safe_load(yaml_content)
        return data.get('proxies', [])
    except (requests.exceptions.RequestException, yaml.YAMLError) as e:
        print(f"Error fetching or parsing YAML from '{url}': {e}")
        return []

def process_urls(base_url, tag='h2', cls=''):
    """Process a set of URLs to fetch and parse YAML links and proxies."""
    index_url = get_index_url(base_url, tag, cls)
    yaml_links = extract_links(index_url)
    proxies = []
    for link in yaml_links:
        proxies.extend(extract_yaml_data(link))
    return proxies

def main():
    sources = [
        ("https://www.cfmem.com/", "h2", "entry-title"),
        ("https://oneclash.cc/freenode", "div", "col-3"),
        ("https://wanzhuanmi.com/freenode", "h2", ""),
        ("https://www.mibei77.com/", "h2", "entry-title"),
    ]
    
    all_proxies = []
    for url, tag, cls in sources:
        all_proxies.extend(process_urls(url, tag, cls))
    
    # Add proxies from a static URL as well
    all_proxies.extend(extract_yaml_data('https://raw.githubusercontent.com/aiboboxx/clashfree/refs/heads/main/clash.yml'))

    # Save consolidated YAML file
    with open("./sub/proxy_cf.yaml", "w+", encoding='utf-8') as file:
        yaml_content = yaml.dump({"proxies": all_proxies}, default_flow_style=False)
        file.write(yaml_content)
        print("YAML content successfully saved to proxy_cf.yaml")

if __name__ == '__main__':
    main()
