import os
import sys
import enum
import time
import argparse


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
    def __init__(self, program: str, c_size: int, m_size: int, units: str):
        self.stack = []  # stack for keeping track of loops
        self.tokens = []  # tokenized list of brainfuck instructions
        self.data_ptr = 0  # pointer to current cell in memory
        self.instr_ptr = 0  # pointer to current instruction
        self.program = program  # string of brainfuck script
        self.cell_size = c_size  # size of memory cells (in bits)
        self.memory = [0] * m_size  # array of cells that serves as program memory
        self.max_int = 2 << (c_size - 1)  # max int size (greater values will wrap around past 0)
        self.runtime_units = units  # units to measure and output runtime in

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
        sys.stdout.write(chr(self.memory[self.data_ptr]))
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
                    raise Exception(
                        "BF script error: no matching open bracket for closed bracket at {}".format(self.instr_ptr))
            else:
                if self.stack:
                    self.stack[-1].append(token)
                else:
                    self.tokens.append(token)

            self.instr_ptr += 1

        if self.stack:
            raise Exception("BF script error: no matching closed bracket for open bracket")

    def execute(self, tokens: list):
        for token in tokens:
            if isinstance(token, list):
                while self.memory[self.data_ptr] != 0:
                    self.execute(token)
            elif token == Token.IncrPtr:
                self.incr_ptr()
            elif token == Token.DecrPtr:
                self.decr_ptr()
            elif token == Token.Incr:
                self.incr()
            elif token == Token.Decr:
                self.decr()
            elif token == Token.StdOut:
                self.stdout()
            elif token == Token.StdIn:
                self.stdin()

    def run(self):
        unit_map = {"ns": ("nanoseconds", 1),
                    "us": ("microseconds", 10 ** 3),
                    "ms": ("milliseconds", 10 ** 6),
                    "s": ("seconds", 10 ** 9)}

        start = time.perf_counter_ns()
        self.parse()
        parse_end = time.perf_counter_ns()
        self.execute(self.tokens)
        exec_end = time.perf_counter_ns()

        parse_time = (parse_end - start) // unit_map[self.runtime_units][1]
        exec_time = (exec_end - parse_end) // unit_map[self.runtime_units][1]

        print("\nTime to parse: {} {}".format(parse_time, unit_map[self.runtime_units][0]))
        print("Time to execute: {} {}".format(exec_time, unit_map[self.runtime_units][0]))


def main():
    parser = argparse.ArgumentParser(description='An interpreter for brainfuck scripts.')
    parser.add_argument("path", metavar="file-path", help="path to the brainfuck script")
    parser.add_argument("-c", help="size of each memory cell (bits)", type=int, choices=[4, 8, 16, 32], default=8)
    parser.add_argument("-m", metavar="memory-size", help="number of cells in memory", type=int, default=30000)
    parser.add_argument("-r", help="units to output runtime in", choices=["ns", "us", "ms", "s"], default="ms")

    args = parser.parse_args()
    script_path = args.path
    if not os.path.isfile(script_path):
        raise Exception('Input error: cannot open {} (no such file)'.format(script_path))
    elif not (script_path.endswith('.b') or script_path.endswith('.bf')):
        raise Exception('Input error: incorrect filetype for {} (must be .b or .bf)'.format(script_path))

    with open(script_path, 'r') as file:
        instructions = set("><+-.,[]")
        program = "".join([char for char in file.read() if char in instructions])
        interpreter = Interpreter(program, args.c, args.m, args.r)
        interpreter.run()


if __name__ == "__main__":
    main()
