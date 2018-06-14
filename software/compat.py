try:
	import socket
	import time
	import io
	micro = False
except:
	print("Running on Micropython")
	import usocket as socket
	import utime as time
	import uio as io
	micro = True
