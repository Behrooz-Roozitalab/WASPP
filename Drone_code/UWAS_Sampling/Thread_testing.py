import threading
import time

variable1 = []
flag = 0

def task1():
	t1 = 10
	
	for i in range(100):
		global variable1
		variable1 = t1 + i
		time.sleep(1)
		
		global flag
		if flag==1:
			return

def task2():
	for i in range(10):
		global variable1
		print(variable1)
		time.sleep(2)
	
	global flag
	flag=1
		
		
t1 = threading.Thread(target=task1, name='t1')
t2 = threading.Thread(target=task2, name='t2')

t1.start()
t2.start()

t1.join()
t2.join()
