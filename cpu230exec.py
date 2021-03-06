#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

# Author 1: Altay Acar
# Author 1's ID: 2018400084
# Author 2: Engin Oğuzhan Şenol
# Author 2's ID: 2020400324

import sys
import re
import string

# registers dictionary stores the name of the register as key and the value that register holds as value as value in key:value pair
registers = {
	"A": 0x0,
	"B": 0x0,
	"C": 0x0,
	"D": 0x0,
	"E": 0x0,
	"PC": 0x0,	# program counter points the start of the memory
	"S": 0xfffe	# stack pointer points the end of the memory
}

# Matches every register with their corresponding number
find_reg = {
	0: "PC",
	1: "A",
	2: "B",
	3: "C",
	4: "D",
	5: "E",
	6: "S"
}

# flags dictionary stores the name of the flag as key and the state of the flag (0 or 1) as value in key:value pair
flags = {
	"ZF": 0,
	"CF": 0,
	"SF": 0
}

# memory dictionary uses memory addresses as keys to point value in 1 byte
memory = {}

L = 65536
for i in range(L):
	memory[i] = '00000000'

f = open(sys.argv[1], "r")	# input file "<filename>.bin"
filename = f.name
filename = filename[0:-3]
filename = filename + "txt"
o = open(filename, "w")

found_halt = 0
# puts every byte into one memory cell
memcounter = 0
for line in f:
	instr = int(line, 16)
	binstr = bin(instr)[2:].zfill(24)
	if "000001000000000000000000" in binstr:
		found_halt = 1
	byte1 = binstr[0:8]
	byte2 = binstr[8:16]
	byte3 = binstr[16:24]
	memory[memcounter] = byte1
	memcounter += 1
	memory[memcounter] = byte2
	memcounter += 1
	memory[memcounter] = byte3
	memcounter += 1

f.close()

# Checks if the memory limit is exceeded
if (len(memory) > 65536):
	# ERROR: memory limit is not enough for given instructions
	print("ERROR: Memory limit exceeded!\n     | No output txt file generated!")
	sys.exit()

# Checks if the instructions contain HALT instruction to stop program
if not found_halt:
	# ERROR There is no HALT instruction to stop the program, it enters infinite loop
	print("ERROR: No HALT operation found!\n     | No output txt file generated!")
	sys.exit()

# Converts a 16-bit value to corresponding two bytes in integer values
def div_two(val):
	dval = int(val)
	bval = bin(dval)[2:].zfill(16)
	ibyte0 = bval[0:8]
	ibyte1 = bval[8:16]
	byte0 = "0b" + ibyte0
	byte1 = "0b" + ibyte1
	adr0 = int(byte0, 0)	# First 8-bit's corresponding value
	adr1 = int(byte1, 0)	# Last 8-bit's corresponding value
	res = [adr0, adr1]
	return res

# Converts a memory address and its subsequent address' byte values into one integer value
def take_val_from_mem(adr):
	ival0 = memory[adr]
	ival1 = memory[adr+1]
	dval0 = int(ival0)
	dval1 = int(ival1)
	bval0 = bin(dval0)[2:].zfill(8)
	bval1 = bin(dval1)[2:].zfill(8)
	bval = "0b" + bval0 + bval1
	val = int(bval, 0)	# Final value of given address' and its next address' bytes combined
	return val

# Takes two integer values and adds them. Flags are set accordingly
def add_opr(val0, val1):
	dsum = val0 + val1
	bsum = bin(dsum)[2:].zfill(17)
	carry_bit = bsum[0]
	sign_bit = bsum[1]
	res = bsum[1:]
	bres = "0b" + res
	val = int(bres, 0)
	if (val == 0):
		flags["ZF"] = 1
	else:
		flags["ZF"] = 0
	if carry_bit == "1":
		flags["CF"] = 1
	else:
		flags["CF"] = 0
	if sign_bit == "1":
		flags["SF"] = 1
	else:
		flags["SF"] = 0
	return val

