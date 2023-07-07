import os.path
import re
import json
import glob
import pydot
from collections import OrderedDict
from cpg.function import Function
from cpg.edge import Edge
from json_to_dot import generate_complete_json, generate_sub_json
from points_get import get_pointers_node
from slice_op import pointer_slice


def graph_indexing(graph):
    idx = graph["file"].split(".c")[0].split("/")[-1]
    del graph["file"]
    return idx, {"functions": [graph]}


def ddg_edge_genearate(ddg_dot_path, idx):
    if not os.path.exists(ddg_dot_path):
        return False
    try:
        dot = pydot.graph_from_dot_file(ddg_dot_path, encoding='utf-8')[0]
        ddg_edge_list = dot.get_edges()
    except:
        return []
    return ddg_edge_list


def json_process(file):
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as jf:
            cpg_string = jf.read()
            cpg_string = re.sub(r"io\.shiftleft\.codepropertygraph\.generated\.", '', cpg_string)
            cpg_json = json.loads(cpg_string)
            jf.close()
            return [graph_indexing(graph) for graph in cpg_json["functions"] if graph["file"] != "N/A"]



def filter_nodes(nodes):
    return {n_id: node for n_id, node in nodes.items() if node.has_code() and
            node.has_line_number() and
            node.label not in ["Comment", "Unknown"]}


def order_nodes(nodes):
    # sorts nodes by line and column
    nodes_by_column = sorted(nodes.items(), key=lambda n: n[1].get_column_number())
    nodes_by_line = sorted(nodes_by_column, key=lambda n: n[1].get_line_number())

    for i, node in enumerate(nodes_by_line):
        node[1].order = i

    return OrderedDict(nodes_by_line)  # 有序字典


def parse_to_nodes(cpg):
    nodes = {}
    for function in cpg["functions"]:
        func = Function(function)
        var_nodes = get_var_node(func)
        node_tmp = func.get_nodes()  # 得到ast中的所有节点

        var_nodes = get_use_var_node(var_nodes, node_tmp)
        # Only nodes with code and line number are selected  过滤节点，只选择存在代码和行号的节点
        filtered_nodes = filter_nodes(node_tmp)
        # var_nodes = get_var_ast_node(var_nodes, node_tmp)
        nodes.update(filtered_nodes)  # 将filtered_nodes添加到到nodes中
    return order_nodes(nodes), var_nodes  # 根据行号和列号对节点进行排序


# 得到cpg中的变量节点
def get_var_node(func):  # 得到所有Local
    var_nodes = []
    nodes = func.get_nodes()
    for node in nodes:
        if nodes[node].label == 'Local':
            var_nodes.append(nodes[node])
        elif nodes[node].label == 'MethodParameterIn':
            var_nodes.append(nodes[node])
    return var_nodes


def get_use_var_node(var_nodes, all_nodes):
    node_list = []
    for var in var_nodes:
        min = 9999
        for node in all_nodes:
            if all_nodes[node].has_code() and all_nodes[node].get_code() == var.get_code():
                if all_nodes[node].has_line_number() and int(all_nodes[node].get_line_number()) < min:
                    min = int(all_nodes[node].get_line_number())
                    temp_node = all_nodes[node]
        node_list.append(temp_node)
    return node_list


def get_var_ast_node(var_nodes, filter_nodes):
    node_list = []
    length = len(var_nodes)
    for node in var_nodes:
        if node.label == 'Identifier':
            ast_parent = node.get_ast_parents()
            ast_parent_node = filter_nodes[ast_parent]
            node_list.append(ast_parent_node)
        else:
            node_list.append(node)

    if length != len(node_list):
        print('get var len error')

    for node in node_list:
        if node.get_line_number() == None:
            print('get nan line ast parent')
    return node_list


