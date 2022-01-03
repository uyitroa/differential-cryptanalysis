import time

test_list = []
starttime = time.time()
for i in range(64 * 64 * 96 * 3 * 50):
	test_list = test_list + [i]
	if i % 1000:
		test_list = []
print(starttime - time.time())

test_list = [0] * 1000
starttime = time.time()
for i in range(64 * 64 * 96 * 3 * 50):
	test_list[i%1000] = i
print(starttime - time.time())
