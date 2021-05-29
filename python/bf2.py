import sys
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
		self.stack = []                   # stack for keeping track of loops
		self.tokens = []                  # tokenized list of brainfuck instructions
		self.data_ptr = 0                 # pointer to current cell in memory
		self.instr_ptr = 0                # pointer to current instruction
		self.program = program            # string of brainfuck script
		self.cell_size = c_size           # size of memory cells (in bits)
		self.memory = [0] * m_size        # array of cells that serves as program memory
		self.max_int = 2 << (c_size - 1)  # max int size (greater values will wrap around past 0)

	def incr_ptr(self):
		self.data_ptr += 1
		if self.data_ptr == len(self.memory):
			self.memory += [0] * (len(self.memory) // 2)

	def decr_ptr(self):
		self.data_ptr -= 1

	def incr(self):
		self.memory[self.data_ptr] += 1
		self.memory[self.data_ptr] %= (2 << (self.cell_size - 1))

	def decr(self):
		self.memory[self.data_ptr] -= 1
		self.memory[self.data_ptr] %= (2 << (self.cell_size - 1))

	def stdout(self):
		sys.stdout.write(self.memory[self.data_ptr])
		sys.stdout.flush()

	def stdin(self):
		self.memory[self.data_ptr] = ord(sys.stdin.read(1))

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