def complete_pdg(data_nodes_tmp, ddg_edge_list):  # data_nodes_tmp 来自json的按行列排序的节点字典  ddg_edge_list 来自ddg图的边
    if type(ddg_edge_list) == bool:
        return data_nodes_tmp

    node_id_dict = {}
    for node in data_nodes_tmp:
        node_id = data_nodes_tmp[node].id.split('id=')[-1][:-1]  # 得到id编号
        node_id_dict[node_id] = data_nodes_tmp[node].id  # id编号：id全称
    for dot_edge in ddg_edge_list:
        node_in = None
        node_out = None
        src_node_id_tmp = dot_edge.get_source()[1:-1]  # ddg图中的edge的起点编号 如：1000178
        dst_node_id_tmp = dot_edge.get_destination()[1:-1]  # out id
        try:
            dot_edge_attr = dot_edge.obj_dict['attributes']['label'][1:-1]  # 有label的边中的label值    "1000178" -> "1000180"  [ label = "<RET>"] 得到  <RET>
        except:
            dot_edge_attr = '$head'  # 若没有label
            continue
        for node_id in node_id_dict.keys():
            if src_node_id_tmp == node_id:  # 若找到该编号的节点
                node_in = node_id_dict[node_id]  # 得到id全称

            elif dst_node_id_tmp == node_id:
                node_out = node_id_dict[node_id]

        if node_in == None or node_out == None:
            continue

        edge_tmp = {}
        ddg_edge_name = 'Ddg@' + dot_edge_attr
        ddg_edge_name_tmp = ddg_edge_name
        edge_tmp['id'] = ddg_edge_name
        edge_tmp['in'] = node_in
        edge_tmp['out'] = node_out
        edge = Edge(edge_tmp, indentation=3)

        cnt = 1
        while (ddg_edge_name in data_nodes_tmp[node_in].edges.keys()):  # 该id字符串的节点的所有边中是否有该id字符串
            ddg_edge_name = ddg_edge_name.split('#')[0] + '#' + str(cnt)
            cnt += 1
        data_nodes_tmp[node_in].edges[ddg_edge_name] = edge  # 添加ddg到edge中

        while (ddg_edge_name_tmp in data_nodes_tmp[node_out].edges.keys()):  # 添加ddg到该out节点的edge中
            ddg_edge_name_tmp = ddg_edge_name_tmp.split('#')[0] + '#' + str(cnt)
            cnt += 1
        ddg_edge_name = ddg_edge_name_tmp
        data_nodes_tmp[node_out].edges[ddg_edge_name] = edge

    return data_nodes_tmp  # 返回添加所有ddg边的集合




def get_pdg_nodes_id(pdg):
    if not os.path.exists(pdg):
        return False
    try:
        dot,func_name = parse_dot(pdg)
        if dot == None:
            return None
        edge_list = dot.get_edges()
        dot_node = dot.get_nodes()
    except:
        # 自己解析

        return None
    return dot_node, edge_list, func_name



def get_var_type_name(Function):
    # 得到所有变量和实参
    var_node = get_var_node(Function)
    vars = []
    for var in var_node:
        var = var.properties.get()
        type_name = var['TYPE_FULL_NAME']
        name = var['NAME']
        vars.append([type_name, name])
    return vars


def get_node_by_id(function, id):
    fun_nodes = function.ast.nodes
    for node in fun_nodes:
        if fun_nodes[node].id.split('=')[-1][:-1] == id.replace("\"", ""):
            return fun_nodes[node]
    return None


