import pickle

import pandas as pd
import csv
# path = './/test.csv'
# csv_reader = csv.reader(open(path))
# for row in csv_reader:
#     print(row)

# 读取pickle
# with open('train.pikle','rb') as f:
#     i = 0
#     j = 0
#     datas = pickle.load(f)
#     for i in range(len(datas['lines'])):
#         if not datas['lines'][i] == None:
#             # print(i,end='\t')
#             j+=1
#             # print(datas['source'][i])
#
#     print(i)
#     print(j)

# 进行数据增强 复杂扩大10倍
with open('val.pikle', 'rb') as f:
    datas = pickle.load(f)
    for i in range(len(datas['lines'])):
        if not datas['lines'][i] == None:
            for j in range(10):
                datas['source'].append(datas['source'][i])
                datas['lines'].append(datas['lines'][i])
                datas['raw_codes'].append(datas['raw_codes'][i])
    f.close()


with open('add_val.pikle','wb') as file:
    pickle.dump(datas, file)