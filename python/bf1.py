import sys


def run(program):
	stack = []
	memory = [0] * 30000
	data_pointer = 0
	instruction_pointer = 0

	while instruction_pointer < len(program):
		token = program[instruction_pointer]
		if token == ">":
			data_pointer += 1
			if data_pointer >= len(memory):
				memory += [0] * (len(memory) // 2)
		elif token == "<":
			data_pointer -= 1
		elif token == "+":
			memory[data_pointer] += 1
		elif token == "-":
			memory[data_pointer] -= 1
		elif token == ".":
			print(chr(memory[data_pointer]), end="")
		elif token == ",":
			memory[data_pointer] = ord(input("Input one alphanumeric character"))
		elif token == "[":
			if memory[data_pointer] != 0:
				stack.append(instruction_pointer)
			else:
				open_count = 1
				while instruction_pointer < len(program) and open_count > 0:
					instruction_pointer += 1
					if program[instruction_pointer] == "[":
						open_count += 1
					elif program[instruction_pointer] == "]":
						open_count -= 1
				if open_count > 0:
					print("Error: Mismatched brackets in brainfuck code. ")
					return
		elif token == "]":
			if memory[data_pointer] != 0:
				instruction_pointer = stack[-1]
			else:
				stack.pop()

		instruction_pointer += 1


def main():
	if len(sys.argv) == 1:
		print("Please provide a valid brainfuck file")
	else:
		filename = sys.argv[1]
		with open(filename) as f:
			run("".join([i.strip() for i in f.readlines()]))


if __name__ == '__main__':
	main()
