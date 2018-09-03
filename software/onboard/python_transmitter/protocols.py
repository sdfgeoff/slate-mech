import packet_formats

class ConnectionHandler:
	latest_packets = {}

	def __init__(self, connection):
		self.connection = connection

	def send_packet(self, packet):
		"""Sends a packet of type packet_type"""
		self.connection.send_packet(packet.id_byte + packet.serialize())

	def get_latest_packet(self, packet_type):
		"""Returns the most recent packet of the packet type, along with some
		metadata about the packet (eg time to receive)"""
		return self.latest_packets.get(packet_type.id_byte)


	def handle_packet(self, packet):
		packet_type = chr(packet[0]).encode('ascii')
		if packet_type in packet_formats.PACKET_TYPES:
			if packet_type not in self.latest_packets:
				packet_instance = packet_formats.PACKET_TYPES[packet_type]()
				self.latest_packets[packet_type] = packet_instance
			self.latest_packets[packet_type].deserialize(packet[1:])
		else:
			print("Unknown Packet Type:", packet_type)


	def update(self):
		packet = self.connection.get_latest_packet()
		while packet is not None:
			self.handle_packet(packet)
			packet = self.connection.get_latest_packet()

