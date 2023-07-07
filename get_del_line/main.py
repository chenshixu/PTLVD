import pydot
import json
file = 'export.dot'
file = 'ddg//0-ddg.dot'
dot = pydot.graph_from_dot_file(file,encoding='utf-8')[0]
ddg_edge_list = dot.get_edges()
node_list = dot.get_nodes()
# print(ddg_edge_list)
for dot_edge in ddg_edge_list:
    try:
        dot_edge_attr = dot_edge.obj_dict['attributes']['label'][1:-1]  # 有label的边
        src = dot_edge.get_source()[1:-1]
        print(src)
    except:
        dot_edge_attr = '$head'
        continue



