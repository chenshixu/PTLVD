# 删除注释
import os.path

# 先加载line_label
import pickle
import re

def load_line(path):
    if not os.path.exists(path):
        print('not label file exsit')
        return None
    with open(path, 'rb') as f:
        datas = pickle.load(f)
    return datas


def delete_explanatory(file, marked_lines = None):  # 漏洞版本
    if not os.path.exists(file):
        print('file not exit')
        return
    with open(file, 'r') as f:
        code = f.readlines()

    # 删除注释
    lines = code
    standardized_code = []
    line_number = 1
    in_block_comment = False
    in_string = False
    for line in lines:
        # 处理多行字符串
        if not in_string and line.count('"') % 2 == 1:  # 不在字符串中且字符串不匹配 "引号个数为奇数个 表示最后一个"后续为字符串
            in_string = True

        elif in_string and line.count('"') % 2 == 1:    # 在字符串中且字符串不匹配   最后一个"前是字符串 ，后面是代码语句
            in_string = False

        # 删除行尾注释
        if not in_string:
            line = line.split('//')[0].strip()

        # 删除块注释
        if in_block_comment:
            block_comment_end_index = line.find('*/')
            if block_comment_end_index != -1:
                in_block_comment = False
                line = line[block_comment_end_index + 2:].strip()
            else:
                continue
        block_comment_start_index = line.find('/*')
        if block_comment_start_index != -1:
            in_block_comment = True
            line = line[:block_comment_start_index].strip()

        if len(line) > 0:
            if line_number in marked_lines:
                standardized_code.append(">>> " + str(line_number) + ": " + line)
            else:
                standardized_code.append(str(line_number) + ": " + line)
            line_number += 1
    return '\n'.join(standardized_code)

def delete_explanatory_novul(file): # 非漏洞版本
    if not os.path.exists(file):
        print('file not exit')
        return
    with open(file,'r') as f:
        source = f.read()


def has_zhuanyi(code):  # 判断是否有引号
    if '\"' in code or '\'' in code:
        return True
    return False


def delete_Double(line): # 删除代码单行注释 (没有做字符串检验)
    if '//' in line:
        line = line[:line.index('//')]+'\n'
    while '/*' in line and '*/' in line:
        start = line.index('/*')
        end = line.index('*/')+2
        line = line[:start] + line[end:]
    return line

def is_in_yinhao(line):     # 判断是否//或/* */在引号中
    # 若没有引号
    if not has_zhuanyi(line):
        return False



def get_sentence(line):  # 判断是否有字符串内的转义引号，若存在则返回存在转义字符的字符串的索引号,反之返回None
    if not has_zhuanyi(line):  # 没有引号
        return None
    else:
        pattern = r'"(?:\\.|[^"\\])*"'
        matches = re.findall(pattern, line)  # 得到改行字符串内容
        indexs = []
        for match in matches:
            start = line.find(match)
            end = start + len(match)
            indexs.append([int(start), int(end)])   # match == line[start:end]
        return indexs


# 判断代码行字符串中是否有// /* 和 */
def has_zhushi(line):
    indexs = get_sentence(line)
    if indexs == None:
        return False
    flag = False
    for index in indexs:
        start = index[0]
        end = index[1]
        str = line[start: end]
        if '//' in str or '/*' in str or '*/' in str:
            flag = True

    return flag

def is_pipei(line):  # 判断代码的/* 和*/个数是否匹配 若 /* 大于 */ 且存在/*则返回true
    start_index = line.find('/*')
    if start_index == -1:   # 没有/*
        return False
    while start_index != -1:
        # 查找*/的位置
        end_index = line.find('*/',start_index+2)
        if end_index == -1: # 没有则说明在多行代码注释中
            return True
        # 查找下一个位置
        start_index = line.find('/*',end_index+2)


def find_end(line): # 判断代码是注释结束行并返回
    start_index = line.find('*/')
    if start_index == -1:
        return -1
    return start_index



def get_codes(lines):
    code = ''
    is_duohang = False
    for line in lines:
        if is_duohang:  # 直接找*/
            end_index = line.find('*/')
            if end_index == -1: # 没有*/ 全部删除
                line = '\n'
            else:
                line =line[end_index+2:]
                is_duohang = False

        # 判断字符串
        indexes = get_sentence(line) # 得到所有字符串索引
        if indexes == None or not has_zhushi(line): # 没有字符串或字符串中没有注释字符 ,删除注释
            # 先删除//后的内容 和第一个/* */
            if '//' in line:
                line = line[:line.index('//')] + '\n'
            # 判断/* */是否匹配
            if not '*/' in line and not '/*' in line:  # 若没有注释部分
                code += line
                continue
            if not is_pipei(line) : # 若不 /*大于 */ 且/*存在
                while '*/' in line: #  删除/**/注释
                    line = delete_Double(line)
            else: # 不匹配则多行注释
                is_duohang = True
                while '*/' in line:
                    line = delete_Double(line)
                # 删除 /*后的内容
                i = line.find('/*')
                line = line[:i]+'\n'
            code += line

        else: # 字符串中有// 或 /* 或 */
            # 先删除单行注释
            index_xiegan = get_index_xiegan(line,indexes) # 得到在引号外的//索引
            if not index_xiegan == None:
                line = line[:index_xiegan]+'\n'
            # 查看是否还存在/*号注释 ,不存在也
            indexs = get_sentence(line)
            if indexs == None :  # 删除后没有引号里的内容了
                code += line
                continue
            starts,ends = get_lindex_xin(line, indexs)  # 得到在引号外的 /* */位置 , start 和end的先后顺序已经排号
            if len(starts) != len(ends):  # 不匹配，说明有多行注释
                is_duohang = True
                c = ''
                end_index = 0
                if len(ends) == 0 and len(starts) == 1: # 只有一个/*在后面的情况
                    line = line[:starts[0]]+'\n'
                    code += line
                    continue
                for i in range(len(ends)):
                    if i == 0: # 第一个则从开头开始
                        end_index = starts[i + 1]
                        c += line[:starts[i]] + line[ends[i]+2:end_index]
                    elif i>0: # 从上面的位置开始加
                        if i+1 <len(starts):
                            c += line[end_index+1:starts[i]:] + line[ends[i]+2:starts[i+1]]
                            end_index = starts[i+1]


                line = c +'\n'

            else:   # 删除 /*  */的内容
                c = ''
                for i in range(len(starts)):
                    c += line[:starts[i]] + line[ends[i]+2:]
                line = c

            code += line

    return code




