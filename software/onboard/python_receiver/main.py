import protocols
import connection
import packet_formats
import time
import machine
import gc
import math


LOOP_TIME_US = 16000  # ~ 60Hz


def print_loop_time():
	prev_time = time.ticks_ms()
	counter = 0
	while(1):
		cur_time = time.ticks_ms()
		counter += 1
		delta = cur_time - prev_time
		if delta > 1000:
			prev_time = cur_time
			print("Loop rate:", (1000 / delta) * counter)
			counter = 0
		yield 1


def heartbeat():
	led = machine.PWM(machine.Pin(2))
	while(1):
		led.duty(int(math.sin(time.ticks_ms() / 500) * 300 + 300))
		yield 1


def check_for_packets(comms):

	while(1):
		comms.update()
		latest = comms.get_latest_packet(packet_formats.ControlPacket)
		if latest is not None:
			print(latest.val1, latest.val2, latest.val3, latest.val4)
		yield 1


def start():
	connection.init()
	comms = protocols.ConnectionHandler(connection)

	tasks = [
		heartbeat(),
		check_for_packets(comms),
		print_loop_time()
	]
	sleep_time = time.ticks_us()
	while(1):
		for task in tasks:
			next(task)

		gc.collect()
		sleep_time = LOOP_TIME_US - (time.ticks_us() - sleep_time)
		if sleep_time > 0:
			time.sleep_us(sleep_time)
		sleep_time = time.ticks_us()


if __name__ == "__main__":
	start()
