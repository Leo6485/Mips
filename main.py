from sys import argv
import re

d = """
li $s1 10
addi $s2 $s2 5
add $s1 $s1 $s1
j exit
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
    return hex(int(num, 2))[2:].zfill(8) # Garante que tenha 8 casa hexadecimais mesmo para números pequenos

def R(inst):
    opcode = "000000"
    rs = get_reg(inst[2])
    rt = get_reg(inst[3])
    rd = get_reg(inst[1])
    shamt = "00000"
    
    funct_map = {
        "add": "100000",
    }
    funct = funct_map[inst[0]]
    
    return opcode + rs + rt + rd + shamt + funct

def I(inst):
    opcode_map = {
        "addi": "001000"
    }
    
    # Pseudo instrução
    if inst[0] == "li":
        return I(["addi", inst[1], "$0", inst[2]])
    
    opcode = opcode_map[inst[0]]
    rs = get_reg(inst[2])
    rt = get_reg(inst[1])
    imm = i2bin(inst[3])
    
    return opcode + rs + rt + imm

def J(inst):
    opcode = "000010"
    
    addr = format(0, '026b')
    
    return opcode + addr

data = [i.split() for i in data.strip().split("\n")]

binary_instructions = []
labels = {}
for i, line in enumerate(data):
    if line[0] in ["addi", "li"]:
        binary_instructions.append(I(line))
    elif line[0] in ["add"]:
        binary_instructions.append(R(line))
    elif line[0] in ["j"]:
        binary_instructions.append(J(line))
    elif line[-1][-1] == ":":
        labels[line[-1][:-1]] = i
    
    print(line)
    print(binary_instructions[-1])

print(labels)
for bin_inst in binary_instructions:
    print(binstr_to_hexstr(bin_inst))
