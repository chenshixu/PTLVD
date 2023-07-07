import csv
import glob
import json

import pandas as pd
from tqdm import tqdm
from multiprocessing import  Manager, Pool
import functools


def load_json(jsonfile):
    with open(jsonfile,'r') as f:
        data = f.read()
        file = json.loads(data)
        codes = file['codes']



        code_list = []
        if file['del_lines'] == None:
            source = file['codes'][0]
            raw_lines = file['codes'][1]
            code = ''
            flag = True
            if raw_lines == None or len(raw_lines) == 0:
                flag = False
            raw_code = []
            for i in range(0,len(source)):
                if flag and i+1 in raw_lines:
                    raw_code.append(source[i])
                code += source[i]
            code_list.append([code,raw_lines,raw_code])
        else:
            for c in codes:
                code = ''
                raw_code = []
                flag = True
                if c[1] == None or len(c[1]) == 0:
                    flag = False
                for i in range(0,len(c[0])):
                    if flag == True and i+1 in c[1]:
                        raw_code.append(c[0][i])
                    code += c[0][i]
                code_list.append([code, c[1], raw_code])  # code gadget ,代码行，代码行代码

    return code_list

import pickle
# gadget = load_json('/mnt/f/label2/gadget/test/1_99_xpath.json')
json_dir = '/mnt/f/label2/gadget/val/'
jsonfiles = glob.glob(json_dir+'*.json')
i = 0
datas = {}
datas = {'source':[], 'lines':[], 'raw_codes':[]}
with open('./val.pikle','wb') as f:
    for file in jsonfiles:
        data = load_json(file)
        for d in data:
            datas['source'].append(d[0])
            datas['lines'].append(d[1])
            datas['raw_codes'].append(d[2])
            # writer.writerow(d[1],d[2],d[3])
        i+=1
        print(i)
        # if i==10:
        #     print()

    pickle.dump(datas,f)
    f.close()



# with open('./test.csv','w',encoding='utf-8') as f:
#     writer = csv.writer(f)
#     for file in jsonfiles:
#         data = load_json(file)
#         for d in data:
#             writer.writerow(d[1],d[2],d[3])
#         i+=1
#         print(i)
#         if i==10:
#             break
            
# with open('./test.csv','w',encoding='utf-8') as f:
#     writer = csv.writer(f)
#     # df =pd.DataFrame(columns=['source','lines','raw_codes'])
#     for file in jsonfiles:
#         data = load_json(file)
#         for d in data:
#             # new_data = {'source':d[0], 'lines':d[1], 'raw_codes':d[2]}
#
#             # df = df.append(new_data,ignore_index=True)
#             i += 1
#             # df = df.append(d[0],ignore_index=True)
#             # df = df.append(d[1],ignore_index=True)
#             # df = df.append(d[2],ignore_index=True)
#             # df.loc[''] = d[0]
#             # df.loc['idx2'] = None if d[1] ==None else pd.Series(d[1])
#             # df.loc['idx3'] = None if d[2]==None else pd.Series(d[2])
#         print(i)
#         if i == 10:
#             break
#     df.to_csv('test1.csv',header=True)
# with Manager():
#
#     pool = Pool(20)
#     dirs = [dir for dir in tqdm(pool.imap_unordered(load_json, jsonfiles), desc=f"gadget: ", total=len(jsonfiles), )]
#     pool.close()
#     pool.join()



