import enum


class Token(enum.Enum):
	IncrPtr = ">"
	DecrPtr = "<"
	Incr = "+"
	Decr = "-"
	StdOut = "."
	StdIn = ","
	LoopStart = "["
	LoopEnd = "]"


class Interpreter:
	def __init__(self, program: str, c_size: int = 8, m_size: int = 30000):
		self.stack = []             # stack for keeping track of loops
		self.tokens = []            # tokenized list of brainfuck instructions
		self.data_ptr = 0           # pointer to current cell in memory
		self.instr_ptr = 0          # pointer to current instruction
		self.program = program      # string of brainfuck script
		self.cell_size = c_size     # size of memory cells (in bits)
		self.memory = [0] * m_size  # array of cells that serves as program memory

	def parse(self):
		while self.instr_ptr < len(self.program):
			token = Token(self.program[self.instr_ptr])

			if token == Token.LoopStart:
				self.stack.append([])
			elif token == Token.LoopEnd:
				if self.stack:
					loop = self.stack.pop()
					if self.stack:
						self.stack[-1].append(loop)
					else:
						self.tokens.append(loop)
				else:
					Exception(
						"BF script error: no matching open bracket for closed bracket at {}".format(self.instr_ptr))
			else:
				if self.stack:
					self.stack[-1].append(token)
				else:
					self.tokens.append(token)

			self.instr_ptr += 1

		if self.stack:
			Exception("BF script error: no matching closed bracket for open bracket")