# Takes an integer value and returns its complement. Flags are set accordingly
def not_opr(val):
	z = val
	flags["ZF"] = 0
	bin_z = bin(z)[2:].zfill(16)
	inv_z = ""
	for i in bin_z:
		if i == "0":
			inv_z += "1"
		else:
			inv_z += "0"
	sign_bit = inv_z[0]
	if sign_bit == "1":
		flags["SF"] = 1
	else:
		flags["SF"] = 0
	inv_bin_z = "0b" + inv_z
	inv_dec_z = int(inv_bin_z, 0)
	if inv_dec_z == 0:
		flags["ZF"] = 1
	else:
		flags["ZF"] = 0
	return inv_dec_z

# Takes a hex value and shifts its binary form's bits one position to the left. Flags are set accordingly
def shl_opr(val):
	dval = int(val)
	shifted_res = dval << 1
	bres = bin(shifted_res)[2:].zfill(17)
	carry_bit = bres[0]
	sign_bit = bres[1]
	res = bres[1:]
	bin_res = "0b" + res
	dres = int(bin_res, 0)
	if (dres == 0):
		flags["ZF"] = 1
	else:
		flags["ZF"] = 0
	if carry_bit == "1":
		flags["CF"] = 1
	else:
		flags["CF"] = 0
	if sign_bit == "1":
		flags["SF"] = 1
	else:
		flags["SF"] = 0
	return dres

# Takes a hex value and shifts its binary form's bits one position to the right. Flags are set accordingly
def shr_opr(val):
	dval = int(val)
	shifted_res = dval >> 1
	bres = bin(shifted_res)[2:].zfill(16)
	sign_bit = bres[0]
	bin_res = "0b" + bres
	dres = int(bin_res, 0)
	if (dres == 0):
		flags["ZF"] = 1
	else:
		flags["ZF"] = 0
	if sign_bit == "1":
		flags["SF"] = 1
	else:
		flags["SF"] = 0
	return dres

execute = 1
cmp_above = 0


