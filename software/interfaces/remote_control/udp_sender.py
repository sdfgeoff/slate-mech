"""Exposes robot control over network for json encoded packets. Each
packet should be ended by a newline eg:

{
	"velocity":[0, 0],
	"rotation":0,
	"elevation_delta":0,
	"fire":false
}
"""

from interfaces.remote_control.abstract import RemoteControlRecieverAbstract



class RemoteControlSender():
	pass
