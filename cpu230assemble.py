#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

# Author 1: Altay Acar
# Author 1's ID: 2018400084
# Author 2: Engin Oğuzhan Şenol
# Author 2's ID: 2020400324

import sys
import re
import string

# Checks if the given input s is a hex value or not
def is_hex(s):
     hex_digits = set(string.hexdigits)
     return all(c in hex_digits for c in s)

def is_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

f = open(sys.argv[1], "r")	# Input file

filename = f.name
filename = filename[0:-3]
filename = filename + "bin"
o = open(filename, "w")	# Produces an output file with the same name as input file in .bin format

# Stores every register and instruction's corresponding hex codes
data = {
	'PC': 0x0000,
	'A': 0x0001,
	'B': 0x0002,
	'C': 0x0003,
	'D': 0x0004,
	'E': 0x0005,
	'S': 0x0006,
	'HALT': 0x1,
	'LOAD': 0x2,
	'STORE': 0x3,
	'ADD': 0x4,
	'SUB': 0x5,
	'INC': 0x6,
	'DEC': 0x7,
	'XOR': 0x8,
	'AND': 0x9,
	'OR': 0xA,
	'NOT': 0xB,
	'SHL': 0xC,
	'SHR': 0xD,
	'NOP': 0xE,
	'PUSH': 0xF,
	'POP': 0x10,
	'CMP': 0x11,
	'JMP': 0x12,
	'JZ': 0x13,
	'JE': 0x13,
	'JNZ': 0x14,
	'JNE': 0x14,
	'JC': 0x15,
	'JNC': 0x16,
	'JA': 0x17,
	'JAE': 0x18,
	'JB': 0x19,
	'JBE': 0x1A,
	'READ': 0x1B,
	'PRINT': 0x1C,
}

labels = {}	# Stores the key:value pairs of label and the address that label points out
lines = []	# Stores every line in the input file
commands = []	# Stores every tokenized line

# Tokenization process
for line in f:
	line = line.strip()
	lines.append(line)
	words = line.split(" ")
	commands.append(words)

f.close()

count = 0 	# Counts the amount of labels
check_labels = [] # Stores every defined label name in order to check error of multiple defined labels

lines = list(filter(None, lines))	# Removes empty lines from the input lines

# Finds every label's corresponding address that it points out and stores them in labels dictionary
for i in range(len(lines)):
	found = re.search(r':', lines[i])
	if found:
		memh = hex(3*(i-count))
		temp = lines[i]
		temp = temp.replace(":", "")
		check_labels.append(temp)
		labels[temp] = memh
		count += 1
	else:
		pass

# Checks if there are duplicate labels defined in the input asm file
if len(check_labels) != len(set(check_labels)):
	# ERROR: Duplicate labels are defined
	print("SYNTAX ERROR: Duplicate labels are not allowed!\n\t    | No output bin file generated!")
	sys.exit()

