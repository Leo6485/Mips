from sys import argv
import re

d = """
inicio:
addi $t0, $t0, 10
j exit
sw $t0, 4, $zero
lw $ra, 4, $zero
exit:
"""

if len(argv) > 1:
    with open(argv[1], "r") as f:
        data = f.read()
else:
    data = d

def i2bin(value):
    return format(int(value), '016b')

def get_reg(reg):
    reg = reg[1:]
    reg_map = {
        "zero": 0, "at": 1, "v": 2, "a": 4,
        "t": 8, "s": 16, "t8": 24, "k": 26,
        "gp": 28, "sp": 29, "fp": 30, "ra": 31
    }
    reg_type = re.sub(r'\d', '', reg)
    numero = re.sub(r'\D', '', reg)

    num = reg_map.get(reg_type, 0) + int("0"+numero)
    return format(int(num), '05b')

def binstr_to_hexstr(num):
    return hex(int(num, 2))[2:].zfill(8)

def R(inst):
    opcode = "000000"
    rs = get_reg(inst[2])
    rt = get_reg(inst[3])
    rd = get_reg(inst[1])
    shamt = "00000"
    
    funct_map = {
        "add": "100000", "sub": "100010", "and": "100100", "or": "100101",
        "xor": "100110", "nor": "100111", "slt": "101010", "sll": "000000",
        "srl": "000010", "sra": "000011"
    }
    funct = funct_map[inst[0]]
    
    return opcode + rs + rt + rd + shamt + funct

def I(inst):
    opcode_map = {
        "addi": {"code": "001000", "rs": inst[2], "rt": inst[1], "imm": inst[3]},
        "lw": {"code": "100011", "rs": inst[3], "rt": inst[1], "imm": inst[2]},
        "sw": {"code": "101011", "rs": inst[3], "rt": inst[1], "imm": inst[2]},
        "andi": {"code": "001100", "rs": inst[2], "rt": inst[1], "imm": inst[3]},
        "ori": {"code": "001101", "rs": inst[2], "rt": inst[1], "imm": inst[3]},
        "xori": {"code": "001110", "rs": inst[2], "rt": inst[1], "imm": inst[3]},
        "slti": {"code": "001010", "rs": inst[2], "rt": inst[1], "imm": inst[3]},
        "beq": {"code": "000100", "rs": inst[1], "rt": inst[2], "imm": inst[3]},
        "bne": {"code": "000101", "rs": inst[1], "rt": inst[2], "imm": inst[3]}
    }
    
    if inst[0] == "li":
        inst = {"code": "001000", "rs": inst[1], "rt": "$0", "imm": inst[2]}
    else:
        inst = opcode_map[inst[0]]
    
    opcode = inst["code"]
    rs = get_reg(inst["rs"])
    rt = get_reg(inst["rt"])
    imm = i2bin(inst["imm"])
    
    return opcode + rs + rt + imm

def J(inst, labels):
    opcode_map = {
        "j": "000010", "jal": "000011"
    }
    opcode = opcode_map[inst[0]]
    addr = format(labels[inst[1]], '026b')

    return opcode + addr

data = data.replace(",", "")
data_labels = data.replace(":\n", ":")
data_labels = data_labels.split("\n")

data = [i.split() for i in data.strip().split("\n")]

binary_instructions = []
labels = {}

for i, line in enumerate(data_labels):
    if ":" in line:
        pos = line.index(":")
        labels[line[:pos]] = i - 1
del data_labels

for i, line in enumerate(data):
    if line[0] in ["addi", "li", "lw", "sw", "andi", "ori", "xori", "slti", "beq", "bne"]:
        binary_instructions.append(I(line))
    elif line[0] in ["add", "sub", "and", "or", "xor", "nor", "slt", "sll", "srl", "sra"]:
        binary_instructions.append(R(line))
    elif line[0] in ["j", "jal"]:
        binary_instructions.append(J(line, labels))

for bin_inst in binary_instructions:
    print(binstr_to_hexstr(bin_inst))
