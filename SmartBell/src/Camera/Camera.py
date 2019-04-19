import cv2
import threading
import logging


class Camera(object):
	""" Description"""


	def __init__(self,src,generalConfig):
		self.generalConfig = generalConfig
		self.camera = cv2.VideoCapture(src)
		self.d = threading.Thread(target=self.__video, name='InitVideo')
		self.img_counter = 0
		self.grabando = False
		
	def init_video(self):
		self.grabando = True
		self.d.start()

	def __video(self):
		try:
			while(True):
				# Capture frame-by-frame
				self.grabbed, self.frame = self.camera.read()

				# Our operations on the frame come here
				#gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

				# Display the resulting frame
				cv2.imshow('frame',self.frame)
				k = cv2.waitKey(1)
				if k%256 == 27:
					# ESC pressed
					print("Escape hit, closing...")
					self.stop()

				#elif k%256 == 32:
				#	# SPACE pressed
				#	self.take_picture()
		except :
		    pass

	def stop(self):
		self.camera.release()
		cv2.destroyAllWindows()
		self.grabando = False
		self.d._stop()
	
	
	def take_picture(self):
		if not self.grabando:
			self.grabbed, self.frame = self.camera.read()
		img_name = self.generalConfig.Contenedor + "\\opencv_frame_{}.png".format(self.img_counter)
		cv2.imwrite(img_name, self.frame)
		print("{} written!".format(img_name))
		self.img_counter += 1
		return img_name




	


