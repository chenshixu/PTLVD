import json
import os.path


def get_var(file):
    if not os.path.exists(file):
        return None
    with open(file) as f:
        data = json.load(f)
    dics = []
    for dic in data:
        if dic['_label'] == 'METHOD_PARAMETER_IN'.upper():
            if 'lineNumber' in dic:
                dics.append(dic)
        if dic['_label'] == 'Local'.upper():
            dics.append(dic)
    return dics


def get_identifier(file):
    if not os.path.exists(file):
        return None
    with open(file) as f:
        data = json.load(f)
    dics = []
    for dic in data:
        if dic['_label'] == 'IDENTIFIER':
            dics.append(dic)

    return dics


def get_local_name(dic):
    return dic['name']


def get_local_type(dic):
    return dic['typeFullName']


def get_line_number(dic):
    return dic['lineNumber']


def get_id(dic):
    return dic['id']
    

# 得到所有变量的第一次使用的节点(不包含初始化),输入为all.json
def get_first_usage_var(all_json):
    vars = get_var(all_json)
    idens = get_identifier(all_json)
    dicts = {}
    for var in vars:
        name = get_local_name(var)
        line = 99999
        temp = None
        for iden in idens:  # 找到line最小的
            if get_local_name(iden) == name:
                if get_line_number(iden) < line:
                    line = get_line_number(iden)
                    temp = iden

        dicts[name] = temp

    return dicts


def get_ast_call_id(indentifies_id, graph_json):  # 找到该节点在ast中的out节点
    with open(graph_json) as f:
        data = json.load(f)
    for func in data['functions']:
        if func['file'] != 'N/A':
            Ast = func['AST']
            for ast in Ast:
                if int(ast['id'].split('=')[-1][:-1]) == indentifies_id:
                    edges = ast['edges']
                    for edge in edges:
                        if edge['id'].split('.')[-1].split('@')[0] == 'Ast':
                            id = edge['out'].split('=')[-1][:-1]
                            return id
    return None



vars = get_first_usage_var('all2.json')
for key in vars.keys():
    var_name = get_local_name(vars[key])
    id = get_id(vars[key])
    print(id,end=':')
    print(var_name,end='\t')
    id = get_ast_call_id(id,'graph2.json')
    print(id)

