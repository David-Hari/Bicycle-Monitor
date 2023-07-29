import tkinter as tk
from PIL import Image, ImageTk

import display
import config


class MockCamera:
	def __init__(self, tkWindow):
		self.overlays = []
		self.tkWindow = tkWindow

	def start_preview(self, **options):
		pass

	def stop_preview(self):
		pass

	def add_overlay(self, imageBytes, window=None, **options):
		renderer = MockOverlay(self.tkWindow, imageBytes, window)
		self.overlays.append(renderer)
		return renderer

	def remove_overlay(self, overlay):
		self.overlays.remove(overlay)


class MockOverlay:
	def __init__(self, tkWindow, imageBytes, pos):
		self.tkWindow = tkWindow
		self.window = pos
		self.image = None
		self.imageWidget = tk.Label(tkWindow, background='grey')
		self.imageWidget.place(x=pos[0], y=pos[1], width=pos[2], height=pos[3])
		self.update(imageBytes)

	def update(self, imageBytes):
		self.image = ImageTk.PhotoImage(Image.frombytes('RGBA', self.window[2:4], imageBytes))
		self.imageWidget['image'] = self.image
		pass



gear = 1
power = 0
sd = (None, None)
messageNum = 1
root = tk.Tk()
root.title('Bicycle Display Test')
width = config.videoDisplayResolution[0]
height = config.videoDisplayResolution[1]
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry('%dx%d+%d+%d' % (width, height, (screen_width - width) / 2, (screen_height - height) / 2))
root.minsize(width, height)
root.maxsize(width, height)
root.configure(background='grey')

display.start(MockCamera(root))

def initialDisplay():
	display.drawPower(power, config.powerGoal)
	display.drawSpeedAndDistance(sd[0], sd[1])
	display.drawHeartRate(123)
	display.drawGearNumber(gear)

def changeGear(num):
	global gear
	gear += num
	display.drawGearNumber(gear, isChanging=True)
	root.after(1000, lambda: display.drawGearNumber(gear))

def changePower(num):
	global power
	power += num
	display.drawPower(power, config.powerGoal)

def changeSpeedAndDist():
	global sd
	sd = (12.3, 1234) if sd[0] is None else (None, None)
	display.drawSpeedAndDistance(sd[0], sd[1])

def showMessage():
	global messageNum
	display.showStatusText('this is message ' + str(messageNum) + '\nanother line')
	messageNum += 1

root.bind('<w>', lambda e: changePower(1))
root.bind('<s>', lambda e: changePower(-1))
root.bind('<Up>', lambda e: changeGear(1))
root.bind('<Down>', lambda e: changeGear(-1))
root.bind('<space>', lambda e: changeSpeedAndDist())
root.bind('<m>', lambda e: showMessage())

root.after_idle(initialDisplay)
root.mainloop()

display.stop()