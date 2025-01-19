def b(x):
    return bin(x)[2:]

with open("main.asm", "r") as f:
    data = f.read()

while "\n\n" in data:
    data.replace("\n\n", "\n")

data = data.split()

instructions = {
    "MOV": 1,
    "MOVR": 2,
    "DISPLAY": 3,
    "ADD": 4,   
    "JMP": 5
}

i = 0
while i < len(data):
    if data[i] == "JMP" or data[i] == "DISPLAY":
        data.insert(i+2, "0")
    if data[i] == "ADD":
        for j in range(i+3, i+6):
            data.insert(j, "0")
    if data[i] in instructions:
        data[i] = instructions[data[i]]
    else:
        if data[i].isdigit():
            data[i] = int(data[i])
            if data[i-1] == instructions["JMP"]:
                data[i] = (data[i] + 1)
        else:
            data[i] = 63 - int(data[i][1]) # R'0' -> 111111
            
            if data[i-1] == instructions["MOV"]:
                data[i-1] = instructions["MOVR"]
    i += 1

# data = ''.join(data)
data = [0, 0] + data
data[7] = 1
print(data)
result = ""
for i in data:
    result += chr(i+64)


with open("main.bin", "w") as f:
    f.write(result)
