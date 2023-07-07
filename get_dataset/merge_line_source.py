import glob
import json
import os.path
import os
import shutil


def delete_folders_with_incorrect_file_count(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if len(os.listdir(dir_path)) != 4:
                print(f"Deleting folder {dir_path}...")
                # os.rmdir(dir_path)
                shutil.rmtree(dir_path)


if __name__ == '__main__':
    source_path = '/mnt/d/source/normal/'
    del_jsons = '/mnt/d/source/traditional/last_del_jsons/'
    out_path = '/mnt/d/source/traditional/feature_merge/'
    if not os.path.exists(out_path):
        os.mkdir(out_path)

    jsons = glob.glob(del_jsons+'/*.json')
    for del_json in jsons:
        name = del_json.split('/')[-1].split('.')[0]  # 例如:1_1
        new_dir_path = out_path+name.split('_')[0]
        if not os.path.exists(new_dir_path):
            os.mkdir(new_dir_path)

        # 将源代码写入

        soure_filename = source_path+name.split('_')[0] +'/' +name.split('_')[-1]+'.c'
        if not os.path.exists(soure_filename):
            print(soure_filename+'not exsit')
            continue
        # 读取源代码
        with open(soure_filename,'r',encoding='utf-8') as f:
            source = f.read()

        # 写入
        new_source_name = new_dir_path+'/'+name.split('_')[-1]+'.c'
        if not os.path.exists(new_source_name):
            with open(new_source_name,'w',encoding='utf-8') as f:
                f.write(source)
                f.close()

        # 将json文件写入
        with open(del_json,'r') as f:
            del_data = json.load(f)

        new_json_path = new_dir_path+'/'+name.split('_')[-1]+'.json'
        if not os.path.exists(new_json_path):
            with open(new_json_path,'w') as f:
                json.dump(del_data,f)
                f.close()

    # 删除文件夹中特征不全的文件夹
    delete_folders_with_incorrect_file_count(out_path)




