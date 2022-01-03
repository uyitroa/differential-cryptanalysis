import numpy
import random

sbox = (4, 2, 5, 8, 
	11, 12, 10, 9, 
	3, 0, 6, 1, 
	7, 15, 13, 14)

sbox_rev = (9, 11, 1, 8, 
	    0, 2, 10, 12, 
	    3, 7, 6, 4, 
	    5, 14, 15, 13)

pbox = (15, 13, 6, 12, 1, 14, 3, 0, 11, 8, 7, 2, 4, 5, 9, 10)
pbox_rev = (7, 4, 11, 6, 12, 13, 2, 10, 9, 14, 15, 8, 3, 1, 5, 0)

BITS = 16
SIZE = 2**BITS

key_list = []
ROUNDS = 3

def split_sbox(input_, s_box):
	mask0 = 0xF000 # 1111 0000 0000 0000
	mask1 = 0x0F00 # 0000 1111 0000 0000
	mask2 = 0x00F0 # 0000 0000 1111 0000
	mask3 = 0x000F # 0000 0000 0000 1111

	input0 = (input_ & mask0) >> 12
	input1 = (input_ & mask1) >> 8
	input2 = (input_ & mask2) >> 4
	input3 = input_ & mask3

	sinput0 = s_box[input0]
	sinput1 = s_box[input1]
	sinput2 = s_box[input2]
	sinput3 = s_box[input3]

	sinput = (sinput0 << 12) + (sinput1 << 8) + (sinput2 << 4) + sinput3

	return sinput

def permute(input_, p_box):
	binary = '{0:016b}'.format(input_)
	per_binary = ['0'] * len(binary)

	for i in range(len(binary)):
		sub_i = p_box[i]
		per_binary[sub_i] = binary[i]
	
	output_binary = ''.join(per_binary)
	return int(output_binary, 2)

def sp_box(input_):
	sub_input = split_sbox(input_, sbox)
	per_input = permute(sub_input, pbox)
	return per_input

def sp_box_rev(input_):
	per_input_rev = permute(input_, pbox_rev)
	sub_input_rev = split_sbox(per_input_rev, sbox_rev)
	return sub_input_rev

def encrypt(text):
	for r in range(ROUNDS-1):
		text = text ^ key_list[r]
		text = sp_box(text)

	text = split_sbox(text ^ key_list[ROUNDS-1], sbox)
	return text ^ key_list[ROUNDS]

def encrypt_print(text, text1):
	print(hex(text ^ text1))
	for r in range(ROUNDS-1):
		text = text ^ key_list[r]
		text1 = text1 ^ key_list[r]

		text = split_sbox(text, sbox)
		text1 = split_sbox(text1, sbox)

		print("s-box:", hex(text ^ text1))
		
		text = permute(text, pbox)
		text1 = permute(text1, pbox)

		print("p-box", hex(text ^ text1))

	text = split_sbox(text ^ key_list[ROUNDS-1], sbox)
	text1 = split_sbox(text1 ^ key_list[ROUNDS-1], sbox)

	print(hex(text ^ text1))
	return text ^ key_list[-1]

def find_good_pairs(d_input, d_output, n=1):
	good_pairs = []

	for i in range(SIZE):
		# manipuler user pour encrypt les data qu'on veut
		j = i ^ d_input
		encrypt_i = encrypt(i)
		encrypt_j = encrypt(j)

		if encrypt_i ^ encrypt_j == d_output:
			good_pairs.append({"P0" : i, "P1" : j, "C0" : encrypt_i, "C1" : encrypt_j})
			if len(good_pairs) >= n:
				break
			
	return good_pairs

def crack_last_key(good_pairs, expected_diff, mask=0xF, shiftbit=0, keybits=4):
	
	expected_diff = (expected_diff & mask) >> shiftbit

	max_match_pair = 0
	best_keys = []

	for k in range(2**keybits):
		match_pair = 0
		for pair in good_pairs:
			im_bit0 = (pair["C0"] & mask) >> shiftbit
			im_bit1 = (pair["C1"] & mask) >> shiftbit

			actual_diff = split_sbox(im_bit0 ^ k, sbox_rev) ^ split_sbox(im_bit1 ^ k, sbox_rev)
			if actual_diff == expected_diff:
				match_pair += 1

		if match_pair > max_match_pair:
			best_keys = [k]
			max_match_pair = match_pair
		elif match_pair == max_match_pair:
			best_keys.append(k)
	
	return best_keys


def crack_last_key2(good_pairs, expected_diff, mask=0xF, shiftbit=0):
	expected_diff = (expected_diff & mask) >> shiftbit

	max_match_pair = 0
	best_keys = []

	for k in range(2**8):
		match_pair = 0
		for pair in good_pairs:
			im_bit0 = (pair["C0"] & mask) >> shiftbit
			im_bit1 = (pair["C1"] & mask) >> shiftbit

			im_bit0_left = (im_bit0 & 0xF0) >> 4
			im_bit0_right = im_bit0 & 0x0F

			im_bit1_left = (im_bit1 & 0xF0) >> 4
			im_bit1_right = im_bit1 & 0x0F

			k_left = (k & 0xF0) >> 4
			k_right = k & 0x0F

			diff_left = sbox_rev[im_bit0_left ^ k_left] ^ sbox_rev[im_bit1_left ^ k_left]
			diff_right = sbox_rev[im_bit0_right ^ k_right] ^ sbox_rev[im_bit1_right ^ k_right]

			actual_diff = (diff_left << 4) + diff_right
			if actual_diff == expected_diff:
				match_pair +=1

		if match_pair > max_match_pair:
			best_keys = [k]
			max_match_pair = match_pair
		elif match_pair == max_match_pair:
			best_keys.append(k)
	
	return best_keys

key_list = []
for r in range(ROUNDS + 1):
	key_list.append(random.randint(0, SIZE-1))


diff_trail0 = [0x0100, 0x9000, 0x0004, 0x000F]
good_pairs = find_good_pairs(diff_trail0[0], diff_trail0[-1], 20)
last_key_bit0_list = crack_last_key(good_pairs, diff_trail0[-2], mask=0x000F, shiftbit=0, keybits=4)

diff_trail1 = [0x0030, 0x0100, 0x9000, 0x4000]
good_pairs = find_good_pairs(diff_trail1[0], diff_trail1[-1], 20)
last_key_bit1_list = crack_last_key(good_pairs, diff_trail1[-2], mask=0xF000, shiftbit=12, keybits=4)

diff_trail2 = [0x9000, 0x0008, 0x0460, 0x0EE0]
good_pairs = find_good_pairs(diff_trail2[0], diff_trail2[-1], 20)
last_key_bit2_list = crack_last_key2(good_pairs, diff_trail2[-2], mask=0x0FF0, shiftbit=4)

