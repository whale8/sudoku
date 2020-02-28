import numpy as np
from itertools import product
from functools import reduce

class Solver():
	def __init__(self, MAP):
		self.MAP = MAP
		self.all_set = {1, 2, 3, 4, 5, 6, 7, 8, 9}
		# *9 は同じオブジェクトを複製するため避ける
		self.rows = [set() for _ in range(9)]
		self.cols = [set() for _ in range(9)]
		self.blocks = [set() for _ in range(9)] # 番号は左上から右下
		self.selections = np.array([[set([1, 2, 3, 4, 5, 6, 7, 8, 9])]*9 \
									for _ in range(9)])
		self.index = [np.ones(9, dtype=bool) for i in range(9)]
		for i, index in enumerate(self.index):
			index[i] = False

		self.preprocessing()
		
	def preprocessing(self):
		
		# initialize rows, cols and blocks
		for i in range(9):
			self.rows[i] = set(self.MAP[i])
			self.cols[i] = set(self.MAP[:, i])
			for j in range(9):
				self.blocks[(i//3)*3+j//3].add(self.MAP[i, j])

		# initialize selections
		for i, j in product(range(9), repeat=2):
			if self.MAP[i, j] != 0:
				self.selections[i, j] = set()
				continue
			else:
				sel = self.all_set - self.rows[i] \
					- self.cols[j] - self.blocks[(i//3)*3+j//3]
				if len(sel) == 1:
					num = sel.pop()
					self._setvalue(i, j, num)
					self.selections[i, j] = {}
				else:
					self.selections[i, j] = sel

		self._heuristic()


	def solve(self, name="backtracking"):
		if name == "backtracking":
			self._backtracking()
		else:
			pass

	def _setvalue(self, i, j, val):
		self.MAP[i, j] = val
		self.rows[i].add(val)
		self.cols[j].add(val)
		self.blocks[(i//3)*3+j//3].add(val)

	def _removevalue(self, i, j, val):
		self.MAP[i, j] = 0
		self.rows[i].remove(val)
		self.cols[j].remove(val)
		self.blocks[(i//3)*3+j//3].remove(val)

	def _checkvalue(self, i, j, val):
		sel = self.all_set - self.rows[i] \
			- self.cols[j] - self.blocks[(i//3)*3+j//3]
		return val in sel
		
	def _backtracking(self, i=0, j=0):
		# i: row
		# j: column
		#print(self.MAP)
		if i > 8:
			return True
		elif self.MAP[i, j] != 0: # 既に数字がある
			if j == 8:
				if self._backtracking(i+1, 0):
					return True
			else:
				if self._backtracking(i, j+1):
					return True
		else:
			for sel in self.selections[i, j]:
				if self._checkvalue(i, j, sel):
					self._setvalue(i, j, sel)
					if j == 8:
						if self._backtracking(i+1, 0):
							return True
						else:
							self._removevalue(i, j, sel)
					else:
						if self._backtracking(i, j+1):
							return True
						else:
							self._removevalue(i, j, sel)
			return False

	def _get_selection(self, i, j):
		# 縦、横、ブロックで入る可能性のある数値
		# return: 
		sel = self.selections[i, j] - (self.rows[i] \
							    | self.cols[j] | self.blocks[(i//3)*3+j//3])

		self.selections[i, j] = sel
		
		if len(sel) == 1:
			return True
		
		sel1 = sel - reduce(add_selection, \
			self.selections[i, :][self.index[j]]) # 横

		if len(sel1) == 1:
			self.selections[i, j] = sel1
			return True

		sel2 = sel - reduce(add_selection, \
			self.selections[:, j][self.index[i]]) # 縦

		if len(sel2) == 1:
			self.selections[i, j] = sel2
			return True

		bi = [(i//3)*3, (i//3+1)*3]
		bj = [(j//3)*3, (j//3+1)*3]
		
		sel3 = sel - reduce(add_selection, \
			self.selections[bi[0]:bi[1], bj[0]:bj[1]].flatten()[self.index[i%3+j%3]])

		if len(sel3) == 1:
			self.selections[i, j] = sel3
			return True

		return False

	def _heuristic(self):

		count = 0
		while True:
			for i, j in product(range(9), repeat=2):
				if self.MAP[i, j] != 0:
					count += 1
					continue
				else:
					if self._get_selection(i, j):
						self._setvalue(i, j, self.selections[i, j].pop())
					else:
						count += 1
						
			if count == 81:
				break
			else:
				count = 0


def add_selection(a, b):
	return a | b
	
	

if __name__ == "__main__":

	from time import time
	
	MAP = np.array([list(map(int, input().split())) for i in range(9)])
	#print(*MAP, sep="\n")
	print(MAP)
	print("----------------------------")
	t1 = time()
	s = Solver(MAP)
	s.solve()
	print(s.selections)
	t2 = time()
	print(s.MAP)
	print(t2-t1)
