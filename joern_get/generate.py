# 生成new_bins 和new_c_data
import glob
import os.path
import shutil
if __name__ == '__main__':
    bins_dir = '/mnt/d/source/mvul_gadgets/bins/'
    bins = glob.glob(bins_dir+'*')
    out_new_bins_dir = '/mnt/d/source/mvul_gadgets/new_bins/'
    if not os.path.exists(out_new_bins_dir):
        os.mkdir(out_new_bins_dir)
    for bin in bins:
        vul_path = bin+'/1.bin'
        no_vul_path = bin + '/0.bin'
        if not os.path.exists(vul_path) or not os.path.exists(no_vul_path):
            print('path error')

        # 复制文件
        new_vul_path = out_new_bins_dir + bin.split('/')[-1] + '_1.bin'
        new_no_vul_path = out_new_bins_dir + bin.split('/')[-1] + '_0.bin'
        shutil.copy2(vul_path,new_vul_path)
        shutil.copy2(no_vul_path,new_no_vul_path)




