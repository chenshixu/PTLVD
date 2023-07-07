

def sub_slice_backFor(ast_all_node_list, startnode, list_node, not_scan_list, flag):
    if startnode in not_scan_list:
        return list_node, not_scan_list
    
    list_node.append(startnode)  # 添加该节点到集合中
    not_scan_list.append(startnode) # 添加该节点到集合中

    if flag == 'back':
        predecessor_id_list = startnode.ddg_predecessors()  # 找到边out到startnode的Node
        adj_node_id_list = predecessor_id_list   
    elif flag == 'for':
        successor_id_list = startnode.ddg_successors()
        adj_node_id_list = successor_id_list   

    if adj_node_id_list != []:
        for p_node_id in adj_node_id_list:
            p_node = ast_all_node_list[p_node_id]  # 其Node类型
            list_node, not_scan_list = sub_slice_backFor(ast_all_node_list, p_node, list_node, not_scan_list, flag)  # 对p_node进行递归找

    return list_node, not_scan_list


def program_slice_backFor(ast_all_node_list, startnode, flag):
    backFor_slice = []
    not_scan_list = []
    list_node = [startnode]

    if flag == 'back':
        predecessor_id_list = startnode.ddg_predecessors()  # 向前切片 找到startnode的Edge中到startnode的节点 ，返回id字符串
        adj_node_id_list = predecessor_id_list   
    elif flag == 'for':
        successor_id_list = startnode.ddg_successors()
        adj_node_id_list = successor_id_list   

    if adj_node_id_list != []:
        for p_node_id in adj_node_id_list:
            p_node = ast_all_node_list[p_node_id]  # 通过id得到Node
            list_node, not_scan_list = sub_slice_backFor(ast_all_node_list, p_node, list_node, not_scan_list, flag)   # 深度寻路通过边找节点
    backFor_slice += list_node
    return backFor_slice


def program_slice(ast_all_node_list, startnode):
    _slice = []
    flag = 'back'
    back_list = program_slice_backFor(ast_all_node_list, startnode, flag)  # 向上深度寻路找到所有路径节点集合
    flag = 'for'
    for_list = program_slice_backFor(ast_all_node_list, startnode, flag)
    for back_node in back_list:
        _slice.append(back_node)
    for for_node in for_list:
        if for_node not in _slice:
            _slice.append(for_node)
    
    if len(_slice) == 1:
        return None
    elif len(_slice) == 2:
        for node in _slice:
            if node.label == 'MethodReturn' or node.label == 'MethodParameterIn':
                return None

    print(startnode.id, startnode.properties.line_number())
    line_num_dict = {}  # 行号对应类型的字典，一行可能有多个节点
    for node in _slice:
        line_num = int(node.properties.line_number())
        node_type = node.label
        if line_num not in line_num_dict.keys():
            line_num_dict[line_num] = []
        line_num_dict[line_num].append(node_type)
    line_dict = sorted(line_num_dict)
    for line_num in line_dict:
        print('\t',line_num, line_num_dict[line_num])
    print('---------------------\n')
    return _slice


def type_slice(ast_all_node_list,pointer_node_list):
    _pointer_slice_list = []
    pointer_list = []
    # 找到变量节点对应的句子节点
    for pointer_node in pointer_node_list:
        if pointer_node.node_type == 'Identifier':
            ast_parent = pointer_node.get_ast_parents()
            ast_parent_node = ast_all_node_list[ast_parent]
            # 一直找到他有ddg边的ast parents
            while (ast_parent_node.has_ddg_edge() == None):
                if ast_parent_node.get_ast_parents().split("[")[0] == 'Method':
                    break
                ast_parent_node = ast_all_node_list[ast_parent_node.get_ast_parents()]

            if ast_parent_node not in pointer_list:
                pointer_list.append(ast_parent_node)

        else:
            if pointer_node not in pointer_list:
                pointer_list.append(pointer_node)

    i = 0
    while (len(pointer_list) != 0):
        pointer_node = pointer_list[i]
        slice_list = program_slice(ast_all_node_list, pointer_node)
        if slice_list == None:
            i += 1
            if i == len(pointer_list):
                break
            continue
        if slice_list not in _pointer_slice_list:
            _pointer_slice_list.append(slice_list)
        flag = 0
        for node in slice_list:
            if node in pointer_list:
                pointer_list.remove(node)
                flag = 1
                i = 0
        if flag == 0:
            i += 1
    return _pointer_slice_list

