import os
import sys
import time
import argparse

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
    parser = argparse.ArgumentParser(description='An interpreter for brainfuck scripts.')
    parser.add_argument("path", metavar="file-path", help="path to the brainfuck script")
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

        unit_map = {"ns": ("nanoseconds", 1),
                    "us": ("microseconds", 10 ** 3),
                    "ms": ("milliseconds", 10 ** 6),
                    "s": ("seconds", 10 ** 9)}

        start = time.perf_counter_ns()
        run(program)
        end = time.perf_counter_ns()
        runtime = (end - start) // unit_map[args.r][1]

        print("\nTime to parse: {} {}".format(runtime, unit_map[args.r][0]))


if __name__ == '__main__':
    main()
