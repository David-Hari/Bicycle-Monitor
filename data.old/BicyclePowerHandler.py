
from struct import Struct
from ant.core import message

from data.AbstractDeviceHandler import AbstractDeviceHandler


class BicyclePowerHandler(AbstractDeviceHandler):

	messagePeriod = 8182
	deviceType = 11
	name = 'Bicycle Power'

	def __init__(self):
		super().__init__()
		self.messageStruct = Struct('<xxxxxHBB')

	def process(self, msg, channel):
		try:
			print('P', end=' - ')
			if isinstance(msg, message.ChannelBroadcastDataMessage):
				if msg.payload[1] == 0x10:
					eventCount = msg.payload[2]
					print('count = %d' % eventCount, end=', ')
					if msg.payload[3] != 0xFF:
						knowsPedal = (msg.payload[3] >> 7) == 1
						powerPercent = msg.payload[3] & 0x7F
						print('knowsPedal = %s, powerPercent = %d%%' % (knowsPedal, powerPercent), end=', ')
					if msg.payload[4] != 0xFF:
						cadence = msg.payload[4]
						print('cadence = %drpm' % cadence, end=', ')
					accumulatedPower = (msg.payload[6] << 8) | msg.payload[5]
					instantaneousPower = (msg.payload[8] << 8) | msg.payload[7]
					print('accumulatedPower = %dW, instantaneousPower = %dW' % (accumulatedPower, instantaneousPower), end='')
			print('')
		except Exception as e:
			print(e)