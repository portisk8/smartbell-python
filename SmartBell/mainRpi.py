
"""
Antes debe instalar en la rpi:
	sudo apt-get install python-rpi.gpio python3-rpi.gpio

"""
from src.Util.GeneralConfig import GeneralConfig
from src.FaceRecognition.FaceRecognition import FaceRecognition
from src.Camera.Camera import Camera
from src.TelegramBot.Bot import Bot
import threading
import time
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

enviroment = "Development"

#Iniciando Las configuraciones generales
print("Iniciando Confiuraciones...")
generalConfig = GeneralConfig(enviroment)
bot = Bot(generalConfig)
fr = FaceRecognition(generalConfig)
bot.set_faceRecognition(fr)

#Configurando button
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)


def camara():
	statusBtn = False
	cam = Camera(0,generalConfig)
	bot.set_camera(cam)
	cam.init_video()
	print("Escuchando...")
	while True:
		if GPIO.input(10) == GPIO.HIGH and statusBtn == False:
			print("Timbre!...")
			statusBtn = True
			path = cam.take_picture()
			bot.send_photo(path)
			result = fr.recognize(path)
			print(result)
			print("_________________________________")
			print("Personas reconocidas en la foto:")
			for r in result:
				if(r['isRecognized']):
					texto = r['person']['name']
					print("|_ {}".format(r['person']['name']))
				else:
					texto = "No reconocible"
					print("|_ No reconocible")
				bot.send_message(texto)
		if GPIO.input(10) == GPIO.LOW and statusBtn == True:
			print("Seteando status de botón e iniciando tiempo de espera...")
			statusBtn = False
			time.sleep(10)
			print("Terminó tiempo de espera")

def botTest():
	bot.run()
	while True:
		pass

t = threading.Thread(target=camara, name="Test")
b = threading.Thread(target=botTest, name="botTest")
	
if __name__ == '__main__':
	print("Iniciando Camara y Bot...")
	b.start()
	t.start()