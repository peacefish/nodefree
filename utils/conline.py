import requests
from bs4 import BeautifulSoup
import urllib3
import re
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import logging
import cloudscraper
import yaml
scraper = cloudscraper.create_scraper(delay=5, browser={
    'browser': 'chrome',
    'platform': 'linux',
    'mobile': False,
})

# Enable debug-level logging
logging.basicConfig(level=logging.DEBUG)
# 禁用不安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
      # 其他请求头可以根据需要添加
  }                                           
def extract_links(url):
    # 发送HTTP请求
    response = scraper.get(url,proxies={'http': 'http://39.102.209.163:2128'})
    #print(response.text)
    # 确保请求成功
    if response.status_code == 200:
        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')
        # 找到所有的<a>标签
        links = soup.find_all(class_="ceo-cover-container")
        # 提取href属性
        extracted_links = [link.get('href') for link in links if link.get('href') is not None]
        #print(extracted_links)
        return extracted_links
    else:
        return "Failed to retrieve the webpage"
def extract_links_url(url):
    # 发送HTTP请求
    response = scraper.get(url,proxies={'http': 'http://39.102.209.163:2128'})
    # 确保请求成功
    if response.status_code == 200:
        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')
        # 找到所有的<a>标签
        links = soup.find_all('a', href=lambda href: href and href.endswith('.yaml'))
        # 提取href属性
        extracted_links = [link.get('href') for link in links if link.get('href') is not None]
        return extracted_links
    else:
        return "Failed to retrieve the webpage"


def main():
    file1 = open("./sub/clash_online.yaml", "w+",encoding='utf-8')
    # 获取当前日期
    current_date = datetime.now()

    url = "https://www.85la.com/internet-access/free-network-nodes"
    links = extract_links(url)
    a=extract_links_url(links[0])
    response = scraper.get(a[0],proxies={'http': 'http://39.102.209.163:2128'})
    #print(response.text)
    response.encoding = 'utf-8'
    dct = yaml.safe_load(response.text.replace('👉','').replace('www.85la.com','').replace('()','').replace('( https://www.fuye.fun/免费节点分享)',''))
    a=dct['proxies']
    yaml_content = yaml.dump({"proxies":a}, default_flow_style=False)
    file1.write(yaml_content)
    file1.close()
    print("ok url")

def download_content(url):
    """
    第一个函数，用来下载网页，返回网页内容
    参数 url 代表所要下载的网页网址。
    整体代码和之前类似
    """
    response = requests.get(url)
    response.encoding = 'utf-8' 
    #print(response)
    text=response.text.replace('👉','').replace('www.85la.com','').replace('()','').replace('( https://www.fuye.fun/免费节点分享)','')
    return text

if __name__ == '__main__':
    main()
