import os
import sys
import argparse
from typing import NamedTuple
from aenum import MultiValueEnum


class Token(MultiValueEnum):
    IncrPtr = ">", "<"
    Incr = "+", "-"
    StdOut = "."
    StdIn = ","
    LoopStart = "["
    LoopEnd = "]"


class CountedToken(NamedTuple):
    token: Token
    count: int


class Interpreter:
    def __init__(self, program: str, c_size: int, m_size: int):
        self.stack = []  # stack for keeping track of loops
        self.c_tokens = []  # tokenized list of brainfuck instructions
        self.data_ptr = 0  # pointer to current cell in memory
        self.instr_ptr = 0  # pointer to current instruction
        self.program = program  # string of brainfuck script
        self.cell_size = c_size  # size of memory cells (in bits)
        self.memory = [0] * m_size  # array of cells that serves as program memory
        self.max_int = 2 << (c_size - 1)  # max int size (greater values will wrap around past 0)

    def incr_ptr(self, count: int):
        self.data_ptr += count
        if self.data_ptr == len(self.memory):
            self.memory += [0] * (len(self.memory) // 2)

    def incr(self, count: int):
        self.memory[self.data_ptr] += count
        self.memory[self.data_ptr] %= (2 << (self.cell_size - 1))

    def stdout(self, count: int):
        for _ in range(count):
            sys.stdout.write(chr(self.memory[self.data_ptr]))
        sys.stdout.flush()

    def stdin(self, count: int):
        self.memory[self.data_ptr] = ord(sys.stdin.read(count))

    def parse(self):
        while self.instr_ptr < len(self.program):
            token = Token(self.program[self.instr_ptr])
            count = -1 if self.program[self.instr_ptr] in "<-" else 1

            if token == Token.LoopStart:
                self.stack.append([])
            elif token == Token.LoopEnd:
                if self.stack:
                    loop = self.stack.pop()
                    if self.stack:
                        self.stack[-1].append(loop)
                    else:
                        self.c_tokens.append(loop)
                else:
                    raise Exception(
                        "BF script error: no matching open bracket for closed bracket at {}".format(self.instr_ptr))
            else:
                while self.instr_ptr < len(self.program) - 1 and token == Token(self.program[self.instr_ptr + 1]):
                    self.instr_ptr += 1
                    count += -1 if self.program[self.instr_ptr] in "<-" else 1

                c_token = CountedToken(token=token, count=count)
                if self.stack:
                    self.stack[-1].append(c_token)
                else:
                    self.c_tokens.append(c_token)

            self.instr_ptr += 1

        if self.stack:
            raise Exception("BF script error: no matching closed bracket for open bracket")

    def execute(self, c_tokens: list):
        for c_token in c_tokens:
            if isinstance(c_token, list):
                while self.memory[self.data_ptr] != 0:
                    self.execute(c_token)
            elif c_token.token == Token.IncrPtr:
                self.incr_ptr(c_token.count)
            elif c_token.token == Token.Incr:
                self.incr(c_token.count)
            elif c_token.token == Token.StdOut:
                self.stdout(c_token.count)
            elif c_token.token == Token.StdIn:
                self.stdin(c_token.count)

    def run(self):
        self.parse()
        self.execute(self.c_tokens)


def main():
    parser = argparse.ArgumentParser(description='An interpreter for brainfuck scripts.')
    parser.add_argument("path", metavar="file-path", help="path to the brainfuck script")
    parser.add_argument("-c", help="size of each memory cell (bits)", type=int, choices=[4, 8, 16, 32], default=8)
    parser.add_argument("-m", metavar="memory-size", help="number of cells in memory", type=int, default=30000)

    args = parser.parse_args()
    script_path = args.path
    if not os.path.isfile(script_path):
        raise Exception('Input error: cannot open {} (no such file)'.format(script_path))
    elif not (script_path.endswith('.b') or script_path.endswith('.bf')):
        raise Exception('Input error: incorrect filetype for {} (must be .b or .bf)'.format(script_path))

    with open(script_path, 'r') as file:
        instructions = set("><+-.,[]")
        program = "".join([char for char in file.read() if char in instructions])
        interpreter = Interpreter(program, args.c, args.m)
        interpreter.run()


if __name__ == "__main__":
    main()
