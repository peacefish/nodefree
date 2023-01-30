#!/usr/bin/env python3

import os, re, subprocess
import argparse, configparser
import base64, yaml
import socket
import geoip2.database


def convert(subscription,target,other_config={}):
    """Wrapper for subconverter
    subscription: subscription url or content string or local file path, add url support.
    target: target subconvert configuration
    other_config:
        deduplicate: whether to deduplicate
        keep_nodes: amounts of nodes to keep when they are deduplicated
        include: include string in remark
        exclude: exclude string in remark
        config: output subcription config
    """

    default_config = {
        'target': target,
        'deduplicate':False,'keep_nodes':1,
        'rename':'','include':'','exclude':'','config':''
    }
    default_config.update(other_config)
    config = default_config
    
    work_dir = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    if subscription[:8] == 'https://':
        clash_provider = subconverterhandler(subscription)
    else:
        try:
            with open(subscription, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'proxies:' not in content and '://' in content:
                    subscription = content
                    raise ValueError
                else:
                    clash_provider = subconverterhandler(subscription)
        except Exception:
            try:
                if 'proxies:' not in subscription:
                    if '://' in subscription:
                        subscription = base64_encode(subscription)
                        with open('./subscription', 'w', encoding='utf-8') as f:
                            f.write(subscription)
                        clash_provider = subconverterhandler('./subscription')
                        os.remove('./subscription')
                else:
                    with open('./subscription', 'w', encoding='utf-8') as f:
                        f.write(subscription)
                    clash_provider = subconverterhandler('./subscription')
                    os.remove('./subscription')
            except Exception:
                print('No nodes were found in url.')
                os.chdir(work_dir)
                return ''

    if config['deduplicate']:
        clash_provider = deduplicate(clash_provider,config['keep_nodes'])

    with open('./temp', 'w', encoding= 'utf-8') as temp_file:
        temp_file.write(clash_provider)
    output = subconverterhandler('./temp',config)
    os.chdir(work_dir)
    return output

def subconverterhandler(subscription,input_config={'target':'transfer','rename':'','include':'','exclude':'','config':''}):
    """Wrapper for subconverter(by configuration file: generate.ini)
    Target handling config parameters(parameters from https://github.com/tindy2013/subconverter/blob/master/README-cn.md#%E8%BF%9B%E9%98%B6%E9%93%BE%E6%8E%A5):
        target: target subconvert configuration
        url: input subcription url or file path
        include: include string in remark
        exclude: exclude string in remark
        config: output subcription config
    Function input_config variant should be a dictionary which has keys and values of above parameters, output content will be string of target configuration.
    By default, functon will output clash_provider without any format methods.
    """
    work_dir = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    configparse = configparser.ConfigParser()
    configparse.read('./generate.ini',encoding='utf-8')
    
    url = subscription
    target = input_config['target']
    rename = input_config['rename']
    include = input_config['include']
    exclude = input_config['exclude']
    config = input_config['config']
    configparse.set(target,'url',url)
    configparse.set(target,'rename',rename)
    configparse.set(target,'include',include)
    configparse.set(target,'exclude',exclude)
    configparse.set(target,'config',config)

    origin_configparse = configparser.ConfigParser()
    origin_configparse.read('./generate.ini',encoding='utf-8')
    origin_config = {'url':origin_configparse[target]['url'],'rename':origin_configparse[target]['rename'],'include':origin_configparse[target]['include'],'exclude':origin_configparse[target]['exclude'],'config':origin_configparse[target]['config']}

    with open('./generate.ini', 'w', encoding='utf-8') as ini:
        configparse.write(ini,space_around_delimiters=False)

    if os.name == 'posix':
        args = ['./subconverter-linux-amd64', '-g', '--artifact', target]
    elif os.name == 'nt':
        args = ['.\subconverter-windows-amd64.exe', '-g', '--artifact', target]
    subconverter = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True,encoding='utf-8',bufsize=1)
    logs = subconverter.stdout.readlines()
    subconverter.wait()
    # Print log
    pre_run = False
    for line in logs:
        if 'Fetching node data from url' in line and '\'./temp\'' not in line:
            pre_run = True
            print(line[:-1])
    if pre_run == False:
        if '[INFO]' not in (logs[-3]):
            print(logs[-2])
        else:
            print(logs[-3])

    if subconverter.returncode != 0:
        try:
            os.remove('./temp')
            output = ''
        except Exception:
            output = ''
    else:
        try:
            with open(f'./temp', 'r', encoding= 'utf-8', errors='ignore') as temp_file:
                output = ''
                while True:
                    content = temp_file.read(100)
                    if not content:
                        break
                    output += content
            if target == 'url':
                output = base64_decode(output)
            os.remove('./temp')
        except Exception:
            output = ''

    origin_configparse.set(target,'url',origin_config['url'])
    origin_configparse.set(target,'rename',origin_config['rename'])
    origin_configparse.set(target,'include',origin_config['include'])
    origin_configparse.set(target,'exclude',origin_config['exclude'])
    origin_configparse.set(target,'config',origin_config['config'])
    with open('./generate.ini', 'w', encoding='utf-8') as ini:
        origin_configparse.write(ini,space_around_delimiters=False)

    os.chdir(work_dir)
    return output
