"""
Monitors data from ANT+ devices.
"""

import sys
import time
from ant.core import driver
from ant.core.node import Node, Network
from ant.core.exceptions import DriverError
from ant.core.constants import *

from data.HeartRateHandler import HeartRateHandler
from data.BicycleCadenceHandler import BicycleCadenceHandler
from data.BicyclePowerHandler import BicyclePowerHandler


class AntMonitor:

    def __init__(self, key):
        self.key = key
        self.network = None
        self.antNode = None
        self.handlers = {
            BicycleCadenceHandler(),
            HeartRateHandler(),
            BicyclePowerHandler()
        }

    def start(self):
        print('Starting ANT node')
        self.antNode = Node(driver.USB2Driver())
        self.antNode.start()
        self.network = Network(self.key, 'N:ANT+')

        for handler in self.handlers:
            handler.start(self.antNode, self.network)

        print('Listening for events')

    def stop(self):
        for handler in self.handlers:
            handler.stop()
        if self.antNode:
            print('Stopping ANT')
            self.antNode.stop()

    def __enter__(self):
        return self

    def __exit__(self, exceptionType, exceptionValue, traceback):
        self.stop()


with AntMonitor(key=NETWORK_KEY_ANT_PLUS) as monitor:
    try:
        monitor.start()
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                sys.exit(0)
    except DriverError as ex:
        monitor.antNode = None
        print(ex)