# Executes the instructions until HALT instruction is executed.
while execute:

	byte0 = memory[registers["PC"]]
	registers["PC"] += 1
	byte1 = memory[registers["PC"]]
	registers["PC"] += 1
	byte2 = memory[registers["PC"]]
	registers["PC"] += 1

	bopcode = "0b" + byte0[0:6]
	badrmode = "0b" + byte0[6:]
	boperand = "0b" + byte1 + byte2

	opcode = int(bopcode, 0)
	adrmode = int(badrmode, 0)
	operand = int(boperand, 0)

	if opcode == 0x1:
		# HALT operation will be executed
		execute = 0
		cmp_above = 0
		break;

	elif opcode == 0x2:
		# LOAD operation will be executed
		if adrmode == 0x0:
			# Operand is an immediate data
			registers["A"] = operand
			cmp_above = 0
		elif adrmode == 0x1:
			# Operand is given in register
			reg = find_reg[operand]
			opr = registers[reg]
			registers["A"] = opr
			cmp_above = 0
		elif adrmode == 0x2:
			# Operand's memory address is given in register
			reg = find_reg[operand]
			adr = registers[reg]
			opr = take_val_from_mem(adr)
			registers["A"] = opr
			cmp_above = 0
		elif adrmode == 0x3:
			# Operand is a memory address
			opr = take_val_from_mem(operand)
			registers["A"] = opr
			cmp_above = 0
		else:
			# ERROR, only above defined addressing modes are available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0x3:
		# STORE operation will be executed
		if adrmode == 0x1:
			# Operand is given in register
			val = registers["A"]
			reg = find_reg[operand]
			registers[reg] = val
			cmp_above = 0
		elif adrmode == 0x2:
			# Operand's memory address is given in register
			val = registers["A"]
			val_list = div_two(val)
			val0 = val_list[0]
			val1 = val_list[1]
			reg = find_reg[operand]
			adr = registers[reg]
			memory[adr] = val0
			memory[adr+1] = val1
			cmp_above = 0
		elif adrmode == 0x3:
			# Operand is a memory address
			val = registers["A"]
			val_list = div_two(val)
			val0 = val_list[0]
			val1 = val_list[1]
			memory[operand] = val0
			memory[operand+1] = val1
			cmp_above = 0
		else:
			# ERROR, only above defined addressing modes are available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0x4:
		# ADD operation will be executed
		if adrmode == 0x0:
			# Operand is an immediate data
			a_val = registers["A"]
			res = add_opr(a_val, operand)
			registers["A"] = res
			cmp_above = 0
		elif adrmode == 0x1:
			# Operand is given in register
			reg = find_reg[operand]
			val0 = registers["A"]
			val1 = registers[reg]
			res = add_opr(val0, val1)
			registers["A"] = res
			cmp_above = 0
		elif adrmode == 0x2:
			# Operand's memory address is given in register
			reg = find_reg[operand]
			adr = registers[reg]
			opr = take_val_from_mem(adr)
			a_val = registers["A"]
			res = add_opr(opr, a_val)
			registers["A"] = res
			cmp_above = 0
		elif adrmode == 0x3:
			# Operand is a memory address
			opr = take_val_from_mem(operand)
			a_val = registers["A"]
			res = add_opr(opr, a_val)
			registers["A"] = res
			cmp_above = 0
		else:
			# ERROR, only above defined addressing modes are available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0x5:
		# SUB operation will be executed
		if adrmode == 0x0:
			# Operand is an immediate data
			a_val = registers["A"]
			nopr = not_opr(operand)
			inc_nopr = add_opr(nopr, 1)
			res = add_opr(a_val, inc_nopr)
			registers["A"] = res
			cmp_above = 0
		elif adrmode == 0x1:
			# Operand is given in register
			a_val = registers["A"]
			reg = find_reg[operand]
			opr = registers[reg]
			nopr = not_opr(opr)
			inc_nopr = add_opr(nopr, 1)
			res = add_opr(a_val, inc_nopr)
			registers["A"] = res
			cmp_above = 0
		elif adrmode == 0x2:
			# Operand's memory address is given in register
			a_val = registers["A"]
			reg = find_reg[operand]
			adr = registers[reg]
			opr = take_val_from_mem(adr)
			nopr = not_opr(opr)
			inc_nopr = add_opr(nopr, 1)
			res = add_opr(a_val, inc_nopr)
			registers["A"] = res
			cmp_above = 0
		elif adrmode == 0x3:
			# Operand is a memory address
			a_val = registers["A"]
			opr = take_val_from_mem(operand)
			nopr = not_opr(opr)
			inc_nopr = add_opr(nopr, 1)
			res = add_opr(a_val, inc_nopr)
			registers["A"] = res
			cmp_above = 0
		else:
			# ERROR, only above defined addressing modes are available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0x6:
		# INC operation will be executed
		if adrmode == 0x0:
			# Operand is an immediate data
			res = add_opr(operand, 1)
			cmp_above = 0
		elif adrmode == 0x1:
			# Operand is given in register
			reg = find_reg[operand]
			opr = registers[reg]
			res = add_opr(opr, 1)
			registers[reg] = res
			cmp_above = 0
		elif adrmode == 0x2:
			# Operand's memory address is given in register
			reg = find_reg[operand]
			adr = registers[reg]
			opr = take_val_from_mem(adr)
			res = add_opr(opr, 1)
			res_list = div_two(res)
			res0 = res_list[0]
			res1 = res_list[1]
			memory[adr] = res0
			memory[adr+1] = res1
			cmp_above = 0
		elif adrmode == 0x3:
			# Operand is a memory address
			opr = take_val_from_mem(operand)
			res = add_opr(opr, 1)
			res_list = div_two(res)
			res0 = res_list[0]
			res1 = res_list[1]
			memory[operand] = res0
			memory[operand+1] = res1
			cmp_above = 0
		else:
			# ERROR, only above defined addressing modes are available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0x7:
		# DEC operation will be executed
		if adrmode == 0x0:
			# Operand is an immediate data
			nopr = not_opr(1)
			inc_nopr = add_opr(nopr, 1)
			res = add_opr(operand, inc_nopr)
			cmp_above = 0
		elif adrmode == 0x1:
			# Operand is given in register
			reg = find_reg[operand]
			opr = registers[reg]
			nopr = not_opr(1)
			inc_nopr = add_opr(nopr, 1)
			res = add_opr(opr, inc_nopr)
			registers[reg] = res
			cmp_above = 0
		elif adrmode == 0x2:
			# Operand's memory address is given in register
			reg = find_reg[operand]
			adr = registers[reg]
			opr = take_val_from_mem(adr)
			nopr = not_opr(1)
			inc_nopr = add_opr(nopr, 1)
			res = add_opr(opr, inc_nopr)
			res_list = div_two(res)
			res0 = res_list[0]
			res1 = res_list[1]
			memory[adr] = res0
			memory[adr+1] = res1
			cmp_above = 0
		elif adrmode == 0x3:
			# Operand is a memory address
			opr = take_val_from_mem(operand)
			nopr = not_opr(1)
			inc_nopr = add_opr(nopr, 1)
			res = add_opr(opr, inc_nopr)
			res_list = div_two(res)
			res0 = res_list[0]
			res1 = res_list[1]
			memory[operand] = res0
			memory[operand+1] = res1
			cmp_above = 0
		else:
			# ERROR, only above defined addressing modes are available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0x8:
		# XOR operation will be executed
		if adrmode == 0x0:
			# Operand is an immediate data
			a_val = registers["A"]
			res = a_val ^ operand
			bres = bin(res)[2:].zfill(16)
			sign_bit = bres[0]
			if (res == 0):
				flags["ZF"] = 1
			else:
				flags["ZF"] = 0
			if sign_bit == "1":
				flags["SF"] = 1
			else:
				flags["SF"] = 0
			registers["A"] = res
			cmp_above = 0
		elif adrmode == 0x1:
			# Operand is given in register
			a_val = registers["A"]
			reg = find_reg[operand]
			opr = registers[reg]
			res = a_val ^ opr
			bres = bin(res)[2:].zfill(16)
			sign_bit = bres[0]
			if (res == 0):
				flags["ZF"] = 1
			else:
				flags["ZF"] = 0
			if sign_bit == "1":
				flags["SF"] = 1
			else:
				flags["SF"] = 0
			registers["A"] = res
			cmp_above = 0
		elif adrmode == 0x2:
			# Operand's memory address is given in register
			a_val = registers["A"]
			reg = find_reg[operand]
			adr = registers[reg]
			opr = take_val_from_mem(adr)
			res = a_val ^ opr
			bres = bin(res)[2:].zfill(16)
			sign_bit = bres[0]
			if (res == 0):
				flags["ZF"] = 1
			else:
				flags["ZF"] = 0
			if sign_bit == "1":
				flags["SF"] = 1
			else:
				flags["SF"] = 0
			registers["A"] = res
			cmp_above = 0
		elif adrmode == 0x3:
			# Operand is a memory address
			a_val = registers["A"]
			opr = take_val_from_mem(operand)
			res = a_val ^ opr
			bres = bin(res)[2:].zfill(16)
			sign_bit = bres[0]
			if (res == 0):
				flags["ZF"] = 1
			else:
				flags["ZF"] = 0
			if sign_bit == "1":
				flags["SF"] = 1
			else:
				flags["SF"] = 0
			registers["A"] = res
			cmp_above = 0
		else:
			# ERROR, only above defined addressing modes are available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0x9:
		# AND operation will be executed
		if adrmode == 0x0:
			# Operand is an immediate data
			a_val = registers["A"]
			res = a_val & operand
			bres = bin(res)[2:].zfill(16)
			sign_bit = bres[0]
			if (res == 0):
				flags["ZF"] = 1
			else:
				flags["ZF"] = 0
			if sign_bit == "1":
				flags["SF"] = 1
			else:
				flags["SF"] = 0
			registers["A"] = res
			cmp_above = 0
		elif adrmode == 0x1:
			# Operand is given in register
			a_val = registers["A"]
			reg = find_reg[operand]
			opr = registers[reg]
			res = a_val & opr
			bres = bin(res)[2:].zfill(16)
			sign_bit = bres[0]
			if (res == 0):
				flags["ZF"] = 1
			else:
				flags["ZF"] = 0
			if sign_bit == "1":
				flags["SF"] = 1
			else:
				flags["SF"] = 0
			registers["A"] = res
			cmp_above = 0
		elif adrmode == 0x2:
			# Operand's memory address is given in register
			a_val = registers["A"]
			reg = find_reg[operand]
			adr = registers[reg]
			opr = take_val_from_mem(adr)
			res = a_val & opr
			bres = bin(res)[2:].zfill(16)
			sign_bit = bres[0]
			if (res == 0):
				flags["ZF"] = 1
			else:
				flags["ZF"] = 0
			if sign_bit == "1":
				flags["SF"] = 1
			else:
				flags["SF"] = 0
			registers["A"] = res
			cmp_above = 0
		elif adrmode == 0x3:
			# Operand is a memory address
			a_val = registers["A"]
			opr = take_val_from_mem(operand)
			res = a_val & opr
			bres = bin(res)[2:].zfill(16)
			sign_bit = bres[0]
			if (res == 0):
				flags["ZF"] = 1
			else:
				flags["ZF"] = 0
			if sign_bit == "1":
				flags["SF"] = 1
			else:
				flags["SF"] = 0
			registers["A"] = res
			cmp_above = 0
		else:
			# ERROR, only above defined addressing modes are available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0xa:
		# OR operation will be executed
		if adrmode == 0x0:
			# Operand is an immediate data
			a_val = registers["A"]
			res = a_val | operand
			bres = bin(res)[2:].zfill(16)
			sign_bit = bres[0]
			if (res == 0):
				flags["ZF"] = 1
			else:
				flags["ZF"] = 0
			if sign_bit == "1":
				flags["SF"] = 1
			else:
				flags["SF"] = 0
			registers["A"] = res
			cmp_above = 0
		elif adrmode == 0x1:
			# Operand is given in register
			a_val = registers["A"]
			reg = find_reg[operand]
			opr = registers[reg]
			res = a_val | opr
			bres = bin(res)[2:].zfill(16)
			sign_bit = bres[0]
			if (res == 0):
				flags["ZF"] = 1
			else:
				flags["ZF"] = 0
			if sign_bit == "1":
				flags["SF"] = 1
			else:
				flags["SF"] = 0
			registers["A"] = res
			cmp_above = 0
		elif adrmode == 0x2:
			# Operand's memory address is given in register
			a_val = registers["A"]
			reg = find_reg[operand]
			adr = registers[reg]
			opr = take_val_from_mem(adr)
			res = a_val | opr
			bres = bin(res)[2:].zfill(16)
			sign_bit = bres[0]
			if (res == 0):
				flags["ZF"] = 1
			else:
				flags["ZF"] = 0
			if sign_bit == "1":
				flags["SF"] = 1
			else:
				flags["SF"] = 0
			registers["A"] = res
			cmp_above = 0
		elif adrmode == 0x3:
			# Operand is a memory address
			a_val = registers["A"]
			opr = take_val_from_mem(operand)
			res = a_val | opr
			res = bin(res)[2:].zfill(16)
			sign_bit = bres[0]
			if (dres == 0):
				flags["ZF"] = 1
			else:
				flags["ZF"] = 0
			if sign_bit == "1":
				flags["SF"] = 1
			else:
				flags["SF"] = 0
			registers["A"] = res
			cmp_above = 0
		else:
			# ERROR, only above defined addressing modes are available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0xb:
		# NOT operation will be executed
		if adrmode == 0x0:
			# Operand is an immediate data
			res = not_opr(operand)
			registers["A"] = res
			cmp_above = 0
		elif adrmode == 0x1:
			# Operand is given in register
			reg = find_reg[operand]
			opr = registers[reg]
			res = not_opr(opr)
			registers["A"] = res
			cmp_above = 0
		elif adrmode == 0x2:
			# Operand's memory address is given in register
			reg = find_reg[operand]
			adr = registers[reg]
			opr = take_val_from_mem(adr)
			res = not_opr(opr)
			registers["A"] = res
			cmp_above = 0
		elif adrmode == 0x3:
			# Operand is a memory address
			opr = take_val_from_mem(operand)
			res = not_opr(opr)
			registers["A"] = res
			cmp_above = 0
		else:
			# ERROR, only above defined addressing modes are available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0xc:
		# SHL operation will be executed
		if adrmode == 0x1:
			# Operand is given in register
			reg = find_reg[operand]
			opr = registers[reg]
			res = shl_opr(opr)
			registers[reg] = res
			cmp_above = 0
		else:
			# ERROR, only above defined addressing mode is available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0xd:
		# SHR operation will be executed
		if adrmode == 0x1:
			# Operand is given in register
			reg = find_reg[operand]
			opr = registers[reg]
			res = shr_opr(opr)
			registers[reg] = res
			cmp_above = 0
		else:
			# ERROR, only above defined addressing mode is available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0xe:
		# NOP operation will be executed
		cmp_above = 0
		pass

	elif opcode == 0xf:
		# PUSH operation will be executed
		if adrmode == 0x1:
			# Operand is given in register
			reg = find_reg[operand]
			opr = registers[reg]
			val_list = div_two(opr)
			val0 = val_list[0]
			val1 = val_list[1]
			stackptr = registers["S"]
			stackptr = stackptr - 2
			memory[stackptr] = val0
			memory[stackptr+1] = val1
			registers["S"] = stackptr
			cmp_above = 0
		else:
			# ERROR, only above defined addressing mode is available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0x10:
		# POP operation will be executed
		if adrmode == 0x1:
			# Operand is given in register
			stackptr = registers["S"]
			if stackptr == 0xfffe:
				# ERROR stack does not store any value but pop operation is called
				print("ERROR: Reached empty stack!\n     | No output txt file generated!")
				sys.exit()
			val = take_val_from_mem(stackptr)
			memory[stackptr] = 0x0
			memory[stackptr+1] = 0x0
			registers["S"] = stackptr + 2
			reg = find_reg[operand]
			registers[reg] = val
			cmp_above = 0
		else:
			# ERROR, only above defined addressing mode is available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0x11:
		# CMP operation will be executed
		if adrmode == 0x0:
			# Operand is an immediate data
			a_val = registers["A"]
			nopr = not_opr(operand)
			inc_nopr = add_opr(nopr, 1)
			res = add_opr(a_val, inc_nopr)
			cmp_above = 1
		elif adrmode == 0x1:
			# Operand is given in register
			a_val = registers["A"]
			reg = find_reg[operand]
			opr = registers[reg]
			nopr = not_opr(opr)
			inc_nopr = add_opr(nopr, 1)
			res = add_opr(a_val, inc_nopr)
			cmp_above = 1
		elif adrmode == 0x2:
			# Operand's memory address is given in register
			a_val = registers["A"]
			reg = find_reg[operand]
			adr = registers[reg]
			opr = take_val_from_mem(adr)
			nopr = not_opr(opr)
			inc_nopr = add_opr(nopr, 1)
			res = add_opr(a_val, inc_nopr)
			cmp_above = 1
		elif adrmode == 0x3:
			# Operand is a memory address
			a_val = registers["A"]
			opr = take_val_from_mem(operand)
			nopr = not_opr(opr)
			inc_nopr = add_opr(nopr, 1)
			res = add_opr(a_val, inc_nopr)
			cmp_above = 1
		else:
			# ERROR, only above defined addressing modes are available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0x12:
		# JMP operation will be executed
		if adrmode == 0x0:
			# Operand is an immediate data
			registers["PC"] = operand
			cmp_above = 0
		else:
			# ERROR, only above defined addressing mode is available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0x13:
		# Either JZ or JE operation will be executed
		if adrmode == 0x0:
			# Operand is an immediate data
			if flags["ZF"]:
				registers["PC"] = operand
			else:
				pass
			cmp_above = 0
		else:
			# ERROR, only above defined addressing mode is available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0x14:
		# Either JNZ or JNE operation will be executed
		if adrmode == 0x0:
			# Operand is an immediate data
			if flags["ZF"]:
				pass
			else:
				registers["PC"] = operand
			cmp_above = 0
		else:
			# ERROR, only above defined addressing mode is available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0x15:
		# JC operation will be executed
		if adrmode == 0x0:
			# Operand is an immediate data
			if flags["CF"]:
				registers["PC"] = operand
			else:
				pass
			cmp_above = 0
		else:
			# ERROR, only above defined addressing mode is available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0x16:
		# JNC operation will be executed
		if adrmode == 0x0:
			# Operand is an immediate data
			if flags["CF"]:
				pass
			else:
				registers["PC"] = operand
			cmp_above = 0
		else:
			# ERROR, only above defined addressing mode is available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0x17:
		# JA operation will be executed
		if adrmode == 0x0:
			# Operand is an immediate data
			if cmp_above:
				# There is a CMP instruction right above this instruction, so executes
				if flags["SF"]:
					pass
				else:
					registers["PC"] = operand
				cmp_above = 0
			else:
				# ERROR There must be a CMP instruction right above JA operation
				print("SYNTAX ERROR: There must be a CMP instruction right above JA operation!\n\t    | No output txt file generated!")
				sys.exit()
		else:
			# ERROR, only above defined addressing mode is available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0x18:
		# JAE operation will be executed
		if adrmode == 0x0:
			# Operand is an immediate data
			if cmp_above:
				# There is a CMP instruction right above this instruction, so executes
				if flags["ZF"] == 1 or flags["SF"] == 0:
					registers["PC"] = operand
				else:
					pass
				cmp_above = 0
			else:
				# ERROR There must be a CMP instruction right above JAE operation
				print("SYNTAX ERROR: There must be a CMP instruction right above JAE operation!\n\t    | No output txt file generated!")
				sys.exit()
		else:
			# ERROR, only above defined addressing mode is available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0x19:
		# JB operation will be executed
		if adrmode == 0x0:
			# Operand is an immediate data
			if cmp_above:
				# There is a CMP instruction right above this instruction, so executes
				if flags["SF"]:
					registers["PC"] = operand
				else:
					pass
				cmp_above = 0
			else:
				# ERROR There must be a CMP instruction right above JB operation
				print("SYNTAX ERROR: There must be a CMP instruction right above JB operation!\n\t    | No output txt file generated!")
				sys.exit()
		else:
			# ERROR, only above defined addressing mode is available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0x1a:
		# JBE operation will be executed
		if adrmode == 0x0:
			# Operand is an immediate data
			if cmp_above:
				# There is a CMP instruction right above this instruction, so executes
				if flags["ZF"] == 1 or flags["SF"] == 1:
					registers["PC"] = operand
				else:
					pass
				cmp_above = 0
			else:
				# ERROR There must be a CMP instruction right above JBE operation
				print("SYNTAX ERROR: There must be a CMP instruction right above JBE operation!\n\t    | No output txt file generated!")
				sys.exit()
		else:
			# ERROR, only above defined addressing mode is available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0x1b:
		# READ operation will be executed
		if adrmode == 0x1:
			# Operand is given in register
			char_input = input()
			ascii_input = ord(char_input)
			reg = find_reg[operand]
			registers[reg] = ascii_input
			cmp_above = 0
		elif adrmode == 0x2:
			# Operand's memory address is given in register
			char_input = input()
			ascii_input = ord(char_input)
			reg = find_reg[operand]
			adr = registers[reg]
			val_list = div_two(ascii_input)
			list0 = val_list[0]
			list1 = val_list[1]
			memory[adr] = list0
			memory[adr+1] = list1
			cmp_above = 0
		elif adrmode == 0x3:
			# Operand is a memory address
			char_input = input()
			ascii_input = ord(char_input)
			val_list = div_two(ascii_input)
			list0 = val_list[0]
			list1 = val_list[1]
			memory[operand] = list0
			memory[operand+1] = list1
			cmp_above = 0
		else:
			# ERROR, only above defined addressing modes are available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	elif opcode == 0x1c:
		# PRINT operation will be executed
		if adrmode == 0x0:
			# Operand is an immediate data
			output = chr(operand)
			o.write(output + "\n")
			cmp_above = 0
		elif adrmode == 0x1:
			# Operand is given in register
			reg = find_reg[operand]
			opr = registers[reg]
			output = chr(opr)
			o.write(output + "\n")
			cmp_above = 0
		elif adrmode == 0x2:
			# Operand's memory address is given in register
			reg = find_reg[operand]
			adr = registers[reg]
			opr = take_val_from_mem(adr)
			output = chr(opr)
			o.write(output + "\n")
			cmp_above = 0
		elif adrmode == 0x3:
			# Operand is a memory address
			opr = take_val_from_mem(operand)
			output = chr(opr)
			o.write(output + "\n")
			cmp_above = 0
		else:
			# ERROR, only above defined addressing modes are available
			print("SYNTAX ERROR: Addressing mode is corrupted!\n\t    | No output txt file generated!")
			sys.exit()

	else:
		# ERROR only operations listed above are defined to use
		print("SYNTAX ERROR: Given instruction is not recognized!\n\t    | No output txt file generated!")
		sys.exit()

o.close()