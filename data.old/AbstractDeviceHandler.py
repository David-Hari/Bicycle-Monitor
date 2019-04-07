"""
Base class for handling data from ANT devices.
"""

from ant.core.constants import *


class AbstractDeviceHandler(object):

	rfChannel = 57
	messagePeriod = 0
	deviceType = 0
	name = 'Ant Channel'

	def __init__(self):
		self.channel = None

	def start(self, antNode, network):
		print('Starting ', self.name)  # TODO: Log instead of print
		self.channel = antNode.getFreeChannel()
		self.channel.name = self.name
		self.channel.assign(network, CHANNEL_TYPE_TWOWAY_RECEIVE)
		self.channel.setID(devType = self.deviceType, devNum = 0, transType = 0)
		self.channel.searchTimeout = TIMEOUT_NEVER
		self.channel.frequency = self.rfChannel
		self.channel.period = self.messagePeriod
		self.channel.open()
		self.channel.registerCallback(self)

	def stop(self):
		if self.channel:
			print('Closing channel ', self.name)
			self.channel.close()
			self.channel.unassign()

	def process(self, msg, channel):
		raise NotImplementedError()