def generate_complete_pdg(function, pdg_nodes, pdg_edges):
    nodes_list = []
    edge_list = []
    fun_nodes = function.ast.nodes
    for node in fun_nodes:  # 找出json function中的非ast边
        flag = False
        Edges = fun_nodes[node].edges
        for edge_id in Edges:  # 遍历该节点的所有非ast边
            if Edges[edge_id].type == 'Ast':
                continue
            flag = True
            # 添加到pdg_edges中
            # edge_list.append(edge)
            # in_id = edge.node_in
            # out_id = edge.node_out
            # type = edge.type
            # edge_list.append([type, in_id, out_id])
            edge_list.append(Edges[edge_id])
        if flag == True:
            nodes_list.append(fun_nodes[node])  # 将该节点加入列表

    # 将pdg图中的节点生成Node对象并加入集合
    for pdg_node in pdg_nodes:
        node = get_node_by_id(function, pdg_node.get_name())

    # pdg_node_id_list = [node['name'] for node in pdg_nodes]
    # for edge in edge_list:
    #     if not edge[in_id].split('=')[:-2] in pdg_node_id_list:
    #         nodes_list.append(node())


# 只保存id和边id
def simple_pdg(pdg_nodes, pdg_edges):
    nodes_list = []
    edge_list = []
    for node in pdg_nodes:
        node = node.get_name()[1:-1]
        nodes_list.append(int(node))
    for edge in pdg_edges:
        e = edge.obj_dict['points']
        source = e[0][1:-1]
        destination = e[1][1:-1]
        edge_list.append([int(source), int(destination)])

    return nodes_list, edge_list


# 生成非ast的id和边
def simple_json_id_edge(Function):
    edge_list = []
    nodes_list = []
    nodes = Function.ast.nodes
    for node in nodes:  # 找出json function中的非ast边
        flag = False
        Edges = nodes[node].edges
        for edge_id in Edges:  # 遍历该节点的所有非ast边
            if Edges[edge_id].type == 'Ast':
                continue
            flag = True
            source = Edges[edge_id].node_out.split('=')[-1][:-1]
            destination = Edges[edge_id].node_in.split('=')[-1][:-1]
            edge_list.append([int(source), int(destination)])
        if flag == True:
            nodes_list.append(int(nodes[node].id.split('=')[-1][:-1]))  # 将该节点加入列表

    return nodes_list, edge_list



def find_first_node(nodes, function, var):
    method = function.id
    ast_nodes = function.ast.nodes
    node_list = []
    for node in nodes:
        # 查找node中funtion中的ast位置
        if node == int(method.split('=')[-1][:-1]):  # 根节点不在ast中,不找
            continue
        ast_node = None
        # 找到在ast中的节点
        for key in ast_nodes:
            if int(key.split('=')[-1][:-1]) == node:
                ast_node = ast_nodes[key]
                break

        # 该节点变量子节点
        stack = []
        stack.append(ast_node)
        while not len(stack) == 0:
            current_node = stack.pop()
            if 'NAME' in current_node.properties.get().keys() and current_node.properties.get()['NAME'] == var[1] and 'TYPE_FULL_NAME' in current_node.properties.get().keys() and current_node.properties.get()['TYPE_FULL_NAME'] == var[0]:
                node_list.append(ast_node)
                break
            # 添加子节点到stack中
            edges = current_node.edges
            if edges == None:
                continue
            for key in edges:
                if edges[key].type == 'Ast' and edges[key].node_out == current_node.id:
                    stack.append(ast_nodes[edges[key].node_in])

    # 找到最后一个节点
    # for i in range(len(node_list)):
    #     print(node_list[i].properties.line_number(),end=' ')
    #     print(node_list[i].properties.column_number())
    if len(node_list) == 0:
        return None
    last_node = node_list[0]
    for i in range(1, len(node_list)):
        if int(node_list[i].properties.line_number()) < int(last_node.properties.line_number()):

            last_node = node_list[i]
        elif int(node_list[i].properties.line_number()) == int(last_node.properties.line_number()):
            if int(node_list[i].properties.column_number()) < int(last_node.properties.column_number()):
                last_node = node_list[i]

    return last_node

