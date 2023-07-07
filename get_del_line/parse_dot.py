import functools
import glob
import os.path
from multiprocessing import Manager
from multiprocessing.pool import Pool
import re
import pydot
from tqdm import tqdm


def parse_dot(pdg):
    if not os.path.exists(pdg):
        return None
    data = pydot.graph_from_dot_file(pdg)
    if data == None:
        data, func_name = read_dot(pdg)
        dot = pydot.graph_from_dot_data(data)
        if dot == None:
            return None
        return dot,func_name
    else:
        return data[0],data[0].obj_dict['name']

def parse_dot_data(pdg_data):
    dot = pydot.graph_from_dot_data(pdg_data)
    if dot == None:
        return None
    return dot[0], dot[0].obj_dict['name']

def read_dot(pdg):
    with open(pdg,'r') as f:
        lines = f.readlines()
        f.close()
    pdg_line = []
    func_name = None
    graph_name = lines[0]
    if ':' in graph_name or '~' in graph_name:
        line_sp = graph_name.split(' ')
        for l in line_sp:
            if ':' in l or '~' in l:
                func_name = l
                break

        lines[0] = lines[0].replace(':', '').replace('~','')




    data = ''+lines[0]
    for i in range(1,len(lines)-1):
        index = lines[i].find('label')
        temp = lines[i][:index]+' label=""]\n'
        # data += lines[i]+'\n'
        data += temp
    data += lines[-1]
    return data,func_name

# 读取过滤后的的dot文件
def read_fiter_dot(pdg):
    with open(pdg, 'r') as f:
        lines = f.readlines()
        f.close()
    graph_name = lines[0]
    if ':' in graph_name or '~' in graph_name:
        line_sp = graph_name.split(' ')
        for l in line_sp:
            if ':' in l or '~' in l:
                func_name = l
                break
    else:
        func_name = None
    lines[0] = lines[0].replace(':', '').replace('~', '')
    data = ''+lines[0]
    for i in range(1, len(lines) ):
        data+=lines[i]
    return  data,func_name

# path = '/home/chen/source/code_slice/dataset/big-vul_dataset/pdg/test/0_5405_WebInspectorProxyGtk.dot'
# import pydot
# data = pydot.graph_from_dot_file(path)
# print(data)
# data,func_name = read_dot('/home/chen/source/code_slice/dataset/big-vul_dataset/pdg/test/0_5405_WebInspectorProxyGtk.dot')
# dot = pydot.graph_from_dot_data(data)
# data = parse_dot(path)
# if not data == None:
#     print(data[0])
#     print(data[1])
# else:
#     print('error')

# test
# pdg_dir = '/home/chen/source/code_slice/dataset/big-vul_dataset/pdg/test/'
# input_files = glob.glob(pdg_dir+'*.dot')
# i = 0
# for pdg in input_files:
#     dot,fun_name = parse_dot(pdg)
#
#     if not dot == None:
#
#         i+=1
#         # print(data[0], end="")
#         # print(data[1])
#     else:
#         print('error '+str(i)+' pdg')


# 过滤dot文件，只存id


# 尝试删除dot文件中引号的内容
def test(dot):
    with open(dot, 'r') as f:
        dot = f.read()
        # pattern = r'"(?:\\.|[^"\\])*"'
        pattern = r'"(?:\\.|[^"\\])*"'
        matches = re.findall(pattern, dot,re.DOTALL)  #

    for match in matches:
        if not match[1:-1].isdigit():
            rs = r"{}".format(match)
            dot = dot.replace(rs,'""')
            # new_dot= re.sub(match, '\"\"', dot)

    # new_dot = re.sub(pattern,lambda m: m.group() if m.group().isdigit() else "", dot)
    # print(new_dot)
    # print(matches)
    # print(dot)
    pattern = r'"(?:\\.|[^"\\])*\\\\?"'
    matches = re.findall(pattern, dot,re.DOTALL)  #
    # print(matches)
    new_dot  = dot
    for match in matches:
        # rs = r'{}'.format(match)
        new_dot = new_dot.replace(match, '')

    return new_dot

if __name__ == '__main__':
    # 将dot文件删除label内容并写入
    path = '/mnt/d/source/mvul_gadgets/v100/pdgs/'
    input_files = glob.glob(path+'*.dot')
    i = 0
    new_dir = '/mnt/d/source/mvul_gadgets/v100/filter_pdgs/'
    if not os.path.exists(new_dir):
        os.mkdir(new_dir)
    for pdg in input_files:
        data = test(pdg)  # 得到改行字符串内容
        new_file = new_dir+pdg.split('/')[-1]
        if not os.path.exists(new_file):
            with open(new_file,'w') as f :
                f.write(data)

        # datas = parse_dot_data(data)
        # if datas == None:
        #     print('sad')
        #     continue
        # dot = datas[0]
        # fun_name = datas[1]
        # if not dot == None:
        #
        #     i+=1
        #     # print(data[0], end="")
        #     # print(data[1])
        # else:
        #     print('error '+str(i)+' pdg')


    # test(path+'/8_0.dot')
