from crc import crc16
import time

# Packet-level instructions
INSTR_WRITE_REG = 0x03
INSTR_PING = 0x01

# Registers on the dynamixel xl-320
XL320_LED_COLOR = 0x19
XL320_SERVO_ID = 0x03
XL320_RETURN_DELAY = 0x05
XL320_BAUD_RATE = 0x04
XL320_BAUDS = {
	9600: 0,
	57600: 1,
	115200: 2,
	1000000: 3,
}

XL320_TORQUE_ENABLE = 0x18
XL320_GOAL_POSITION = 0x1e


class DynamixelProtocol2:
	def __init__(self, uart, max_timeout_us=6000):
		self.uart = uart
		self.max_timeout_us = max_timeout_us

	def send(self, address, instruction, parameters):
		"""Sends a packet on the bus. Waits for up to max_timeout_us for
		a response. If a response is retrieved, it returns it. Otherwise it
		returns None"""

		self.uart.read() # Clear buffer
		packet = self._build_packet(address, instruction, parameters)
		send_time = time.ticks_us()
		self.uart.write(packet)

		data = None
		buff = b''
		while time.ticks_us() < send_time + self.max_timeout_us:
			data = self.uart.read()
			if data != None:
				buff += data
				if buff.startswith(packet):
					buff = buff[len(packet):]
				if len(buff):
					return buff
		else:
			return None

	def _build_packet(self, address, instruction, parameters):
		packet = [0xFF, 0xFF, 0xFD, 0x00]
		packet.append(address)
		packet.append(len(parameters)+3 % 256)  # Packet_length_lower
		packet.append(len(parameters)+3 >> 8)  # Packet_length_higher
		packet.append(instruction)
		packet += parameters
		crc = crc16(packet)
		packet.append(crc % 256)  # crc low
		packet.append(crc >> 8)   # crc high
		return bytes(packet)

	def send_blind(self, address, instruction, parameters):
		"""Sends a message without attempting to receive. This is done
		to send messages faster"""
		self.uart.write(self._build_packet(address, instruction, parameters))


class XL320:
	def __init__(self, bus, servo_id):
		self.servo_id = servo_id
		self.bus = bus

	def ping(self):
		data = self.bus.send(
			self.servo_id, INSTR_PING,
			[]
		)
		return data != None

	def set_led(self, color):
		"""Sets the LED"""
		data = self.bus.send(
			self.servo_id, INSTR_WRITE_REG,
			(XL320_LED_COLOR, 0x00, color)
		)

	def set_baud(self, baud):
		baud_id = XL320_BAUDS[baud]
		data = self.bus.send(
			self.servo_id, INSTR_WRITE_REG,
			[XL320_BAUD_RATE, 0x00, baud_id]
		)

	def set_return_delay(self, return_delay_us):
		"""Sets how many mucroseconds the servo waits before sending it's
		reponse."""
		# TODO: debug this. It seems not to be working
		data = self.bus.send(
			self.servo_id, INSTR_WRITE_REG,
			[XL320_RETURN_DELAY, 0x00, return_delay_us//2]
		)
		print(data)

	def set_id(self, new_servo_id):
		data = self.bus.send(
			self.servo_id, INSTR_WRITE_REG,
			[XL320_SERVO_ID, 0x00, new_servo_id]
		)

	def set_enable(self, enable):
		data = self.bus.send(
			self.servo_id, INSTR_WRITE_REG,
			[XL320_TORQUE_ENABLE, 0x00, 1 if enable else 0]
		)

	def set_angle(self, angle):
		"""Sets the servo angle 1024 steps per 360 degrees.
		At some point this should be changed to degrees"""
		data = self.bus.send(
			self.servo_id, INSTR_WRITE_REG,
			[XL320_GOAL_POSITION, 0x00, angle % 256, angle >> 8]
		)




import machine
bus = DynamixelProtocol2(
	machine.UART(2, baudrate=1000000, rx=16, tx=17, timeout=0)
)


s1 = XL320(bus, 0x01)
s2 = XL320(bus, 0x02)
s3 = XL320(bus, 0x03)

#s1.set_return_delay(2)
#s2.set_return_delay(2)
#bus.set_id(0x01, 2)
s1.set_led(1)
s2.set_led(2)
s3.set_led(3)

s1.set_enable(True)
s2.set_enable(True)
s3.set_enable(True)

a = time.ticks_us()
for i in range(1000):
	s2.set_angle(i)
	s1.set_angle(1000-i)
	s3.set_angle(1000-i)
b = time.ticks_us()
delta = (b - a)/1000000
print("2000 blind messages in {} seconds".format(delta))
print("For a time of {} seconds per message".format(delta/2000))
print("Or settings all 14 servos at a rate of {} Hz".format(1/(delta/2000 * 14)))
