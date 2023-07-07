import glob
import json
import os.path
from tqdm import tqdm
from multiprocessing import Manager, Pool
import functools
import numpy as np
from load_label import load_label

def get_new_line_number(raw_lines, all_lines, del_lines):  # 返回code gadget的行号和漏洞行号，若没有返回[]
    # 得到新的行号
    new_line = []
    for line in all_lines:
        if not line in del_lines:
            new_line.append(line)

    flag = False
    # 判断是否存在漏洞
    A = raw_lines
    B = new_line
    for a in A:
        if a in B:
            flag = True
            break

    line_number_list = []  #
    if flag:  # 为漏洞
        for i in range(len(new_line)):
            if new_line[i] in raw_lines:
                line_number_list.append(i + 1)

    return new_line, line_number_list


def get_tra_new_line_number(raw_lines, all_lines, lines):
    # 得到新的行号
    new_line = lines
    A = raw_lines
    B = new_line

    flag = False
    for a in A:
        if a in B:
            flag = True
            break

    line_number_list = []  #
    if flag:  # 为漏洞
        for i in range(len(new_line)):
            if new_line[i] in raw_lines:
                line_number_list.append(i + 1)

    return new_line, line_number_list





def get_tra_child_code(source,raw_lines,lines):
    code_list = []
    raw_line_list = []
    if lines == None:
        return None,None
    if raw_lines:
        # 查看code gadget是否有漏洞
        # 得到剩余的代码行号：
        for line in lines:
            all_lines = [i for i in range(1, len(source) + 1)]
            new_line, raw_list = get_tra_new_line_number(raw_lines, all_lines, line)
            code = []
            for new in new_line:
                code.append(source[new - 1])
            code_list.append(code)
            if len(raw_list) == 0:
                raw_line_list.append(None)
            else:
                raw_line_list.append(raw_list)
    else:
        for line in lines:
            code = []
            for i in range(0, len(source)):
                if  i + 1 in line:
                    code.append(source[i])
            code_list.append(code)
            raw_line_list.append(None)

    return code_list, raw_line_list



def get_chiled_code(source, raw_lines, lines):
    code_list = []
    raw_line_list = []
    if  raw_lines:
        # 查看code gadget是否有漏洞
        # 得到剩余的代码行号：
        for line in lines:
            all_lines = [i for i in range(1, len(source) + 1)]
            new_line, raw_list = get_new_line_number(raw_lines, all_lines, line)
            code = []
            for new in new_line:
                code.append(source[new - 1])
            code_list.append(code)
            if len(raw_list) == 0:
                raw_line_list.append(None)
            else:
                raw_line_list.append(raw_list)
    else:
        for line in lines:
            code = []
            for i in range(0, len(source)):
                if not i + 1 in line:  # 该行不在删除lines中
                    code.append(source[i])
            code_list.append(code)
            raw_line_list.append(None)

    return code_list, raw_line_list


def get_codes(source, raw_lines, del_lines):  # 通过源代码,漏洞行和要删除行得到code gadget
    dicts = []
    if del_lines is None:  # 若没有删除代码
        dicts.append([source,raw_lines])
        return dicts
    code_list, raw_list = get_chiled_code(source, raw_lines, del_lines)
    for i in range(0, len(code_list)):
        if raw_list is None:
            dicts.append([code_list[i], None])
        elif raw_list[i] is None:
            dicts.append([code_list[i], None])
        else:
            dicts.append([code_list[i], raw_list[i]])
    return dicts

def get_tra_codes(source, raw_lines, lines):
    dicts = []
    code_list,raw_list = get_tra_child_code(source,raw_lines,lines)
    if code_list == None:
        return None,None
    for i in range(0, len(code_list)):
        if raw_list is None:
            dicts.append([code_list[i], None])
        elif raw_list[i] is None:
            dicts.append([code_list[i], None])
        else:
            dicts.append([code_list[i], raw_list[i]])
    return dicts






def get_gadget_data(label, del_lines, source):  # 通过raw_label数组，del_lines,source得到code gadget
    codes = get_codes(source, label, del_lines)
    return codes


def get_tra_gadget_data(label,lines,source):
    codes = get_tra_codes(source,label,lines)
    return codes