def pointer_slice(ast_all_node_list, pointer_node_list):  # 存储的类型都为Node类型
    _pointer_slice_list = []
    pointer_list = []   # 存储指针节点（更新有ddg边的节点）

    # 找到指针节点对应的句子节点
    for pointer_node in pointer_node_list:
        if pointer_node.node_type == 'Identifier':
            ast_parent = pointer_node.get_ast_parents()     # 得到第一个ast边的out节点的Node类型的id
            ast_parent_node = ast_all_node_list[ast_parent]  # 根据id得到Node类型的parent节点
            # 一直找到有ddg边的ast parents
            while(ast_parent_node.has_ddg_edge() == None): 
                if ast_parent_node.get_ast_parents().split("[")[0] == 'Method':  # 到树根了 Method
                    break
                ast_parent_node = ast_all_node_list[ast_parent_node.get_ast_parents()]  # 找它的上级ast节点 Node类型

            if ast_parent_node not in pointer_list:   # 找到后查看是否已经存储过
                pointer_list.append(ast_parent_node)  # 存储到列表

        else: # 若不是indentifier，也存储
            if pointer_node not in pointer_list:
                pointer_list.append(pointer_node)

    i = 0
    while(len(pointer_list) != 0):
        pointer_node = pointer_list[i]
        slice_list = program_slice(ast_all_node_list, pointer_node)  # 进行代码切片
        if slice_list == None:
            i += 1
            if i == len(pointer_list):
                break
            continue
        if slice_list not in _pointer_slice_list:            #
            _pointer_slice_list.append(slice_list)  # 将point_node切片得到的节点列表加入
        flag = 0
        for node in slice_list:  # 遍历point_node的切片列表
            if node in pointer_list:    # 若切片中有指针节点
                pointer_list.remove(node)   # 指针列表移除该节点
                flag = 1
                i = 0
        if flag == 0:
            i += 1            
    return _pointer_slice_list        


def array_slice(ast_all_node_list, array_node_list):
    _array_slice_list = []
    array_list = []

    for array_node in array_node_list:
        if array_node.label == 'indirectIndexAccess' : # 确定节点
            ast_parent = array_node.get_ast_parents()
            ast_parent_node = ast_all_node_list[ast_parent]
            while(ast_parent_node.has_ddg_edge() == None):
                if ast_parent_node.get_ast_parents().split("[")[0] == 'Method':
                    break
                ast_parent_node = ast_all_node_list[ast_parent_node.get_ast_parents()]
            if ast_parent_node not in array_list:
                array_list.append(ast_parent_node)
        else:
            if array_node not in array_list:
                array_list.append(array_node)

    i = 0

    while(len(array_list) != 0):
        arr_node = array_list[i]
        slice_list = program_slice(ast_all_node_list, arr_node)
        if slice_list == None:
            i += 1
            if i == len(array_list):
                break
            continue
        if slice_list not in _array_slice_list:
            _array_slice_list.append(slice_list)
        flag = 0
        for node in slice_list:
            if node in array_list:
                flag = 1
                array_list.remove(node)
                i = 0
        if flag == 0:
            i += 1            
    return _array_slice_list


#  提前变量
#



def call_slice(ast_all_node_list, call_list):
    _call_slice_list = []
    call_node_dict = {}

    for call_node in call_list:
        if call_node not in call_node_dict.keys():
            call_node_dict[call_node] = []

    for call_node in list(call_node_dict.keys()):
        slice_list = program_slice(ast_all_node_list, call_node) 
        if slice_list == None:
            continue
        if slice_list not in _call_slice_list:
            _call_slice_list.append(slice_list)
    return _call_slice_list

                
        
def inte_slice(ast_all_node_list, integer_node_list):
    _integer_slice_list = []
    integer_list = []

    for integer_node_id in integer_node_list:
        integer_node = ast_all_node_list[integer_node_id]
        if integer_node not in integer_list:
            integer_list.append(integer_node)

    i = 0
    while(len(integer_list) != 0):
        integer_node = integer_list[i]
        slice_list = program_slice(ast_all_node_list, integer_node)
        if slice_list == None:
            i += 1
            if i == len(integer_list):
                break
            continue
        if slice_list not in _integer_slice_list:
            _integer_slice_list.append(slice_list)
        flag = 0
        for node in slice_list:
            if node in integer_list:
                integer_list.remove(node)
                flag = 1
                i = 0
        if flag == 0:
            i += 1            
    return _integer_slice_list

def sup_slice(ast_all_node_list, node_list):
    _slice_node_list = []
    _slice_list = []
    for node in node_list:
        if node.node_type == 'Identifier':
            ast_parent = node.get_ast_parents()
            ast_parent_node = ast_all_node_list[ast_parent]
            # 一直找到他有ddg边的ast parents
            while(ast_parent_node.has_ddg_edge() == None): 
                if ast_parent_node.get_ast_parents().split("[")[0] == 'Method':
                    break
                ast_parent_node = ast_all_node_list[ast_parent_node.get_ast_parents()]

            if ast_parent_node not in _slice_node_list:
                _slice_node_list.append(ast_parent_node)
        
        elif node.label == 'indirectIndexAccess' :
            ast_parent = node.get_ast_parents()
            ast_parent_node = ast_all_node_list[ast_parent]
            while(ast_parent_node.has_ddg_edge() == None):
                if ast_parent_node.get_ast_parents().split("[")[0] == 'Method':
                    break
                ast_parent_node = ast_all_node_list[ast_parent_node.get_ast_parents()]
            if ast_parent_node not in _slice_node_list:
                _slice_node_list.append(ast_parent_node)

        else:
            if node not in _slice_node_list:
                _slice_node_list.append(node)

    i = 0
    while(len(_slice_node_list) != 0):
        pointer_node = _slice_node_list[i]
        slice_list = program_slice(ast_all_node_list, pointer_node)
        if slice_list == None:
            i += 1
            if i == len(_slice_node_list):
                break
            continue
        if slice_list not in _slice_list:            
            _slice_list.append(slice_list)
        flag = 0
        for node in slice_list:
            if node in _slice_node_list:
                _slice_node_list.remove(node)
                flag = 1
                i = 0
        if flag == 0:
            i += 1            
    return _slice_list        
