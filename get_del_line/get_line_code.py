import glob
import json

from slice import parse, parse_td_id
import os
def get_left_code(source_file,del_line,label):
    # 按行读取源代码
    if not os.path.exists(source_file):
        print('file '+source_file+'not exist')
        return
    source_list = []
    raw_line_list = []
    with open(source_file,'r') as f:
        line = f.readline()
        i = 1
        j=1
        while(line):
            if not i in del_line:
                source_list.append(line)
            i+=1
            line = f.readline()

        f.close()



    return source_list
def get_del_code(pdg,json):
    line_list = parse(pdg, json)  # 要删除的行
    if line_list == None:
        return None
    del_list = []
    for line in line_list:
        if not line in del_list:
         del_list.append(line)


    return del_list

import argparse
def parse_options():
    parser = argparse.ArgumentParser(description='Extracting Cpgs.')
    parser.add_argument('-i ', '--input', help='The dir path of input', type=str, default='train')
    args = parser.parse_args()
    return args



def load_json(file,pdg_dir,json_dir):  # 之前版本的得到line的json文件，弃用
    result = {}
    filename = file.split('/')[-1].split('.')[0]
    pdg_file = pdg_dir + filename + '.dot'
    json_file = '/mnt/f/label2/line/train/' + filename + '.json'
    if os.path.exists(json_file):
        return
    try:
        del_list = get_del_code(pdg_file, file)
    except:
        del_list = None

    dels = []
    # 对del_list进行优化
    if del_list == None or len(del_list) == 0:
        result[filename] = None
        # 存储为json文件
        with open(json_file, 'w') as f:
            json.dump(result, f)
            f.close()
        return


    flag = False
    for del_line in del_list:
        if len(del_line) == 0:
            continue
        else:
            flag = True
            dels.append(del_line)

    if flag == True:
        result[filename] = dels
    else:
        result[filename] = None

    # 存储为json文件

    with open(json_file, 'w') as f:
        json.dump(result, f)
        f.close()


# 得到删除行
def get_del_list(pdg_file, json_file):
    try:
        del_lines = get_del_code(pdg_file, json_file)
    except:
        del_lines = None

    if del_lines == None or len(del_lines) == 0:
        return None

    dels = []
    flag = False
    for del_line in del_lines:
        if len(del_line) == 0:
            continue
        else:
            flag = True
            dels.append(del_line)

    if flag == True:
        return dels
    else:
        return None


# 对删除的行的函数返回进行过滤

from tqdm import tqdm
from multiprocessing import  Manager, Pool
import functools
def main():  # 得到code gadget的操作
    args = parse_options()
    type = args.input
    json_dir = '/home/chen/source/code_slice/dataset/big-vul_dataset/jsons/'
    pdg_dir = '/home/chen/source/code_slice/dataset/big-vul_dataset/pdg/'
    label = '/home/chen/source/code_slice/dataset/big-vul_dataset/label2/'
    line_label ='line_label.npy'
    fun_label = 'fun_label.npy'
    json_dir = json_dir+type
    pdg_dir = pdg_dir+type+'/'
    files = glob.glob(json_dir+'/*.json')
    result = {}

    for file in files:

        load_json(file,pdg_dir,json_dir)  #

    # with Manager():
    #     pool = Pool(20)
    #     process_func =functools.partial(load_json,pdg_dir=pdg_dir,json_dir=json_dir)
    #     dirs = [dir for dir in tqdm(pool.imap_unordered(process_func, files), desc=f"pdg paths: ", total=len(files), )]
    #     pool.close()
    #     pool.join()


def process(dir,path,source_path,line_path):
    if not os.path.exists(dir):
        print('dir:' + dir + 'not exist')
        return
    vul_dot = dir + '/1.dot'
    no_vul_dot = dir + '/0.dot'
    vul_json = dir + '/1.json'
    no_vul_json = dir + '/0.json'
    vul_source = source_path + dir.split('/')[-1] + '/1.c'
    no_vul_source = source_path + dir.split('/')[-1] + '/0.c'
    with open(vul_source, 'r', encoding='utf-8') as f:
        source_vul = f.read()

    if not os.path.exists(vul_source) or not os.path.exists(no_vul_source):
        print('not source file' + vul_source)
        return


    json_dir_path = line_path + dir.split('/')[-1] + '/'
    vul_json_filename = line_path+dir.split('/')[-1] + '_1.json'
    no_vul_json_filename = line_path + dir.split('/')[-1] + '_0.json'
    if os.path.exists(vul_json_filename) and os.path.exists(no_vul_json_filename):
        return
    # 得到删除行
    try:
        vul_del_list = get_del_list(vul_dot, vul_json)  # 得到要删除的代码行
    except:
        vul_del_list = None
    try:
         no_vul_del_list = get_del_list(no_vul_dot, no_vul_json)
    except:
        no_vul_del_list = None

    # 存储为json文件

    if not os.path.exists(vul_json_filename):
        with open(vul_json_filename, 'w') as f:
            json.dump(vul_del_list, f)
            f.close()


    if not os.path.exists(no_vul_json_filename):
        with open(no_vul_json_filename, 'w') as f:
            json.dump(no_vul_del_list, f)
            f.close()

def load_pdg_json(json_file):
    with open(json_file,'r') as f:
        dicts = json.load(f)
        nodes = dicts['nodes']
        edges =dicts['edges']
        digraph_name = dicts['name']
    return digraph_name,nodes,edges