def remove_comments(s, comments_indices):
    result = ""
    i = 0
    inside_comment = False
    while i < len(s):
        if inside_comment:
            if len(comments_indices) > 0 and i == comments_indices[0][1] - 1:
                inside_comment = False
                i += 1
                comments_indices.pop(0)
        elif len(comments_indices) > 0 and i == comments_indices[0][0]:
            inside_comment = True
            comments_indices.pop(0)
        else:
            result += s[i]
        i += 1
    return result

# 得到在引号外的 /* */位置  返回 '/*' 索引列表 和'*/' 索引列表
def get_lindex_xin(line,indexs):
    is_in_yinhao = False
    out_start = []
    out_end = []
    for i in range(len(line)):
        # 判断i 是否在引号字符串内
        flag = False
        for index in indexs:
            if i in index:
                flag = True
                break
        if flag == True:
            is_in_yinhao = not is_in_yinhao
        if not is_in_yinhao and line[i:i+2] == '/*':
            out_start.append(i)
        if not is_in_yinhao and line[i:i+2] == '*/':
            out_end.append(i)


    return out_start, out_end

def get_index_xiegan(line,indexs):  # 若引号内有//，查找在引号外的//位置 ,若没有返回None ,有则返回最前面的位
    out = []
    is_in = False
    for i in range(len(line)):
        flag = False  # 是否在字符串中
        for index in indexs:
            if i in index:
                flag = True
                break
        if flag:
            is_in = not is_in
        if line[i:i+2]=='//' and is_in == False :
            if i>0 and line[i-1] == '*':
                continue
            out.append(i)

    if len(out) == 0:
        return None
    # 返回最小的索引
    temp = out[0]
    for data in out:
        if data < temp:
            temp = data
    return data




def get_code(lines): #得到无单行注释版本
    code = ''
    is_duohang = False  # 判断是否在多行注释中
    for line in lines:
        indexs = get_sentence(line)
        if indexs == None:  # 没有字符串
            # 判断是否在line中 有单行注释
            if is_duohang:  # 若为多行的下一行
                end_index = find_end(line)  # 查看是否在该行结束
                if end_index == -1:     # 若没有 */符合
                    line = '\n'
                else:
                    is_duohang = False
                    line = line[end_index+2:]
            if not is_pipei(line):
                line = delete_Double(line)
            else:  # 若没有多行注释 删除单行注释并匹配
                start_index = line.find('/*')
                while start_index != -1:
                    # 查找*/的位置
                    end_index = line.find('*/', start_index + 2)
                    # 删除 /* 到 */的内容
                    if end_index == -1:    # 没有则说明在多行代码注释中
                        # 删除 /* 之后的内容
                        line = line[:start_index]+'\n'
                        is_duohang = True
                        break
                    line = line[:start_index] + line[end_index+2:]
                    start_index = line.find('/*')

        else:   # 有字符串，判断字符串中是否有注释内容
            if is_duohang:  # 查看是否在多注释中
                end_index = find_end(line)  # 查看是否在该行结束
                if end_index == -1:  # 若没有 */符合
                    line = '\n'
                else:   # 有*/ 判断是否在字符串中 ,直接删除到*/
                    line = line[end_index + 2:]
                    is_duohang = False
                code += line
                continue
            if has_zhushi(line):
                line = line
            else:
                if not is_pipei(line):
                    line = delete_Double(line)
                else:
                    line = line
        code += line

    return code





def filter_code(filename):# 删除代码注释
    with open(filename, 'r',encoding='utf-8') as f:
        source = f.readlines()
    code = get_codes(source)
    return code



if __name__ == '__main__':
    dir_path = 'dataset'
    data = load_line('real_line.pkl')  # 有行号的标签
    for key in data:
        lines = data[key]
        dir = dir_path+'//'+key
        if not os.path.exists(dir):
            print(dir+'not exist')
            continue
        vul_file = dir+'//1.c'
        no_vul_file = dir+ '//0.c'

        if key == '87':
            print()
        vul = filter_code(vul_file)
        no_vul_file = filter_code(no_vul_file)
        print(key)
        # print(vul_file)
        # print(no_vul_file)
        # 将文件写入
        dir = 'dataset_filter//'
        if os.path.exists(dir):
            print('ex')
        if not os.path.exists(dir+key):
            os.mkdir(dir+key)
        new_vul_file  = dir+key+'//'+'1.c'
        new_no_vul_file =  dir+key+'//'+'0.c'
        with open(new_vul_file,'w',encoding='utf-8') as f:
            f.write(vul)
        with open(new_no_vul_file,'w',encoding='utf-8') as f:
            f.write(no_vul_file)


        # delete_explanatory(vul_file,lines) # 删除注释

    # with open('example.c','r') as f:
    #     source = f.readlines()
    #
    # code = get_codes(source)
    # print(code)