# Reads every tokenized line and produces their corresponding binary encryption
for line in commands:

	opcode = -1
	addrmode = -1
	operand = -1

	if len(line) == 2:
		# Enters here if the command line consists of two tokens
		opcode = hex(data[line[0]])
		found11 = re.search("\[....\]", line[1])	# Checks if it is a memory address
		foundascii = re.search("\'.\'", line[1])	# Checks if it is an ASCII character
		# Below if blocks check if it is a register name
		if line[1] == "PC":
			# Operand is given in the register
			addrmode = int("1", 16)
			operand = hex(data[line[1]])	#hex
		elif line[1] == "A":
			# Operand is given in the register
			addrmode = int("1", 16)
			operand = hex(data[line[1]])	#hex
		elif line[1] == "B":
			# Operand is given in the register
			addrmode = int("1", 16)
			operand = hex(data[line[1]])	#hex
		elif line[1] == "C":
			# Operand is given in the register
			addrmode = int("1", 16)
			operand = hex(data[line[1]])	#hex
		elif line[1] == "D":
			# Operand is given in the register
			addrmode = int("1", 16)
			operand = hex(data[line[1]])	#hex
		elif line[1] == "E":
			# Operand is given in the register
			addrmode = int("1", 16)
			operand = hex(data[line[1]])	#hex
		elif line[1] == "S":
			# Operand is given in the register
			addrmode = int("1", 16)
			operand = hex(data[line[1]])	#hex
		# Below if blocks check if it is a memory address stored in a register
		elif line[1] == "[PC]":
			# Operand’s memory address is given in the register
			addrmode = int("2", 16)
			temp = line[1]
			temp = temp.replace("[", "")
			temp = temp.replace("]", "")
			operand = hex(data[temp])	#hex
		elif line[1] == "[A]":
			# Operand’s memory address is given in the register
			addrmode = int("2", 16)
			temp = line[1]
			temp = temp.replace("[", "")
			temp = temp.replace("]", "")
			operand = hex(data[temp])	#hex
		elif line[1] == "[B]":
			# Operand’s memory address is given in the register
			addrmode = int("2", 16)
			temp = line[1]
			temp = temp.replace("[", "")
			temp = temp.replace("]", "")
			operand = hex(data[temp])	#hex
		elif line[1] == "[C]":
			# Operand’s memory address is given in the register
			addrmode = int("2", 16)
			temp = line[1]
			temp = temp.replace("[", "")
			temp = temp.replace("]", "")
			operand = hex(data[temp])	#hex
		elif line[1] == "[D]":
			# Operand’s memory address is given in the register
			addrmode = int("2", 16)
			temp = line[1]
			temp = temp.replace("[", "")
			temp = temp.replace("]", "")
			operand = hex(data[temp])	#hex
		elif line[1] == "[E]":
			# Operand’s memory address is given in the register
			addrmode = int("2", 16)
			temp = line[1]
			temp = temp.replace("[", "")
			temp = temp.replace("]", "")
			operand = hex(data[temp])	#hex
		elif line[1] == "[S]":
			# Operand’s memory address is given in the register
			addrmode = int("2", 16)
			temp = line[1]
			temp = temp.replace("[", "")
			temp = temp.replace("]", "")
			operand = hex(data[temp])	#hex
		elif is_hex(line[1]):
			# Operand is immediate data
			addrmode = int("0", 16)
			temp = line[1]
			temp2 = int(temp, base=16)
			operand = hex(temp2)	#hex
		elif foundascii:
			# Operand is immediate data and an ascii character
			addrmode = int("0", 16)
			temp = line[1]
			res = temp.replace("'", "")
			operand = hex(ord(res))	#hex
		elif found11:
			# Operand is a memory address
			addrmode = int("3", 16)
			temp = line[1]
			temp = temp.replace("[", "")
			temp = temp.replace("]", "")
			temp2 = "0x" + temp
			bex2 = int(temp2, base=16)
			operand = hex(bex2)	#hex
		else:
			# Operand is a labeled variable
			addrmode = int("0", 16)
			operand = labels[line[1]]	#hex
	elif len(line) == 1:
		# Enters here if the command line consists of one token (either HALT or NOP operation)
		if line[0] == "HALT":
			# Instruction is a HALT operation
			opcode = hex(data[line[0]])
			addrmode = int("0", 16)
			operand = hex(0)
		elif line[0] == "NOP":
			# Instruction is a NOP operation
			opcode = hex(data[line[0]])
			addrmode = int("0", 16)
			operand = hex(0)
		else:
			pass
	else:
		# ERROR Syntax error, only one token or two tokens sized instructions are allowed
		print("SYNTAX ERROR: Only one or two tokens sized instructions allowed!\n\t    | No output bin file generated!")
		sys.exit()	# No output bin file generated

	# Converts the assembly instruction line into corresponding format for bin output file
	if opcode != -1 and addrmode != -1 and operand != -1:
		iopcode = int(opcode, 16)
		ioperand = int(operand, 16)
		bopcode = format(iopcode, '06b')
		baddrmode = format(addrmode, '02b') 
		boperand = format(ioperand, '016b') 
		bin = '0b' + bopcode + baddrmode + boperand 
		ibin = int(bin[2:],2) ; 
		instr = format(ibin, '06x')
		instr = instr.upper()
		o.write(instr + "\n")

o.close()




