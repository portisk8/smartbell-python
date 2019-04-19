import json
import os
from src.Util.TelegramConfig import TelegramConfig
from src.Util.FaceRecognitionConfig import FaceRecognitionConfig

class GeneralConfig(object):
	"""description of class"""

	def __init__(self,environment):
		cwd = os.path.realpath(os.path.dirname(__file__)).replace("\\src\\Util","")
		with open(cwd+'\\'+environment+'.config.json') as json_file:  
			data = json.load(json_file)
		self.Dataset = data["Storage"]["Dataset"]
		self.Contenedor = data["Storage"]["Contenedor"]
		self.Telegram = TelegramConfig(data["Keys"]["TelegramBotKey"], data['Admins'])
		self.FaceConfig = FaceRecognitionConfig(data["Keys"]["FaceRecognitionKey"], data["AzureFaceApi"]["GroupId"], data["AzureFaceApi"]["Endpoint"])