from slice import parse_id
# 输入目录, pdg_id目录和jsons文件目录,得到要删除的行
def get_del_lines(pdg_json,json):
    with open(pdg_json,'r',encoding='utf-8') as f:
        digraph_name, nodes, edges = load_pdg_json(pdg_json)
        if nodes == None:
            return None
        line_list = parse_id(nodes,edges,digraph_name,json) # 要删除的行
        if line_list == None:
            return None
        del_list = []
        for line in line_list:
            if not line in del_list:
                del_list.append(line)

        return del_list



def get_tranditional_lines(pdg_json,json):
    with open(pdg_json,'r',encoding='utf-8') as f:
        digraph_name, nodes, edges = load_pdg_json(pdg_json)
        if nodes == None:
            return None

        line_list = parse_td_id(nodes,edges,digraph_name,json) # 要删除的行
        if line_list == None:
            return None
        td_list = []
        for line in line_list:
            if not line in td_list:
                td_list.append(line)

        return td_list

# 对删除行进行过滤 去空值
def filter_lines(del_lines):
    if del_lines == None or len(del_lines) == 0:
        return None

    dels = []
    flag = False
    for del_line in del_lines:
        if len(del_line) == 0:
            continue
        else:
            flag = True
            dels.append(del_line)

    if flag == True:
        return dels
    else:
        return None

def tra_filter_lines(del_lines):
    if del_lines == None or len(del_lines) == 0:
        return None

    dels = []
    flag = False
    for del_line in del_lines:
        if len(del_line) == 0 or len(del_line) ==1:
            continue
        else:
            flag = True
            dels.append(del_line)

    if flag == True:
        return dels
    else:
        return None


# 用于多线程处理
def preprocess(j,jsons_dir,out_dir):
    jsons_filename = jsons_dir + j.split('/')[-1]
    if not os.path.exists(jsons_filename):
        return
    out_filename = out_dir + j.split('/')[-1]
    if os.path.exists(out_filename):
        return
    # dels = get_tranditional_lines(j,jsons_filename)
    dels = get_del_lines(j, jsons_filename)
    dels = filter_lines(dels)

    # 写入json文件
    with open(out_filename, 'w') as f:
        json.dump(dels, f)
        f.close()

def tradition_preprocess(j,jsons_dir,out_dir):
    jsons_filename = jsons_dir + j.split('/')[-1]
    if not os.path.exists(jsons_filename):
        return
    out_filename = out_dir + j.split('/')[-1]
    if os.path.exists(out_filename):
        return
    dels = get_tranditional_lines(j,jsons_filename)
    dels = tra_filter_lines(dels)

    if dels:
        with open(out_filename, 'w') as f:
            json.dump(dels, f)
            f.close()


if __name__ == '__main__':

    # path = '/mnt/d/source/get_source/data/'
    # source_path = '/mnt/d/source/normal/'
    # dirs = glob.glob(path+'*')
    # line_path = '/mnt/d/source/del_lines_jsons/' # 存储的目录位置
    # # for dir in dirs:
    # #     if not os.path.exists(dir):
    # #         print('dir:'+dir+'not exist')
    # #         continue
    # #     vul_dot = dir+'/1.dot'
    # #     no_vul_dot = dir + '/0.dot'
    # #     vul_json = dir + '/1.json'
    # #     no_vul_json = dir+ '/0.json'
    # #     vul_source = source_path+dir.split('/')[-1]+'/1.c'
    # #     no_vul_source = source_path + dir.split('/')[-1] + '/0.c'
    # #     with open(vul_source,'r',encoding='utf-8') as f:
    # #         source_vul  = f.read()
    # #
    # #
    # #     if not os.path.exists(vul_source) or not os.path.exists(no_vul_source):
    # #         print('not source file'+vul_source)
    # #         continue
    # #
    # #     # 得到删除行
    # #     try:
    # #         vul_del_list = get_del_list(vul_dot, vul_json)  # 得到要删除的代码行
    # #     except:
    # #         vul_del_list = None
    # #
    # #     try:
    # #         no_vul_del_list = get_del_list(no_vul_dot,no_vul_json)
    # #     except:
    # #         no_vul_del_list = None
    # #
    # #     # 存储为json文件
    # #     json_dir_path =line_path+dir.split('/')[-1]+'/'
    # #     if not os.path.exists(json_dir_path):
    # #         os.mkdir(json_dir_path)
    # #     vul_json_filename = json_dir_path+'1.json'
    # #     with open(vul_json_filename, 'w') as f:
    # #         json.dump(vul_del_list, f)
    # #         f.close()
    # #
    # #     no_vul_json_filename = json_dir_path +'0.json'
    # #     with open(no_vul_json_filename,'w') as f:
    # #         json.dump(no_vul_json_filename,f)
    # #         f.close()
    #
    #
    # # 多线程
    # with Manager():
    #
    #     pool = Pool(20)
    #     process_func = functools.partial(process,path=path,source_path=source_path,line_path=line_path)
    #     dirs = [dir for dir in tqdm(pool.imap_unordered(process_func, dirs), desc=f"get del line json: ", total=len(dirs), )]
    #     pool.close()
    #     pool.join()

    # 得到要删除的代码行并存为json文件
    json_dir = '/mnt/d/source/pdg_id/'
    jsons_dir = '/mnt/d/source/jsons/'
    jsons = glob.glob(json_dir+'*.json')
    out_dir = '/mnt/d/source/traditional/last_del_jsons/'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    # for j in jsons:
    #     preprocess(j,jsons_dir,out_dir)
    # 多线程
    with Manager():
        pool = Pool(20)
        process_func = functools.partial(tradition_preprocess, jsons_dir=jsons_dir,out_dir=out_dir)
        dirs = [dir for dir in tqdm(pool.imap_unordered(process_func, jsons), desc=f"writer  json: ", total=len(jsons), )]
        pool.close()
        pool.join()

    # main()









