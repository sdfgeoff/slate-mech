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
		return self.latest_packets[packet[0]]


	def handle_packet(self, packet):
		if packet[0] in packet_formats.PACKET_TYPES:
			if packet[0] not in self.latest_packets:
				packet_type = packet_formats.PACKET_TYPES[packet[0]]()
				self.latest_packets[packet[0]] = packet_type
			self.latest_packets[packet[0]].deserialize(packet[1:])


	def update(self):
		packet = self.connection.get_latest_packet()
		while packet is not None:
			handle_packet(packet)
			packet = self.connection.get_latest_packet()

