import os

from delete_code import load_line

if __name__ == '__main__':
    dir_path = 'dataset'
    data = load_line('real_line.pkl')  # 有行号的标签

    for key in data:
        lines = data[key]
        dir = dir_path + '//' + key
        vul_file = dir + '//1.c'
        no_vul_file = dir + '//0.c'
        if not os.path.exists(vul_file) or not os.path.exists(no_vul_file):
            print('error')


