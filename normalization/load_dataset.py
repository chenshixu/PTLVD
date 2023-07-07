import pickle
from sklearn.model_selection import KFold,train_test_split
def load_data(path):
    with open(path,'rb') as f:
        data = pickle.load(f)
        f.close()
    return data

def write_data(data,path):
    with open(path, "wb") as f:
        pickle.dump((data[0], data[1]), f)
        f.close()
if __name__ == '__main__':
    train_data = load_data('train.pkl')
    test_data = load_data('test.pkl')
    val_data = load_data('val.pkl')
    datas = train_data+test_data+val_data
    x = []
    y = []
    for data in datas:
        x.append(data[0])
        y.append(data[1])
    train,test_val ,y_train,y_val_test=train_test_split(x, y, test_size=0.2, random_state=20)
    test,val,y_test,y_val = train_test_split(test_val, y_val_test, test_size=0.5, random_state=20)
    train_data = [train,y_train]
    test_data = [test,y_test]
    val_data = [val, y_val]

    write_data(train_data,'3_train.pkl')
    write_data(test_data, '3_test.pkl')
    write_data(val_data, '3_val.pkl')


    print()
