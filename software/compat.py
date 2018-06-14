"""Handles differences between micropython and regular python as far
as module-names go, and provides a way to check if it's micropython or not.

Hopefully nothing more serious will come up.
"""
try:
	import socket
	import time
	import io
	import collections
	import struct
	micro = False
except:
	import usocket as socket
	import utime as time
	import uio as io
	import ucollections as collections
	import ustruct as struct
	micro = True
