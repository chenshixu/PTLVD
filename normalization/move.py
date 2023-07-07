# 将bins下的文件转 为new_bins
import glob
import os.path

bins_dir = '/mnt/d/source/mvul_gadgets/bins/'
if not os.path.exists(bins_dir):
    print('not dir')
bins = glob.glob(bins_dir + '*')

for bin in bins:
    new_name = bin.split('/')[-1]
    vul_file = bin+'/1.bin'
    no_vul_file = bin+'/0.bin'
    with open(vul_file,'rb') as f:
        vul_bin = f.read()
    with open(no_vul_file,'rb') as f:
        no_vul_bin = f.read()

    new_vul_name = new_name+'_1.bin'
    new_no_vul_name = new_name+'_0.bin'

    outdir = '/mnt/d/source/mvul_gadgets/new_bins/'
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    with open(outdir+new_vul_name,'wb') as f:
        f.write(vul_bin)

    with open(outdir+new_no_vul_name,'wb') as f:
        f.write(no_vul_bin)

