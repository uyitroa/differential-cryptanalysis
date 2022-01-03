import numpy as np

size = 16
sbox = (3, 12, 8, 7,
	4, 9, 13, 0,
	1, 5, 10, 14,
	2, 6, 11, 15)
round_number = 4

def get_ddt():
        ddt = np.zeros((size, size))
        for i in range(size):
                for j in range(size):
                        d_input = i ^ j
                        d_output = sbox[i] ^ sbox[j]

                        ddt [d_input, d_output] += 1
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

ddt = get_ddt()
print(get_max_proba(ddt))