def find_last_node(nodes, function, var):
    method = function.id
    ast_nodes = function.ast.nodes
    node_list = []
    for node in nodes:
        # 查找node中funtion中的ast位置
        if node == int(method.split('=')[-1][:-1]):  # 根节点不在ast中,不找
            continue
        ast_node = None
        # 找到在ast中的节点
        for key in ast_nodes:
            if int(key.split('=')[-1][:-1]) == node:
                ast_node = ast_nodes[key]
                break

        # 该节点变量子节点
        stack = []
        stack.append(ast_node)
        while not len(stack) == 0:
            current_node = stack.pop()
            if 'NAME' in current_node.properties.get().keys() and current_node.properties.get()['NAME'] == var[1] and 'TYPE_FULL_NAME' in current_node.properties.get().keys() and current_node.properties.get()['TYPE_FULL_NAME'] == var[0]:
                node_list.append(ast_node)
                break
            # 添加子节点到stack中
            edges = current_node.edges
            if edges == None:
                continue
            for key in edges:
                if edges[key].type == 'Ast' and edges[key].node_out == current_node.id:
                    stack.append(ast_nodes[edges[key].node_in])


    # 找到最后一个节点
    if len(node_list)==0:
        return None
    # for i in range(len(node_list)):
    #     print(node_list[i].properties.line_number(),end=' ')
    #     print(node_list[i].properties.column_number())
    last_node = node_list[0]
    for i in range(1, len(node_list)):
        if int(node_list[i].properties.line_number()) > int(last_node.properties.line_number()):

            last_node = node_list[i]
        elif int(node_list[i].properties.line_number()) == int(last_node.properties.line_number()):
            if int(node_list[i].properties.column_number()) > int(last_node.properties.column_number()):
                last_node = node_list[i]

    return last_node




def get_slice_nodes(method_id, edges, id):
    stack = []
    stack.append(id)
    node_list = []
    # 向前切片
    while not len(stack) == 0:
        temp_node = stack.pop()
        node_list.append(temp_node)
        for edge in edges:
            source = edge[0]
            destination = edge[1]
            if destination == temp_node:
                # 若已经遍历过，不加入栈
                if not source in node_list:
                    stack.append(source)
                if source == method_id:
                    break

    # 向后切片
    back_list = []
    stack = []
    stack.append(id)
    while not len(stack) == 0:
        temp_node = stack.pop()
        node_list.append(temp_node)
        for edge in edges:
            source = edge[1]
            destination = edge[0]
            if destination == temp_node:
                # 若已经遍历过，不加入栈
                if not source in node_list:
                    stack.append(source)
                if source == method_id:
                    break

    # 防止意外向后切片
    node_list += back_list
    return list(set(node_list))


def get_all_line(slice_nodes_id, function):
    line = []

    nodes = function.ast.nodes

    for key in nodes:
        id = int(key.split('=')[-1][:-1])
        for slice_id in slice_nodes_id:
            if slice_id == id or id == int(function.id.split('=')[-1][:-1]):
                line.append(int(nodes[key].properties.line_number()))
                continue

    return line

from parse_dot import parse_dot



