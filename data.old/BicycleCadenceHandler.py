
from struct import Struct
from ant.core import message

from data.AbstractDeviceHandler import AbstractDeviceHandler


class BicycleCadenceHandler(AbstractDeviceHandler):

    messagePeriod = 8102
    deviceType = 122
    name = 'Bike Cadence'

    def __init__(self):
        super().__init__()
        self.messageStruct = Struct('<xxxxxHH')

    def process(self, msg, channel):
        try:
            print('C', type(msg), end=' - ')
            if isinstance(msg, message.ChannelBroadcastDataMessage):
                time, revs = self.messageStruct.unpack(msg.payload)
                print('time = {},\trevs = {}'.format(time / 1024.0, revs))
            else:
                for byte in msg.payload:
                    print(byte, end=' ')
                print('')
        except Exception as e:
            print(e)