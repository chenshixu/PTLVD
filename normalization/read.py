import pickle

with open('/mnt/d/source/mVulPreter-main/line.pkl','rb') as f:
    labels = pickle.load(f)
    print(labels)