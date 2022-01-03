import numpy
import random
import time

sbox = (4, 2, 5, 8, 
	11, 12, 10, 9, 
	3, 0, 6, 1, 
	7, 15, 13, 14)

bits = 4
size = 2**bits

round_number = 5

pbox = [1, 6, 0, 7, 2, 3, 5, 4]
pbox_rev = [2, 0, 4, 5, 7, 6, 1, 3]

key_list = []

def encrypt(text):
	for r in range(round_number):
		text = text ^ key_list[r]
		text = sbox[text]
	return text ^ key_list[-1]

def get_ddt():
	ddt = numpy.zeros((size, size))
	for i in range(size):
		for j in range(size):
			d_input = i ^ j
			d_output = sbox[i] ^ sbox[j]
			ddt[d_input, d_output] += 1
	return ddt

def get_max_proba(ddt):
	best_doutput = []
	for i in range(ddt.shape[0]):
		m = 0
		m_index = 0

		for j in range(ddt.shape[1]):
			if ddt[i, j] >= m:
				m_index = j
				m = ddt[i, j]
		best_doutput.append(m_index)

	best_path = [0] * (round_number+1)
	max_proba = 0

	for i in range(1, ddt.shape[0]):
		dinput = i
		proba = 1

		path = [0] * (round_number+1)

		for r in range(round_number):
			doutput = best_doutput[dinput]

			proba *= ddt[dinput, doutput]/size
			path[r] = dinput

			dinput = doutput

		path[-1] = dinput
		if proba >= max_proba:
			max_proba = proba
			best_path = path

	return max_proba, best_path

def get_one_charac_data(d_input, d_output):
	in_char = []
	out_char = []
	for i in range(size):
		j = i ^ d_input

		out_i = sbox[i]
		out_j = sbox[j]
		if out_j ^ out_i == d_output:
			in_char.append(i)
			out_char.append(out_i)
	
	return {'input differential': in_char, 'output differential': out_char}

def get_charac_data(best_path):
	charac_data = []
	for i in range(len(best_path) - 1):
		d_input = best_path[i]
		d_output = best_path[i+1]
		charac_data.append(get_one_charac_data(d_input, d_output))
	return charac_data

def find_good_pair(d_input, d_output, n=1):
	good_pair = []

	for i in range(size):
		# manipuler user pour encrypt les data qu'on veut
		j = i ^ d_input
		encrypt_i = encrypt(i)
		encrypt_j = encrypt(j)

		if encrypt_i ^ encrypt_j == d_output:
			good_pair.append([i, encrypt_i])
			good_pair.append([j, encrypt_j])
			if len(good_pair) >= n:
				break
			
	
	return good_pair

def get_sample(amount):
	sample = []
	for i in range(amount):
		text = random.randint(0, size-1)
		cipher = encrypt(text)
		sample.append({"known text": text, "known cipher": cipher})

	return sample

def test_keys(test_key_list, sample):
	for i in range(len(sample)):
		text = sample[i]['known text']

		for r in range(round_number):
			text = text ^ test_key_list[r]
			text = sbox[text]
		cipher = text ^ test_key_list[-1]
		if cipher != sample[i]['known cipher']:
			return False
	return True

def crack(good_pair, sample, charac_data, best_path):

	def crack_recur(round_, test_key_list, prev):
		if round_ == round_number:
			test_last_key = prev ^ good_pair[1]
			test_key_list[-1] = test_last_key

			if test_keys(test_key_list, sample):
				return test_key_list
			return None

		for i in range(len(charac_data[round_]['input differential'])):

			input_text = charac_data[round_]['input differential'][i]
			output_text = charac_data[round_]['output differential'][i]

			test_key = prev ^ input_text
			test_key_list[round_] = test_key


			result = crack_recur(round_ + 1, test_key_list, output_text)
			if result is not None:
				return result
		return None

	return crack_recur(0, [0] * (round_number+1), good_pair[0])

ddt = get_ddt()
print(ddt)
max_proba, best_path = get_max_proba(ddt)
charac_data = get_charac_data(best_path)
for r in range(len(charac_data)):
	print(len(charac_data[r]['input differential']))
print(best_path, max_proba)
total = 100
success = 0
n_pair = 1
for i in range(total):
	key_list = []
	for r in range(round_number + 1):
		key_list.append(random.randint(0, size-1))
	good_pair = find_good_pair(best_path[0], best_path[-1], n_pair)
	sample = get_sample(10)
	if good_pair is None:
		continue
	#cracktime = time.time()
	for L in good_pair:
		result = crack(L, sample, charac_data, best_path)
		if result is not None:
			if result == key_list:
				success += 1
				break
	#print("Crack time:", time.time() - cracktime)
print(success/total)
