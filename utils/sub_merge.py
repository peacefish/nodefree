#!/usr/bin/env python3

import json, os, time

from subconverter import convert, base64_decode


class merge():
    def __init__(self,file_dir,format_config):
        self.list_dir = file_dir['list_dir']
        self.list_file = file_dir['list_file']
        self.merge_dir = file_dir['merge_dir']
        self.update_dir = file_dir['update_dir']
        self.readme_file = file_dir['readme_file']
        self.share_file = file_dir['share_file']
        

        self.format_config = {
            'deduplicate': bool(format_config['deduplicate']), 'rename': format_config['rename'],
            'include': format_config['include_remarks'], 'exclude': format_config['exclude_remarks'], 'config': format_config['config']
            }

        self.url_list = self.read_list()
        self.sub_merge()
        if self.readme_file != '':
            self.readme_update()
        if self.update_dir != '':
            self.backup()

    def read_list(self): # 将 sub_list.json Url 内容读取为列表
        with open(self.list_file, 'r', encoding='utf-8') as f:
            raw_list = json.load(f)
        input_list = []
        for index in range(len(raw_list)):
            if raw_list[index]['enabled']:
                input_list.append(raw_list[index])
        return input_list

    def sub_merge(self): # 将转换后的所有 Url 链接内容合并转换 YAML or Base64, ，并输出文件，输入订阅列表。
        url_list = self.url_list
        list_dir = self.list_dir
        merge_dir = self.merge_dir

        for t in os.walk(list_dir): # Remvove old files
            for f in t[2]:
                f = t[0]+f
                os.remove(f)

        content_list = []
        for index in range(len(url_list)):
            content = convert(url_list[index]['url'],'url')
            ids = url_list[index]['id']
            remarks = url_list[index]['remarks']
            if content != '' and content != None:
                content_list.append(content)
                print(f'Writing content of {remarks} to {ids:0>2d}.txt\n')
            else:
                content = 'No nodes were found in url.'
                print(f'Writing error of {remarks} to {ids:0>2d}.txt\n')
            if self.list_dir != '':
                with open(f'{list_dir}{ids:0>2d}.txt', 'w', encoding= 'utf-8') as file:
                    file.write(content)

        print('Merging nodes...\n')

        content = convert(''.join(content_list),'url',self.format_config)
        content_clash = convert(''.join(content_list),'clash_provider',self.format_config)
        content_base64 = convert(''.join(content_list), 'base64',self.format_config)

        def content_write(file, output_type):
            file = open(file, 'w+', encoding = 'utf-8')
            file.write(output_type)
            file.close
        write_list = [f'{merge_dir}/sub_merge.txt', f'{merge_dir}/sub_merge_base64.txt', f'{merge_dir}/sub_merge_clash.yaml']
        content_type = (content, content_base64, content_clash)
        for index in range(len(write_list)):
            content_write(write_list[index], content_type[index])
        print('Done!\n')

    def readme_update(self): # 更新 README 节点信息

        print('Updating README...')
        with open(self.readme_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            f.close()
        # 获得当前名单及各仓库节点数量
        with open(f'{self.merge_dir}sub_merge.txt', 'r', encoding='utf-8') as f:
            total = len(f.readlines())
            total = f'合并节点总数: `{total}`\n'
            thanks = []
            repo_amount_dic = {}
            for repo in self.url_list:
                line = ''
                if repo['enabled'] == True:
                    id = repo['id']
                    remarks = repo['remarks']
                    repo_site = repo['site']

                    sub_file = f'{self.list_dir}{id:0>2d}.txt'
                    with open(sub_file, 'r', encoding='utf-8') as f:
                        proxies = f.readlines()
                        amount = len(proxies)
                        f.close()
                    repo_amount_dic.setdefault(id, amount)
                    line = f'- [{remarks}]({repo_site}), 节点数量: `{amount}`\n'
                if remarks != "Jason6111/TopFreeProxies":
                    thanks.append(line)
            f.close()

        # 高速节点打印
        for index in range(len(lines)):
            if lines[index] == '### 高速节点\n': # 目标行内容
                # 清除旧内容
                lines.pop(index+1) # 删除节点数量
                while lines[index+4] != '\n':
                    lines.pop(index+4)

                with open(self.share_file, 'r', encoding='utf-8') as f:
                    proxies_base64 = f.read()
                    proxies = base64_decode(proxies_base64)
                    proxies = proxies.split('\n')
                    proxies = ['    '+proxy for proxy in proxies]
                    proxies = [proxy+'\n' for proxy in proxies]
                top_amount = len(proxies)
                
                lines.insert(index+1, f'高速节点数量: `{top_amount}`\n')
                index += 4
                for i in proxies:
                    index += 1
                    lines.insert(index, i)
                break
        # 所有节点打印
        for index in range(len(lines)):
            if lines[index] == '### 所有节点\n': # 目标行内容
                # 清除旧内容
                lines.pop(index+1) # 删除节点数量

                with open(f'{self.merge_dir}sub_merge.txt', 'r', encoding='utf-8') as f:
                    proxies = f.read()
                    proxies = proxies.split('\n')
                    top_amount = len(proxies) - 1
                    f.close()
                lines.insert(index+1, f'合并节点总数: `{top_amount}`\n')
                """
                with open('./sub/sub_merge.txt', 'r', encoding='utf-8') as f:
                    proxies = f.read()
                    proxies = proxies.split('\n')
                    proxies = ['    '+proxy for proxy in proxies]
                    proxies = [proxy+'\n' for proxy in proxies]
                top_amount = len(proxies) - 1
                
                lines.insert(index+1, f'合并节点数量: `{top_amount}`\n')
                
                index += 5
                for i in proxies:
                    index += 1
                    lines.insert(index, i)
                """
                break
        # 节点来源打印
        for index in range(len(lines)):
            if lines[index] == '### 节点来源\n':
                # 清除旧内容
                while lines[index+1] != '\n':
                    lines.pop(index+1)

                for i in thanks:
                    index +=1
                    lines.insert(index, i)
                break

        # 写入 README 内容
        with open(self.readme_file, 'w', encoding='utf-8') as f:
            data = ''.join(lines)
            print('完成!\n')
            f.write(data)

    def backup(self):
        t = time.localtime()
        date = time.strftime('%y%m', t)
        date_day = time.strftime('%y%m%d', t)

        file_eternity = open(self.share_file, 'r', encoding='utf-8')
        sub_content = file_eternity.read()
        file_eternity.close()

        try:
            os.mkdir(f'{self.update_dir}{date}')
        except FileExistsError:
            pass
        txt_dir = self.update_dir + date + '/' + date_day + '.txt' # 生成$MM$DD.txt文件名
        file = open(txt_dir, 'w', encoding= 'utf-8')
        file.write(base64_decode(sub_content))
        file.close()

if __name__ == '__main__':
    merge()
