# 对删掉注释的文件,删除,后的换行符号
import os
import pickle

from delete_code import load_line, get_sentence


def normal_code(filename,lines): # vul才计算行号
    if not os.path.exists(filename):
        return None
    with open(filename,'r',encoding='utf-8') as f:
        codes = f.readlines()
    data = ''
    i = 1
    j = 1
    new_lines = []
    for code in codes:
        if j in lines:
            new_lines.append(i)
        # 查看是否有,号后换行的情况
        if code == '\n': # 先判断是否为空行
            data = data
        elif code[-2:] == ',\n' or (len(code) > 2 and (code[-3:] == ', \n'  or code[-3:] == '||\n')) : # 若后面换行则不增加行数
            data += code[:-1]
        else:
            data += code
            i += 1
        j += 1
    return data, new_lines

def normal_no_vul_code(filename):
    if not os.path.exists(filename):
        return None
    with open(filename, 'r', encoding='utf-8') as f:
        codes = f.readlines()
    data = ''
    for code in codes:
        if code == '\n': # 先判断是否为空行
            continue
        elif code[-2:] == ',\n' or (len(code) > 2 and (code[-3:] == ', \n' or code[-3:] == '||\n')):
            data += code[:-1]
        else:# 判断是否是逗号后还有空格福换行
            data += code

    return data





if __name__ == '__main__':
    dir_path = 'dataset_filter'
    data = load_line('real_line.pkl')  # 有行号的标签
    index = 0
    new = {}  # 新行号字典
    for key in data:
        index += 1
        lines = data[key]
        dir = dir_path+'//'+key
        if not os.path.exists(dir):
            print(dir+'not exist')
            continue
        vul_file = dir + '//1.c'
        no_vul_file = dir + '//0.c'

        if index == 45:
            print()

        vul_code, new_lines = normal_code(vul_file,lines)
        new[index] = new_lines  # 添加到字典中
        no_vul_code = normal_no_vul_code(no_vul_file)

        new_dir = 'normal//'
        new_fir_dir = new_dir+str(index)+'//'
        if not os.path.exists(new_fir_dir):
            os.mkdir(new_fir_dir)


        # 写入文件
        new_vul = new_fir_dir + '1.c'
        new_no_vul = new_fir_dir + '0.c'
        with open(new_vul,'w',encoding='utf-8') as f:
            f.write(vul_code)

        with open(new_no_vul, 'w', encoding='utf-8') as f:
            f.write(no_vul_code)

    with open('normal.pickle', 'wb') as f:
            pickle.dump(new, f)

    # normal_code('example2.c',[3,4,5,6,12])


