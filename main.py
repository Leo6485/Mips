from sys import argv
import re

d = """
main:
    move $t0, $a0
    addi $t1, $zero, 0
    addi $t2, $zero, 1
    beq $t0, $zero, done
    beq $t0, 1, done
fib_loop:
    add $t3, $t1, $t2
    move $t1, $t2
    move $t2, $t3
    sub $t0, $t0, 1
    bgtz $t0, fib_loop
done:
    move $v0, $t2
"""

if len(argv) > 1:
    with open(argv[1], "r") as f:
        data = f.read()
else:
    data = d

data = data.replace("&", "$").replace(",", "")
lines = data.splitlines()

instructions = []
labels = {}
pc = 0
for line in lines:
    line = line.strip()
    if not line:
        continue
    if line.endswith(":"):
        labels[line[:-1]] = pc
    else:
        instructions.append(line.split())
        pc += 1

def i2bin(value):
    return format(int(value) & 0xffff, '016b')

def get_reg(reg):
    if not reg.startswith('$'):
        reg = '$' + reg
    reg = reg[1:]
    reg_map = {"zero": 0, "at": 1, "v": 2, "a": 4, "t": 8, "s": 16,
               "t8": 24, "k": 26, "gp": 28, "sp": 29, "fp": 30, "ra": 31}
    reg_type = re.sub(r'\d', '', reg)
    numero = re.sub(r'\D', '', reg)
    base = reg_map.get(reg_type, 0)
    num = base + (int(numero) if numero else 0)
    return format(num, '05b')

def binstr_to_hexstr(num):
    return hex(int(num, 2))[2:].zfill(8)

def R(inst):
    opcode = "000000"
    rs = get_reg(inst[2])
    rt = get_reg(inst[3])
    rd = get_reg(inst[1])
    shamt = "00000"
    funct_map = {"add": "100000", "sub": "100010", "and": "100100", "or": "100101",
                 "xor": "100110", "nor": "100111", "slt": "101010", "sll": "000000",
                 "srl": "000010", "sra": "000011"}
    funct = funct_map[inst[0]]
    return opcode + rs + rt + rd + shamt + funct

def I(inst, labels, pc):
    if inst[0] == "li":
        code = "001000"
        rs = "$zero"
        rt = inst[1]
        imm = inst[2]
    elif inst[0] in ["beq", "bne"]:
        code = "000100" if inst[0] == "beq" else "000101"
        rs = inst[1]
        rt = inst[2]
        offset = labels[inst[3]] - (pc + 1)
        imm = str(offset)
    elif inst[0] == "bgtz":
        code = "000111"
        rs = inst[1]
        rt = "$zero"
        offset = labels[inst[2]] - (pc + 1)
        imm = str(offset)
    else:
        mapping = {"addi": "001000", "andi": "001100", "ori": "001101",
                   "xori": "001110", "slti": "001010", "lw": "100011", "sw": "101011"}
        code = mapping[inst[0]]
        rt = inst[1]
        rs = inst[2]
        imm = inst[3]
    return code + get_reg(rs) + get_reg(rt) + i2bin(imm)

def J(inst, labels):
    opcode_map = {"j": "000010", "jal": "000011"}
    opcode = opcode_map[inst[0]]
    addr = format(labels[inst[1]], '026b')
    return opcode + addr

binary_instructions = []
for i, inst in enumerate(instructions):
    if inst[0] == "move":
        inst = ["add", inst[1], inst[2], "$zero"]
    if inst[0] in ["addi", "li", "lw", "sw", "andi", "ori", "xori", "slti", "beq", "bne", "bgtz"]:
        binary_instructions.append(I(inst, labels, i))
    elif inst[0] in ["add", "sub", "and", "or", "xor", "nor", "slt", "sll", "srl", "sra"]:
        binary_instructions.append(R(inst))
    elif inst[0] in ["j", "jal"]:
        binary_instructions.append(J(inst, labels))

def print_bin(bin_text):
    print(bin_text[0:6], bin_text[6:11], bin_text[11:16], bin_text[16:21], bin_text[21:])

for bin_inst in binary_instructions:
    print_bin(bin_inst)

for bin_inst in binary_instructions:
    print(binstr_to_hexstr(bin_inst))
