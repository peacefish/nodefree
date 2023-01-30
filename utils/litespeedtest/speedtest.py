import json, base64, os
import subprocess, argparse

def speedtest(subscription,output_range,other_config={'concurrency': -1, 'timeout': -1}):
    """Wrapper for litespeedtest.
    configurations:
        subscription: Subcription to speedtest, support local file path or url
        output_range: output proxy list range. Set value to '-1' means output all the prorxies, '99' means output 0 to 99 proxies, '99,999' means output 99 to 999 proxies.
        concurrency: The number of proxies tested in one time
        timeout: Time period that cannot connect to the tested proxy
    """
    default_config = {
        'subscription': subscription, 'outputRange': output_range, 
        'concurrency': -1, 'timeout': -1
    }
    default_config.update(other_config)
    config = default_config
    
    work_dir = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    confighandler(config) # Initialize configurations
    if os.name == 'posix':
        args = ['./lite-linux-amd64', '--config', './config.json', '--test', 'Eternity']
    elif os.name == 'nt':
        args = ['.\lite-windows-amd64.exe', '--config', './config.json', '--test', 'Eternity']
    litespeedtest = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True,encoding='utf-8',bufsize=1)

    # Progress bar
    max_node = 1
    current_node = 0
    for line in iter(litespeedtest.stdout.readline, ''):
        try:
            info = json.loads(line[19:])
            try:
                if int(info['servers'][len(info['servers'])-1]['id'])+1 > max_node:
                    max_node = int(info['servers'][len(info['servers'])-1]['id'])+1
            except Exception:
                pass            
            if info['info'] == 'endone':
                current_node += 1
        except Exception:
            pass
        #print(f'{current_node}/{max_node}', end='\r')
        progressbar(current_node, max_node, desc='Litespeedtest running progress')

    # Generate proxies list
    with open('./out.json', 'r', encoding='utf-8') as f:
        proxies_all = json.load(f)
    #Remove temp file
    os.remove('./out.json')
    os.chdir(work_dir)

    output_list = []
    output_range = config['outputRange']
    if ',' in output_range:
        output_range = {'begin': int(output_range.split(',',1)[0]),'end': int(output_range.split(',',1)[1])}
    elif output_range == '-1':
        output_range = {'begin': 0, 'end': len(proxies_all)}
    else:
        output_range = {'begin': 0, 'end': int(output_range)}
    for index in range(output_range['begin'],output_range['end']):
        try:
            proxy = proxies_all[index]['Link']
            output_list.append(proxy)
        except Exception:
            pass
    content = base64.b64encode('\n'.join(output_list).encode('utf-8')).decode('ascii')
    return content

def confighandler(input_config):
    """Config handler for litespeedtest config
    target handling config parameters:
        subscription: Subcription to speedtest, support local file path or url
        outputRange: output proxy list range. Set value to '-1' means output all the prorxies, '99' means output 0 to 99 proxies, '99,999' means output 99 to 999 proxies.
        concurrency: The number of proxies tested in one time
        timeout: Time period that cannot connect to the tested proxy
    function input_config variant should be a dictionary which has keys and values of above parameters
    """
    with open('./config.json', 'r', encoding='utf-8') as f:
        lite_config = json.load(f)

    lite_config['subscription'] = input_config['subscription']
    lite_config['outputRange'] = input_config['outputRange']
    if input_config['concurrency'] != -1:
        lite_config['concurrency'] = input_config['concurrency']
    if input_config['timeout'] != -1:
        lite_config['timeout'] = input_config['timeout']

    with open('./config.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(lite_config, sort_keys=False, indent=4, ensure_ascii=False))

def progressbar(current,range,desc,size=60):
    empty='*'
    increment = '█'

    if range != 0:
        x = int(size * current / range)
    else:
        x = 0

    raw_bar = empty * size
    update = increment * x
    updated_bar = '['+update+raw_bar[x:]+']'+'    '+str(current)+'/'+str(range)
    print(desc+': '+updated_bar, end='\r', flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test nodes, and output base64 subscription file.')
    parser.add_argument('--subscription', '-s', help='Subcription url or local file path', default='https://raw.githubusercontent.com/Jason6111/TopFreeProxies/master/sub/sub_merge_base64.txt')
    parser.add_argument('--range', '-r', help='Target proxies range to output', default="99")
    parser.add_argument('--path', '-p', help='Output file path', default='./output.txt')
    args = parser.parse_args()

    # Write content to file(relative path to script directory)
    work_dir = os.getcwd()
    output = speedtest(args.subscription,str(args.range))
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with open(args.path, 'w', encoding='utf-8') as f:
        f.write(output)
    os.chdir(work_dir)
