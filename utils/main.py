#!/usr/bin/env python3

import os, urllib
import configparser

from sub_update import update
from sub_merge import merge
from subconverter import convert, base64_decode

config_file = './utils/config.ini'

def configparse(section):
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')
    if section == 'common':
        return config['common']
    elif section == 'subconverter':
        return config['subconverter']
    elif section == 'speedtest':
        return config['speedtest']

if __name__ == '__main__':

    try:
        print('Downloading Country.mmdb...')
        urllib.request.urlretrieve('https://raw.githubusercontent.com/Loyalsoldier/geoip/release/Country.mmdb', './utils/Country.mmdb')
        print('Success!\n')
    except Exception:
        print('Failed!\n')
        pass

    if configparse('common').getboolean('update_enabled'):
        config = configparse('common')
        update(config)

    if configparse('common').getboolean('merge_enabled'):
        file_dir = configparse('common')
        format_config = configparse('subconverter')
        merge(file_dir, format_config)

    if configparse('common').getboolean('speedtest_enabled'):
        share_file = configparse('common')['share_file']
        share_file_clash = configparse('common')['share_file_clash']
        subscription = configparse('speedtest')['subscription']
        range = configparse('speedtest')['output_range']
        os.system(f'proxychains python3 ./utils/litespeedtest/speedtest.py --subscription \"../../{subscription}\" --range \"200,1100\" --path \"../../temp\"')

        east_asian_proxies = convert('../../temp','base64',{'deduplicate':False,'rename':'','include':'港|HK|Hong Kong|坡|SG|狮城|Singapore|日|JP|东京|大阪|埼玉|Japan|台|TW|新北|彰化|Taiwan|韩|KR|KOR|首尔|Korea','exclude':'','config':''})
        north_america_proxies = convert('../../temp','base64',{'deduplicate':False,'rename':'','include':'美|US|United States|加拿大|CA|Canada|波特兰|达拉斯|俄勒冈|凤凰城|费利蒙|硅谷|拉斯维加斯|洛杉矶|圣何塞|圣克拉拉|西雅图|芝加哥','exclude':'','config':''})
        other_country_proxies = convert('../../temp','base64',{'deduplicate':False,'rename':'','include':'','exclude':'US|HK|SG|JP|TW|KR|美|港|坡|日|台|韩|CA|加','config':''})
        area_proxies = {
            'east_asia': [east_asian_proxies, 45],
            'north_america': [north_america_proxies, 25],
            'other_area':[other_country_proxies, 25]
        }
        share_proxies = []
        for area in area_proxies.keys():
            with open('./temp', 'w', encoding='utf-8') as temp_file:
                temp_file.write(area_proxies[area][0])
            os.system(f'proxychains python3 ./utils/litespeedtest/speedtest.py --subscription \"../../temp\" --range \"{area_proxies[area][1]}\" --path \"../../temp\"')
            with open('./temp', 'r', encoding='utf-8') as temp_file:
                content = temp_file.read()
                share_proxies.append(base64_decode(content))
        with open('./temp', 'w', encoding='utf-8') as temp_file:
            temp_file.write(''.join(share_proxies))
        os.system(f'python3 ./utils/subconverter/subconvert.py --subscription \"../../temp\" --target \"base64\" --output \"../../{share_file}\"')
        os.system(f'python3 ./utils/subconverter/subconvert.py --subscription \"../../temp\" --target \"clash\" --output \"../../{share_file_clash}\"')
        os.remove('./temp')