# 加载文件和标签 ,返回源代码内容和漏洞代码行，删除行内容
def load_data(dir, labels):
    key = dir.split('/')[-1]  # 文件夹名 如: 1 2 3
    raw_lines = labels[int(key)]  # None 或长度大于0的数组
    c_vul = dir + '/1.c'
    json_vul = dir + '/1.json'
    c_no_vul = dir + '/0.c'
    json_no_vul = dir + '/0.json'
    with open(c_vul, 'r', encoding='utf-8') as f:
        vul = f.readlines()
    with open(c_no_vul, 'r', encoding='utf-8') as f:
        no_vul = f.readlines()

    with open(json_vul, 'r') as f:
        vul_json = json.load(f)

    with open(json_no_vul, 'r') as f:
        no_vul_json = json.load(f)

    return raw_lines, vul, vul_json, no_vul, no_vul_json



# 非之前保存的文件按行写入
def write_json(dir,labels,out_dir):

    key = dir.split('/')[-1]  # 文件夹名 如: 1 2 3
    new_out_json = out_dir + key + '.json'
    if os.path.exists(new_out_json):
        return
    raw_lines, vul, vul_json, no_vul, no_vul_json = load_data(dir, labels)
    # 得到 gadget和相应的漏洞行号
    vul_datas = get_gadget_data(raw_lines, vul_json, vul)
    no_vul_datas = get_gadget_data(None, no_vul_json, no_vul)

    # datas[key] = [vul_data, no_vul_data]
    datas = []
    for vul_data in vul_datas:
        code = ''
        for line in vul_data[0]:
            code += line
        datas.append([code,vul_data[1]])

    for no_vul_data in no_vul_datas:
        code = ''
        for line in no_vul_data[0]:
            code+= line
        datas.append([code,no_vul_data[1]])



    # 将字典写入json文件
    with open(new_out_json, 'w', encoding='utf-8') as f:
        json.dump(datas, f, indent=4)


def write_tra_json(dir,labels,out_dir):

    key = dir.split('/')[-1]  # 文件夹名 如: 1 2 3
    new_out_json = out_dir + key + '.json'
    if os.path.exists(new_out_json):
        return
    raw_lines, vul, vul_json, no_vul, no_vul_json = load_data(dir, labels)
    # 得到 gadget和相应的漏洞行号
    vul_datas = get_tra_gadget_data(raw_lines, vul_json, vul)
    no_vul_datas = get_tra_gadget_data(None, no_vul_json, no_vul)

    # datas[key] = [vul_data, no_vul_data]
    datas = []
    if vul_datas == None:
        return
    for vul_data in vul_datas:
        code = ''
        for line in vul_data[0]:
            code += line
        datas.append([code,vul_data[1]])

    for no_vul_data in no_vul_datas:
        code = ''
        for line in no_vul_data[0]:
            code+= line
        datas.append([code,no_vul_data[1]])



    # 将字典写入json文件
    with open(new_out_json, 'w', encoding='utf-8') as f:
        json.dump(datas, f, indent=4)


if __name__ == '__main__':
    label_path = '/mnt/d/source/normal.pickle'
    labels = load_label(label_path)
    data_dir =  '/mnt/d/source/traditional/feature_merge/'
    dirs = glob.glob(data_dir + "*")

    out_dir = '/mnt/d/source/traditional/gadgets_jsons/'
    datas = {}
    # i = 0
    # for dir in dirs:
    #     # if vul_json == None or no_vul_json ==None:
    #     #     i+=
    #     #
    #     write_json(dir,labels,out_dir)
        # key = dir.split('/')[-1]  # 文件夹名 如: 1 2 3
        # raw_lines, vul, vul_json, no_vul, no_vul_json = load_data(dir, labels)
        # # 得到 gadget和相应的漏洞行号
        # vul_data = get_gadget_data(raw_lines, vul_json, vul)
        # no_vul_data = get_gadget_data(None, no_vul_json, no_vul)
        #
        # # datas[key] = [vul_data, no_vul_data]
        # datas[key] = vul_data +no_vul_data

    # # 将字典写入json文件
    # new_out_json = out_dir+'line_levle_gadgets.json'
    # with open(new_out_json,'w',encoding='utf-8') as f:
    #     json.dump(datas,f,indent=4)


    # print(len(datas))
    # print(i)

    # 多线程
    with Manager():
        pool = Pool(20)
        process_func = functools.partial(write_tra_json, labels=labels,out_dir=out_dir)
        dirs = [dir for dir in tqdm(pool.imap_unordered(process_func, dirs), desc=f"writer  json: ", total=len(dirs), )]
        pool.close()
        pool.join()
