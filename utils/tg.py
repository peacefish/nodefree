import urllib3
import requests
import re
from datetime import datetime
def main():
 
    file1 = open("./sub/clash_nodeshare.yaml", "w+",encoding='utf-8')
    # 获取当前日期
    current_date = datetime.now()
# 格式化日期为 'YYYY/MM/DDYYYYMMDD' 格式
    formatted_date = current_date.strftime('%Y/%-m/%d%Y%m%d')
    file1.write(download_content(f'https://tglaoshiji.github.io/nodeshare/{formatted_date}.yaml'))
    file1.close()
    print("ok url")


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
