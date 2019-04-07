
from struct import Struct
from ant.core import message

from data.AbstractDeviceHandler import AbstractDeviceHandler


class HeartRateHandler(AbstractDeviceHandler):

    messagePeriod = 8070
    deviceType = 120
    name = 'Heart Rate'

    def __init__(self):
        super().__init__()
        self.messageStruct = Struct('<xxxxxHBB')

    def process(self, msg, channel):
        try:
            print('H', type(msg), end=' - ')
            if isinstance(msg, message.ChannelBroadcastDataMessage):
                time, beatCount, heartRate = self.messageStruct.unpack(msg.payload)
                print('time = {},\tcount = {},\trate = {}'.format(time, beatCount, heartRate))
            else:
                for byte in msg.payload:
                    print(byte, end=' ')
                print('')
        except Exception as e:
            print(e)