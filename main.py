from sys import argv

d = """
li $1 10
addi $2 $2 5
add $1 $1 $1
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
    b = str(bin(int(reg[1:])))[2:]
    return b

def binstr_to_hexstr(num):
    return str(hex(int(num, 2)))

def R(inst):
    opcode = "000000"
    rs = get_reg(inst[2])
    rt = get_reg(inst[3])
    rd = get_reg(inst[1])
    shamt = "00000"
    funct = "100000"
    return opcode + rs + rt + rd + shamt + funct

def I(inst):
    if inst[0] == "li":
        return I(['addi', inst[1], "$0", inst[2]])
    
    opcode_map = {
        "addi": "001000",
        "li": "001000"
    }
    opcode = opcode_map[inst[0]]
    rs = get_reg(inst[2])
    rt = get_reg(inst[1])
    imm = i2bin(inst[3])
    return opcode + rs + rt + imm

def J(inst):
    opcode = "000010"
    addr = "0"*16
    return opcode + addr

data = [i.split() for i in data.strip().split("\n")]

binary_instructions = []

for line in data:
    if line[0] in ["addi", "li"]:
        binary_instructions.append(I(line))
    elif line[0] in ["add"]:
        binary_instructions.append(R(line))
    elif line[0] in ["j"]:
        binary_instructions.append(J(line))


for bin_inst in binary_instructions:
    print(bin_inst)
