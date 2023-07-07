from .node import Node


class AST:
    def __init__(self, nodes, indentation):  # nodes为json中的ast:[{id,edges,properties}] ，indentation = 1
        self.size = len(nodes) # ast中的节点数量
        self.indentation = indentation + 1
        self.nodes = {node["id"].split(".")[-1]: Node(node, self.indentation) for node in nodes}   # id:Node

    def __str__(self):
        indentation = self.indentation * "\t"
        nodes_str = ""

        for node in self.nodes:
            nodes_str += f"{indentation}{self.nodes[node]}"

        return f"\n{indentation}Size: {self.size}\n{indentation}Nodes:{nodes_str}"

    def get_nodes_type(self):
        return {n_id: node.type for n_id, node in self.nodes.items()}  # 返回 id:type索引






