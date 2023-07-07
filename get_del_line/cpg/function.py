from .ast import AST


class Function:
    def __init__(self, function):
        self.name = function["function"]        # 函数名
        self.id = function["id"].split(".")[-1] # 函数id
        self.indentation = 1
        self.ast = AST(function["AST"], self.indentation)  # 提取该function中的AST信息

    def __str__(self):
        indentation = self.indentation * "\t"
        return f"{indentation}Function Name: {self.name}\n{indentation}Id: {self.id}\n{indentation}AST:{self.ast}"

    def get_nodes(self):
        return self.ast.nodes


    def get_nodes_types(self):
        return self.ast.get_nodes_type()