def deduplicate(clash_provider,keep_nodes=1): # Proxies deduplicate. If proxies with the same servers are greater than keep_nodes, they will not be added.
    lines = re.split(r'\n+', clash_provider)[1:]
    print('Starting deduplicate...')
    print(f'Init amount: {len(lines)}')
    try:
        proxies = yaml.safe_load(clash_provider)['proxies'] # load all proxies from clash provider
    except Exception:
        il_chars = ['|', '?', '[', ']', '@', '!', '%', ':']

        line_fixed = ['proxies:']
        for line in lines:
            try_load = 'proxies:\n' + line
            try:
                yaml.safe_load(try_load)
                line_fixed.append(line)
            except Exception:
                line = line.replace('\'', '').replace('"', '')
                value_list = re.split(r': |, ', line)
                if len(value_list) > 6:
                    value_list_fix = []
                    for value in value_list:
                        for char in il_chars:
                            value_il = False
                            if char in value:
                                value_il = True
                                break
                        if value_il == True and ('{' not in value and '}' not in value):
                            value = '"' + value + '"'
                            value_list_fix.append(value)
                        elif value_il == True and '}' in value:
                            if '}}}' in value:
                                host_part = value.replace('}}}','')
                                host_value = '"'+host_part+'"}}}'
                                value_list_fix.append(host_value)
                            elif '}}' not in value:
                                host_part = value.replace('}','')
                                host_value = '"'+host_part+'"}'
                                value_list_fix.append(host_value)
                        else:
                            value_list_fix.append(value)
                        line_fix = line
                    for index in range(len(value_list_fix)):
                        line_fix = line_fix.replace(value_list[index], value_list_fix[index])
                else:
                    pass
                try:
                    try_load = 'proxies:\n' + line_fix
                    yaml.safe_load(try_load)
                    line_fixed.append(line_fix)
                except Exception:
                    pass
        fix_provider = '\n'.join(line_fixed)
        
        try:
            proxies = yaml.safe_load(fix_provider)['proxies']
        except Exception:
            print('Deduplicate failed, skip')
            output = clash_provider
            return output
    
    servers = {}
    for proxy in proxies:
        server = proxy['server'] # assign remote server
        if server.replace('.','').isdigit():
            ip = server
        else:
            try:
                ip = socket.gethostbyname(server)
            except Exception:
                ip = server

        if ip in servers:
            servers[ip].append(proxy) # add proxy to its remote server list
        elif server not in servers:
            servers[ip] = [proxy] # init remote server list, add first proxy

    proxies = []
    for server in servers:
        # if len(servers[server]) > 3: # if proxy amount is greater than 4 then just add 4 proxies
        #     add_list = servers[server][:3]
        #     for add in add_list:
        #         proxies.append(add)
        # else:
        #     add_list = servers[server] # if proxy amount is less than 4 then add all proxies
        #     for add in add_list:
        #         proxies.append(add)
        try:
            add_list = servers[server][:keep_nodes]
        except Exception:
            add_list = servers[server]
        for x in add_list:
            proxies.append(x)
    print(f'Dedupicate success, remove {len(lines)-len(proxies)} duplicate proxies')
    print(f'Output amount: {len(proxies)}')

    output = yaml.dump({'proxies': proxies}, default_flow_style=False, sort_keys=False, allow_unicode=True, indent=2)
    return output

def base64_decode(content):
    if '-' in content:
        content = content.replace('-', '+')
    if '_' in content:
        content = content.replace('_', '/')
    #print(len(url_content))
    missing_padding = len(content) % 4
    if missing_padding != 0:
        content += '='*(4 - missing_padding) # 不是4的倍数后加= https://www.cnblogs.com/wswang/p/7717997.html
    try:
        base64_content = base64.b64decode(content.encode('utf-8')).decode('utf-8','ignore') # https://www.codenong.com/42339876/
        base64_content_format = base64_content
        return base64_content_format
    except UnicodeDecodeError:
        base64_content = base64.b64decode(content)
        base64_content_format = base64_content
        return str(base64_content)
def base64_encode(content):
    if content == None:
        content = ''
    base64_content = base64.b64encode(content.encode('utf-8')).decode('ascii')
    return base64_content

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert between various proxy subscription formats using Subconverter.')
    parser.add_argument('--subscription', '-s', help='Your subscription url or local file path.', required=True)
    parser.add_argument('--target', '-t', help='Target convert format, support base64, clash, clash_provider, quanx.', default='clash')
    parser.add_argument('--output', '-o', help='Target path to output, default value is the Subconverter root directionary.', default='./Eternity.yaml')
    parser.add_argument('--deduplicate', '-d', help='Whether to deduplicate proxies, default value is False.', default=False)
    parser.add_argument('--keep', '-k', help='Amounts of nodes to keep when deduplicated.', default=1)
    args = parser.parse_args()

    subscription = args.subscription
    target = args.target
    output_dir = args.output
    if args.deduplicate == 'true' or args.deduplicate == 'True':
        deduplicate_enabled = True
    else:
        deduplicate_enabled = False
    keep_nodes = int(args.keep)

    work_dir = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    generate = configparser.ConfigParser()
    generate.read('./generate.ini',encoding='utf-8')
    config={'deduplicate': deduplicate_enabled,'keep_nodes': keep_nodes,'rename': generate.get(target,'rename'), 'include': generate.get(target,'include'), 'exclude': generate.get(target,'exclude'), 'config': generate.get(target,'config')}

    output = convert(subscription,target,config)

    with open(output_dir, 'w', encoding= 'utf-8') as temp_file:
        temp_file.write(output)
    os.chdir(work_dir)