def parse_td_id(pdg_nodes,pdg_edges,func_name,json):  #得到传统的code gadgets的代码行号
    file_name, functions_cpg = load_json(json)
    # ast_nodes = parse_to_nodes(functions_cpg)
    function = None
    for fun in functions_cpg['functions']:
        if fun['function'] == func_name:
            function = Function(fun)
            break
    if function == None:
        print('no json funcion')
        return

    nodes, edges = simple_json_id_edge(function)  # 只存非ast的边上的节点和边，只存id
    # 将两个图合并
    from functools import reduce
    from operator import add
    nodes = reduce(add, (nodes, pdg_nodes))
    # nodes = set(nodes)
    # edges = pdg_edges
    temp_edges = []
    for edge in edges:
        if edge not in temp_edges :
            temp_edges.append(edge)
    for edge in pdg_edges:
        if edge not in temp_edges:
            temp_edges.append(edge)
    edges = temp_edges
    nodes = list(set(nodes))
    #
    # 得到所有变量和实参
    focus_node = []  # id编号
    vars = get_var_type_name(function)
    for var in vars:
        last_node = find_last_node(nodes, function, var)  # 找到pdg图中最后使用var变量的节点
        first_node = find_first_node(nodes, function, var)
        if last_node == None or first_node == None:
            return None
        id = last_node.id.split('=')[-1][:-1]
        id_2 = first_node.id.split('=')[-1][:-1]
        focus_node.append([int(id), int(id_2)])

    method_id = function.id.split('=')[-1][:-1]
    slice_list = []
    for point in focus_node:
        node_list = get_slice_nodes(int(method_id), edges, point[0])  # last
        node_list += get_slice_nodes(int(method_id), edges, point[1])  # first
        node_list = list(set(node_list))

        slice_list.append(node_list)

    # 得到代码的行数集
    line_list = []
    for slice in slice_list:
        lines = get_all_line(slice, function)
        else_nodes = get_else_nodes(slice, nodes)
        else_lines = get_all_line(else_nodes, function)

        lines = list(set(lines))
        # else_lines = list(set(else_lines))
        # del_lines = get_del_lines(lines, else_lines)
        line_list.append(lines)

    # print(vars)
    return line_list

def parse_id(pdg_nodes,pdg_edges,func_name,json):  #
    file_name, functions_cpg = load_json(json)
    # ast_nodes = parse_to_nodes(functions_cpg)
    function = None
    for fun in functions_cpg['functions']:
        if fun['function'] == func_name:
            function = Function(fun)
            break
    if function == None:
        print('no json funcion')
        return

    nodes, edges = simple_json_id_edge(function)  # 只存非ast的边上的节点和边，只存id
    # 将两个图合并
    from functools import reduce
    from operator import add
    nodes = reduce(add, (nodes, pdg_nodes))
    # nodes = set(nodes)
    # edges = pdg_edges
    temp_edges = []
    for edge in edges:
        if edge not in temp_edges :
            temp_edges.append(edge)
    for edge in pdg_edges:
        if edge not in temp_edges:
            temp_edges.append(edge)
    edges = temp_edges
    nodes = list(set(nodes))
    #
    # 得到所有变量和实参
    focus_node = []  # id编号
    vars = get_var_type_name(function)
    for var in vars:
        last_node = find_last_node(nodes, function, var)  # 找到pdg图中最后使用var变量的节点
        first_node = find_first_node(nodes, function, var)
        if last_node == None or first_node == None:
            return None
        id = last_node.id.split('=')[-1][:-1]
        id_2 = first_node.id.split('=')[-1][:-1]
        focus_node.append([int(id), int(id_2)])

    method_id = function.id.split('=')[-1][:-1]
    slice_list = []
    for point in focus_node:
        node_list = get_slice_nodes(int(method_id), edges, point[0])  # last
        node_list += get_slice_nodes(int(method_id), edges, point[1])  # first
        node_list = list(set(node_list))

        slice_list.append(node_list)

    # 得到代码的行数集
    line_list = []
    for slice in slice_list:
        lines = get_all_line(slice, function)
        else_nodes = get_else_nodes(slice, nodes)
        else_lines = get_all_line(else_nodes, function)

        lines = list(set(lines))
        else_lines = list(set(else_lines))
        del_lines = get_del_lines(lines, else_lines)
        line_list.append(del_lines)

    # print(vars)
    return line_list





