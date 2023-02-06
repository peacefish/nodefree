import urllib3
import requests
import re
from bs4 import BeautifulSoup
def main():
    url = "https://agit.ai/12/a/commits/branch/master"
    result = download_content(url)
    doc = BeautifulSoup(result,'html.parser')
    newurl = parse(doc)
    print(newurl)
    file = open("./sub/newclash.yaml", "w+",encoding='utf-8')
    file.write(download_content(newurl))
    file.close()
    file1 = open("./sub/clash_short.yaml", "w+",encoding='utf-8')
    file1.write(download_content('https://agit.ai/ansakg/clash_233/raw/branch/master/speed_short.yaml'))
    file1.close()

def parse(doc):
    links = doc.find_all("span", class_="commit-summary")
    for link in links:
      str=link.get("title")
      _url=re.findall(r"(?:.*) '(.+?)'",str)
      matchObj = re.match( r'.*cl.*', _url[0], re.M|re.I)
      if matchObj:
        return "https://agit.ai/12/a/raw/branch/master/"+_url[0].replace('v2','cl')

def download_content(url):
    """
    第一个函数，用来下载网页，返回网页内容
    参数 url 代表所要下载的网页网址。
    整体代码和之前类似
    """
    response = requests.get(url).text.replace('https://awkj.cf/ky 注册体验流媒体机场','').replace('youtube阿伟科技','|A').replace('()','')
    #print(response)
    return response

if __name__ == '__main__':
    main()
