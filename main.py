import sys
import re

def i2bin(value, bits=16):
    return format(int(value) & ((1 << bits) - 1), f'0{bits}b')

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

def binstr_to_hexstr(bin_str):
    return hex(int(bin_str, 2))[2:].zfill(8)

def parse_data(data):
    data = data.replace("&", "$").replace("(", " ").replace(")", "").replace(",", "")
    lines = data.splitlines()
    instructions = []
    labels = {}
    pc = 0
    for line in lines:
        line = line.strip()
        if not line: continue
        if line.endswith(":"): labels[line[:-1]] = pc

        else:
            instructions.append(line.split())
            pc += 1
    return instructions, labels

# "instr rt, rs, immediate"
typeI_1 = lambda ops: get_reg(ops[1]) + get_reg(ops[0]) + i2bin(ops[2], 16)
typeR = lambda ops, funct: "000000" + get_reg(ops[1]) + get_reg(ops[2]) + get_reg(ops[0]) + "00000" + funct

typeJ = lambda label, pc: i2bin(labels[label], 26)

_map = {
    # I-type
    "addi": lambda ops, pc: "001000" + typeI_1(ops),
    "andi": lambda ops, pc: "001100" + typeI_1(ops),
    "ori":  lambda ops, pc: "001101" + typeI_1(ops),
    "xori": lambda ops, pc: "001110" + typeI_1(ops),
    "slti": lambda ops, pc: "001010" + typeI_1(ops),
    "lw":   lambda ops, pc: "100011" + get_reg(ops[2]) + get_reg(ops[0]) + i2bin(ops[1], 16),
    "sw":   lambda ops, pc: "101011" + get_reg(ops[2]) + get_reg(ops[0]) + i2bin(ops[1], 16),
    "beq":  lambda ops, pc: "000100" + get_reg(ops[0]) + get_reg(ops[1]) + i2bin(labels[ops[2]] - (pc + 3), 16),
    "bne":  lambda ops, pc: "000101" + get_reg(ops[0]) + get_reg(ops[1]) + i2bin(labels[ops[2]] - (pc + 3), 16),
    "bgtz": lambda ops, pc: "000111" + get_reg(ops[0]) + get_reg("$zero") + i2bin(labels[ops[1]] - (pc + 3), 16),
    # J-type
    "j":    lambda ops, pc: "000010" + typeJ(ops[0], pc),
    "jal":  lambda ops, pc: "000011" + typeJ(ops[0], pc),
    # R-type
    "add": lambda ops, pc: typeR(ops, "100000")
}

d = """
addi $t0, $zero, 1
addi $t1, $zero, 40
sw $t0, 0($zero)
sw $t0, 4($zero)
addi $t2, $zero, 8
for:
beq $t2, $t1, fim
lw $t3, -4($t2)
lw $t4, -8($t2)
add $ra, $t3, $t4
sw $ra, 0($t2)
addi $t2, $t2, 4
j for	
fim:
"""


save = len(sys.argv) > 1
if len(sys.argv) > 1:
    with open(sys.argv[1], "r") as f:
        data = f.read()
else:
    data = d

instructions, labels = parse_data(data)
binary_instructions = []
for pc, inst in enumerate(instructions):
    opcode = inst[0]
    ops = inst[1:]
    if opcode in _map:
        bin_inst = _map[opcode](ops, pc)
        binary_instructions.append(bin_inst)

def print_bin(bin_text):
    print(bin_text[0:6], bin_text[6:11], bin_text[11:16], bin_text[16:21], bin_text[21:])

for bin_inst in binary_instructions:
    print_bin(bin_inst)

result = "v2.0 raw\n"
for bin_inst in binary_instructions:
    result += binstr_to_hexstr(bin_inst) + "\n"

print(result)

with open("data.hex", "w") as f:
    f.write(result[:-1])

