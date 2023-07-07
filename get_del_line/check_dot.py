# 检查生成的dot文件是否可读取
import glob
import json
import os

from tqdm import tqdm
from multiprocessing import Manager,Pool
import functools
import pydot

from slice import simple_pdg
from parse_dot import read_fiter_dot


def get_nodes_pdgs(pdg_path):
    func_name = None
    try:
        dot = pydot.graph_from_dot_file(pdg_path)
    except:
        dot =None
    if dot == None:
        data, func_name = read_fiter_dot(pdg_path)
        try:
            dot = pydot.graph_from_dot_data(data)
        except:
            print('error in '+pdg_path+'---------------------------')
            return None,None
    # if dot == None:
    #     print('error '+pdg_path)
    #     return None,None
    if not dot:
        print('not dot ------------------------------')
        return None,None
    if func_name==None :
        func_name = dot[0].obj_dict['name']
    return dot[0], func_name


def check(pdg_path):

    data = get_nodes_pdgs(pdg_path)
    digraph_name = data[1]
    data = data[0]
    if data == None or digraph_name == None:
        print('error'+pdg_path)

def write_json(pdg,outdir):  # 将节点和边写入out_dir中
    filename = outdir+pdg.split('/')[-1].split('.')[0]+'.json'
    if os.path.exists(filename):
        return
    data = get_nodes_pdgs(pdg)
    digraph_name = data[1]
    data = data[0]
    if data == None or digraph_name == None:
        print('error' + pdg)
        return

    # 得到边和节点
    pdg_nodes = data.get_nodes()
    pdg_edges = data.get_edges()
    nodes,edges = simple_pdg(pdg_nodes, pdg_edges)

    # 写入到json文件
    dicts = {}
    dicts['nodes'] = nodes
    dicts['edges'] = edges
    dicts['name'] = digraph_name
    with open(filename,'w',encoding='utf-8') as f:
        json.dump(dicts,f)

if __name__ == '__main__':
    dir = '/mnt/d/source/mvul_gadgets/v100/filter_pdgs/'  # 过滤后的pdg文件
    pdgs = glob.glob(dir+'*.dot')
    i = 0
    # for pdg in pdgs:
    #
    #     data = get_nodes_pdgs(pdg_path=pdg)
    #     digraph_name = data[1]
    #     data = data[0]
    #     if data == None or digraph_name==None:
    #         print(i)
    #         i+=1
    outdir = '/mnt/d/source/mvul_gadgets/v100/pdg_id/'
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    write_json(pdgs[0],outdir)
    with Manager():

        pool = Pool(20)
        process_func = functools.partial(write_json,outdir=outdir)
        dirs = [dir for dir in tqdm(pool.imap_unordered(process_func, pdgs), desc=f"writer  json: ", total=len(pdgs), )]
        pool.close()
        pool.join()