def parse(pdg, json):
    pdg_nodes, pdg_edges, func_name = get_pdg_nodes_id(pdg)
    if pdg_nodes ==None:
        return
    pdg_nodes, pdg_edges = simple_pdg(pdg_nodes, pdg_edges)  # 只存节点的id
    file_name, functions_cpg = load_json(json)
    # ast_nodes = parse_to_nodes(functions_cpg)
    function = None
    for fun in functions_cpg['functions']:
        if fun['function'] == func_name:
            function = Function(fun)
            break
    if function == None:
        print('no json funcion')
        return

    nodes, edges = simple_json_id_edge(function)  # 只存非ast的边上的节点和边，只存id
    # 将两个图合并
    from functools import reduce
    from operator import add
    nodes = reduce(add, (nodes, pdg_nodes))
    # nodes = set(nodes)
    # edges = pdg_edges
    temp_edges = []
    for edge in edges:
        if edge not in temp_edges:
            temp_edges.append(edge)
    edges = temp_edges
    nodes = list(set(nodes))
    #
    #得到所有变量和实参
    focus_node = []  # id编号
    vars = get_var_type_name(function)
    for var in vars:
        last_node = find_last_node(nodes, function, var)  # 找到pdg图中最后使用var变量的节点
        first_node = find_first_node(nodes,function,var)
        if last_node == None or first_node == None:
            return None
        id = last_node.id.split('=')[-1][:-1]
        id_2 = first_node.id.split('=')[-1][:-1]
        focus_node.append([int(id),int(id_2)])

    method_id = function.id.split('=')[-1][:-1]
    slice_list = []
    for point in focus_node:
        node_list = get_slice_nodes(int(method_id), edges, point[0])  #last
        node_list += get_slice_nodes(int(method_id),edges,point[1])     # first
        node_list = list(set(node_list))

        slice_list.append(node_list)

    # 得到代码的行数集
    line_list = []
    for slice in slice_list:
        lines = get_all_line(slice, function)
        else_nodes = get_else_nodes(slice, nodes)
        else_lines = get_all_line(else_nodes, function)

        lines = list(set(lines))
        else_lines = list(set(else_lines))
        del_lines = get_del_lines(lines, else_lines)
        line_list.append(del_lines)


    # print(vars)
    return line_list


def get_del_lines(lines, else_lines):
    del_lines = []
    for else_line in else_lines:
        if not else_line in lines:
            del_lines.append(else_line)
    return del_lines


def get_else_nodes(slice, nodes):
    else_nodes = []
    for node in nodes:
        if not node in slice:
            else_nodes.append(node)
    return else_nodes


def load_json(json):
    ast = json_process(json)
    data = ast[0]
    file_name = data[0]
    functions_cpg = data[1]
    return file_name, functions_cpg



 # test
# pdg_path = 'pdg//0-pdg.dot'
# # pdg_nodes,pdg_edges = get_pdg_nodes_id(pdg_path)
# line_list = parse('pdg//0-pdg.dot', 'graph2.json')  # 要删除的行
# del_list = []
# for line in line_list:
#     if not line in del_list:
#         del_list.append(line)

# test end

# data = get_left_code('.//0_4_yurex.c',del_list[0],'sad')


# data = json_process('graph2.json')
#
# data = data[0]
# idx = data[0]
# cpg = data[1]
# ddg_edge_list = ddg_edge_genearate('ddg//0-ddg.dot', '0-ddg.dot')
# data_nodes_tmp, var_nodes = parse_to_nodes(cpg)  # var_nodes为identifier节点
# data_nodes = complete_pdg(data_nodes_tmp, ddg_edge_list)  # 给data_nodes_tmp添加pdg边并返回
#
# generate_complete_json(data_nodes, './', idx)  # 生成pdg文件
#
# slice_nodes = get_var_ast_node()
# pointer_node_list = get_pointers_node(data_nodes)  # 提取data_nodes中的指针节点
# if pointer_node_list != []:
#     _pointer_slice_list = pointer_slice(data_nodes, pointer_node_list)  # 得到每个指针节点的切片节点集合  （切片重复则合一）
#     points_name = '@pointer'
#     generate_sub_json(data_nodes, _pointer_slice_list, './', idx, points_name, 'label_path')
#
# #  对变量进行代码切片
#
# if var_nodes != []:
#     _var_slice_list = pointer_slice(data_nodes, var_nodes)
#
#     _var_slice_list = add_parameter_node(data_nodes)



