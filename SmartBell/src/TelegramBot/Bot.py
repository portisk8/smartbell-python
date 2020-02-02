from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters, ConversationHandler, RegexHandler, Filters
from telegram.error import (TelegramError, Unauthorized, BadRequest, 
                            TimedOut, ChatMigrated, NetworkError)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup
from emoji import emojize
import logging
from time import gmtime, strftime
from datetime import datetime
import threading
from openal import * 
import time

def getEmoji(type):
	return emojize(type, use_aliases=True)

def reproducirAudio(audioPath):
	time.sleep(3)
	source = oalOpen(audioPath)
	source.play()
	while source.get_state() == AL_PLAYING:
		time.sleep(1)
	oalQuit()

class Bot(object):
	"""description of class"""
	
	def __init__(self,generalConfig):
		self.generalConfig = generalConfig
		self.camera = None
		self.faceRecognition= None
		#logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
		self.updater = Updater(token=self.generalConfig.Telegram.Token, use_context=True)
		self.dispatcher = self.updater.dispatcher
		self.add_handlers()
		self.user={}
		

	def add_handlers(self):
		#Agrego los dispatcher con los que trabajará el bot
		start_handler = CommandHandler('start', self.start)
		self.dispatcher.add_handler(start_handler)
		take_picture_handler = MessageHandler(Filters.regex('^(/takepicture|Tomar Foto {})$'.format(getEmoji(":camera:"))), 
											self.take_picture)
		self.dispatcher.add_handler(take_picture_handler)
		#Audio Catch
		audio_handler = MessageHandler(Filters.voice, self.audioHandler)
		self.dispatcher.add_handler(audio_handler)
		# Add conversation handler to save person name and photoFace
		reconoce_handler = ConversationHandler(
			entry_points=[MessageHandler(Filters.regex('^(/reconoce|Reconoce {})$'.format(getEmoji(":bust_in_silhouette:"))), 
											self.reconoce)],
			states={
				"reconoceStep1": [MessageHandler(Filters.photo, self.reconoceStep1)],

				"reconoceStep2": [MessageHandler(Filters.text, self.reconoceStep2)],

				"reconoceStep3": [MessageHandler(Filters.regex('^(Si|No)$'), self.reconoceStep3)]
			},

			fallbacks=[CommandHandler('cancel', self.cancel)]
		)

		self.dispatcher.add_handler(reconoce_handler)

	def set_faceRecognition(self, faceRecognition):
		self.faceRecognition = faceRecognition


	def start(self, update, context):
		print(update.message.chat_id)
		context.bot.send_message(chat_id = update.effective_chat.id ,text="Hola, Bienvenido/a a SmartBell. ", reply_markup= self.get_keyboard('main'))
		return

	def send_photo(self, photoPath):
		for adminId in self.generalConfig.Telegram.Admins:
			try:
				self.updater.bot.send_photo(chat_id = adminId, photo = open(photoPath, 'rb' ))
			except Exception as ex:
				print(ex)

	def send_message(self, message):
		for adminId in self.generalConfig.Telegram.Admins:
			self.updater.bot.send_message(chat_id = adminId, text=message)

	def run(self):
		self.updater.start_polling()
		print ("Run...")
		return

	def set_camera(self,camera):
		self.camera = camera

	def take_picture(self, update, context):
		if(update.message.chat_id in self.generalConfig.Telegram.Admins):
			path = self.camera.take_picture()
			try:
				context.bot.send_photo(chat_id = update.message.chat_id, photo = open(path, 'rb' ))
			except:
			    pass

	def audioHandler(self, update, context):
		file_id = update.message.voice.file_id
		newFile = bot.get_file(file_id)
		nameAudio = datetime.now().strftime('%Y%m%d%H%M%S')
		newFile.download(self.generalConfig.Contenedor +nameAudio+'.opus')
		threading.Thread(target=reproducirAudio(self.generalConfig.Contenedor +nameAudio+'.opus')).start()
		
	#Conversation - Guardar Persona
	def reconoce(self, update, context):
		context.bot.send_message(chat_id = update.message.chat_id ,text="Primero envíame la foto de la persona (Debe ser solo de la cara)...")
		return "reconoceStep1"

	def reconoceStep1(self, update, context):
		photo_file = update.message.photo[-1].get_file()
		namePhoto = datetime.now().strftime('%Y%m%d%H%M%S')
		photo_file.download(self.generalConfig.Contenedor + namePhoto + ".png")
		self.user[update.message.chat_id] = {'photoUrl': self.generalConfig.Contenedor  + namePhoto + ".png"}
		update.message.reply_text('Bien! Ahora, debes ingresar el Nombre y Apellido de la persona')
		return "reconoceStep2"

	def reconoceStep2(self, update, context):
		self.user[update.message.chat_id]['nombreYApellido'] = update.message.text
		update.message.reply_text('Genial! Ahora necesitamos tu confirmación... \nDeséa guardar ésta imagen para la persona {}?'.format(update.message.text), reply_markup=self.get_keyboard('decision'))
		return "reconoceStep3"
			
	def reconoceStep3(self, update, context):
		if(update.message.text == "Si"):
			#Logica para guardar imagen y nombre a azure
			seGuardo = self.faceRecognition.agregar_persona(self.user[update.message.chat_id]['photoUrl'], 
												 self.user[update.message.chat_id]['nombreYApellido'])
			if(seGuardo):
				texto = 'Se asignó correctamente la foto a {}'.format(self.user[update.message.chat_id]['nombreYApellido'])
			else:
				texto = 'Hubo un error al intentar asignar la foto a la persona.'
			context.bot.send_message(chat_id = update.message.chat_id ,text=texto)
		else:
			self.user[update.message.chat_id] = None

		update.message.reply_text('Ok! terminamos.', reply_markup=self.get_keyboard('main'))
		return ConversationHandler.END
	#Keyboar Definitions
	def get_keyboard(self,type):
		keyboard = {"main":[["Tomar Foto {}".format(getEmoji(":camera:"))],
							["Reconoce {}".format(getEmoji(":bust_in_silhouette:"))],
							["Ayuda"]],
					"decision":[["Si","No"]]
					}
		return ReplyKeyboardMarkup(keyboard[type])

	def cancel(self, update, context):
		self.user[update.message.chat_id] = None
		update.message.reply_text('Has cancelado la operación.', reply_markup=self.get_keyboard('main'))
		return ConversationHandler.END
		