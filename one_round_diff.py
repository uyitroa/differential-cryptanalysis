import numpy as np
import random

sbox = [3, 14, 1, 10, 4, 9, 5, 6, 8, 11, 15, 2, 13, 12, 0, 7]
sbox_rev = [14, 2, 11, 0, 4, 6, 7, 15, 8, 5, 3, 9, 13, 12, 1, 10]

bits = 4
size = 2**4

k0 = random.randint(0, 15)
k1 = random.randint(0, 15)

def encrypt(text):
	ktext = text ^ k0
	ciphertext = sbox[ktext]
	kciphertext = ciphertext ^ k1
	return kciphertext

def get_ddt():
	ddt = np.zeros((size, size))
	for i in range(size):
		for j in range(size):
			d_input = i ^ j
			d_output = sbox[i] ^ sbox[j]

			ddt [d_input, d_output] += 1
	return ddt

def get_max_proba(ddt):
	d_input, d_output = 1, 1
	max_proba = 0
	
	for i in range(1, ddt.shape[0]):
		for j in range(1, ddt.shape[1]):
			if ddt[i, j] >= ddt[d_input, d_output]:
				max_proba = ddt[i, j]
				d_input = i
				d_output = j
	
	return d_input, d_output

def get_charac_data(d_input, d_output):
	in_char = []
	out_char = []
	for i in range(size):
		j = i ^ d_input
		if sbox[i] ^ sbox[j] == d_output:
			in_char.append((i, j))
			out_char.append((sbox[i], sbox[j]))
	
	return in_char, out_char

def find_good_pair(d_input, d_output):
	sample = []
	good_pair = None

	for i in range(size):
		# manipuler user pour encrypt les data qu'on veut
		j = i ^ d_input
		encrypt_i = encrypt(i)
		encrypt_j = encrypt(j)

		if encrypt_i ^ encrypt_j == d_output and good_pair is None:
			good_pair = [i, j, encrypt_i, encrypt_j]
			return sample, good_pair
		else:
			sample.append([i, j, encrypt_i, encrypt_j])
	
	return sample, good_pair

def test_key(sample, test_k0, test_k1):
	for i in range(len(sample)):
		for j in range(2):
			ktext = sample[i][j] ^ test_k0
			ciphertext = sbox[ktext]
			kciphertext = ciphertext ^ test_k1

			if kciphertext != sample[i][2+j]:
				return False
	return True
		
def crack(good_pair, sample, in_char, out_char):
	good_in = good_pair[0]
	good_out = good_pair[2]

	for i in range(len(in_char)):
		test_k0 = in_char[i][0] ^ good_in
		test_k1 = out_char[i][0] ^ good_out
		if test_key(sample, test_k0, test_k1):
			return test_k0, test_k1

ddt = get_ddt()
print(ddt)
ddt[0, 0] = 0

d_input, d_output = get_max_proba(ddt)

in_char, out_char = get_charac_data(d_input, d_output)
sample, good_pair = find_good_pair(d_input, d_output)
print("Found key:", crack(good_pair, sample, in_char, out_char))
print("Real key:", (k0, k1))

