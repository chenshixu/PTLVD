# 删除空行
import pickle
import re

def load_data(pkl_path):
    with open(pkl_path,'rb') as f:
        datas = pickle.load(f)
        sources = datas[0]
        labels = datas[1]

    return sources,labels


def is_null_line(line):
    # 判断是否为空行
    is_blank = re.match(r'^[\s\t\n]*$', line)
    return is_blank


def del_line(source,labels):
    # 删除空行
    lines = source.split('\n')
    result = ''

    #
    if labels == None:
        for i in range(len(lines)):
            if not is_null_line(lines[i]):
                result+=lines[i]
        return result,None

    new_labels = []

    count = 0
    for i in range(len(lines)):
        if i+1 in labels:
            new_labels.append(count+1)
        if is_null_line(lines[i]):
            continue
        else:
            count += 1
            result += lines[i]

    return result,new_labels




def generate_data(data_path,out_pkl):
    sources, labels = load_data(data_path)
    new_sources = []
    new_labels = []
    for i in range(len(sources)):
        new_source, lines = del_line(sources[i], labels[i])
        new_sources.append(new_source)
        new_labels.append(lines)

    with open(out_pkl,'wb') as f:
        pickle.dump((new_sources,new_labels),f)
        f.close()


if __name__ == '__main__':
    # sources,labels = load_data('56_test.pkl')
    # file = """
    # # include<stdio.h>
    # int main()
    #     {
    #
    #
    #           dsad
    #
    #
    #
    #              asda
    #     }
    # return
    # """
    # print(del_line(file,[2,3,7,11,13]))
    # new_sources = []
    # new_labels = []
    # for i in range(len(sources)):
    #     new_source,lines = del_line(sources[i],labels[i])
    #     new_sources.append(new_source)
    #     new_labels.append(lines)

    # print(len(new_sources))
    # print(new_labels)

    generate_data('56_test.pkl','new_test.pkl')
    generate_data('56_train.pkl', 'new_train.pkl')
    generate_data('56_val.pkl', 'new_val.pkl')


