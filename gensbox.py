import itertools
import random
import numpy

bits = 4
size = 2**bits
round_number = 5
def get_ddt(sbox):
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
                        if ddt[i, j] >= m and i != j:
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
                        if dinput in path:
                                proba = 0
                                break

                        proba *= ddt[dinput, doutput]/size
                        path[r] = dinput

                        dinput = doutput

                path[-1] = dinput
                if proba >= max_proba:
                        max_proba = proba
                        best_path = path

        return max_proba

def fixed_point(sbox):
	count = 0
	for i in range(len(sbox)):
		if sbox[i] == i:
			count += 1

		if count >= 3:
			return True
	return False

L = [i for i in range(16)]
while True:
	count = 0
	random.shuffle(L)
	M = 0
	for sbox in itertools.permutations(L):
		if fixed_point(sbox):
			continue

		ddt = get_ddt(sbox)

		prob = get_max_proba(ddt)
		if prob>=M:
			M = prob
			print(M, sbox)
		count += 1
		if count >= 50000:
			break
