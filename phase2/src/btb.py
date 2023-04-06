class BTB:
	def __init__(self):
		self.table = {}

	def find(self, pc):
		if pc in self.table.keys():
			return True
		return False

	def enter(self, type, pc, to_take_address):
		if type:
			self.table[pc] = [True, to_take_address]
		elif to_take_address > pc:
			self.table[pc] = [False, to_take_address]
		else:
			self.table[pc] = [True, to_take_address]

	def predict(self, pc):
		return self.table[pc][0]

	def getTarget(self, pc):
		return self.table[pc][1]
