# 加载标准化后源代码的漏洞行标签
import os.path
import pickle

# label_path = '/mnt/d/source/normal.pickle'


def load_label(label_path):
    if not os.path.exists(label_path):
        print('label path error!')
        return

    with open(label_path,'rb') as f:
        labels = pickle.load(f)
        return labels



# test
# labels = load_label(label_path)
# print(len(labels))