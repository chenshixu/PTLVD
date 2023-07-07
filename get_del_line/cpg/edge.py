class Edge:
	def __init__(self, edge, indentation):
		self.id = edge["id"].split(".")[-1]  # id
		self.type = self.id.split("@")[0]  # edges中的类型：Ast or Cfg 或后来添加的Ddg
		self.node_in = edge["in"].split(".")[-1]  # in
		self.node_out = edge["out"].split(".")[-1] 	# out
		self.indentation = indentation + 1   # 几级目录，方便打印

	def __str__(self):
		indentation = self.indentation * "\t"
		return f"\n{indentation}Edge id: {self.id}\n{indentation}Node in: {self.node_in}\n{indentation}Node out: {self.node_out}\n"