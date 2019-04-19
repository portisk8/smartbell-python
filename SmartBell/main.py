
from src.Util.GeneralConfig import GeneralConfig
from src.FaceRecognition.FaceRecognition import FaceRecognition
from src.Camera.Camera import Camera
from src.TelegramBot.Bot import Bot
import threading

enviroment = "Development"

#Iniciando Las configuraciones generales
generalConfig = GeneralConfig(enviroment)
bot = Bot(generalConfig)
fr = FaceRecognition(generalConfig)
bot.set_faceRecognition(fr)


def camara():
	cam = Camera(0,generalConfig)
	bot.set_camera(cam)
	cam.init_video()
	while True:
		key = input("t to take Picture:")
		if key == "t": #Simula un boton de la raspberrypi
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
		if key == "c":
			cam.stop()
			#t._stop()
			#b._stop()


def botTest():
	bot.run()
	while True:
		pass


t = threading.Thread(target=camara, name="Test")
b = threading.Thread(target=botTest, name="botTest")
	
if __name__ == '__main__':
	b.start()
	t.start()