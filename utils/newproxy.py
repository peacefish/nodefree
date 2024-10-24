import requests
import re
import yaml
from datetime import datetime
def extract_links_url(url):
  # 设置请求头
  headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
      # 其他请求头可以根据需要添加
  }

  # 发起 GET 请求
  ymal_urls = []
  try:
      response = requests.get(url, headers=headers, verify=False)  # 禁用 SSL 验证
      print(f"状态码: {response.status_code}")

      if response.status_code == 200:
        ymal_urls = re.findall(r'https?://[^\s<]+\.yaml', response.text,re.IGNORECASE)
      print(ymal_urls)  # 打印响应内容
  except requests.exceptions.RequestException as e:
      print(f"请求出现错误: {e}")
  return ymal_urls
def extract_yaml_url(url):
  # 设置请求头
  headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
      # 其他请求头可以根据需要添加
  }
  # 发起 GET 请求
  try:
      response = requests.get(url, headers=headers, verify=False)  # 禁用 SSL 验证
      response.encoding = 'utf-8'
      #print(f"状态码: {response.status_code}")
      dct = yaml.safe_load(response.text)
      #print(dct['proxies']) 
      #print(response.text)  # 打印响应内容
  except requests.exceptions.RequestException as e:
      print(f"请求出现错误: {e}")
  return dct['proxies']
def main():
  current_date = datetime.now()
  formatted_date = current_date.strftime('%Y-%m-%d')
  url = f"https://www.freeclashnode.com/free-node/{formatted_date}-free-subscribe-node.htm"
  file1 = open("./proxy.yaml", "w+",encoding='utf-8')
  links = extract_links_url(url)
  print(len(links))
  a=[]
  for link in links:
    s=extract_yaml_url(link)
    a=a+s
  yaml_content = yaml.dump({"proxies":a}, default_flow_style=False)
  print(yaml_content)
  file1.write(yaml_content)
  file1.close()
if __name__ == '__main__':
    main()
