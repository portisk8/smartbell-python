import json
import os
from src.Util.TelegramConfig import TelegramConfig
from src.Util.FaceRecognitionConfig import FaceRecognitionConfig

class GeneralConfig(object):
	"""description of class"""

	def __init__(self,environment):
		if os.name == 'nt':
			cwd = os.path.realpath(os.path.dirname(__file__)).replace("src\\Util","")
		else:
			cwd = os.path.realpath(os.path.dirname(__file__)).replace("src/Util","")
		with open(cwd+environment+'.config.json') as json_file:  
			data = json.load(json_file)
		self.Environment= data["Environment"]
		self.Dataset = data["Storage"]["Dataset"]
		self.Contenedor = data["Storage"]["Contenedor"]
		self.Telegram = TelegramConfig(data["Keys"]["TelegramBotKey"], data['Admins'])
		self.FaceConfig = FaceRecognitionConfig(data["Keys"]["FaceRecognitionKey"], data["AzureFaceApi"]["GroupId"], data["AzureFaceApi"]["Endpoint"])


