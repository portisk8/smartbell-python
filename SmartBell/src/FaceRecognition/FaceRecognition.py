import cognitive_face as CF
from src.Util.GeneralConfig import GeneralConfig

class FaceRecognition(object):
	"""description of class"""

	def __init__(self, gc):
		self.BASE_URL = gc.FaceConfig.Enpoint
		self.PERSONGROUPID = gc.FaceConfig.GroupId
		CF.BaseUrl.set(self.BASE_URL)
		CF.Key.set(gc.FaceConfig.Key)

	def recognize(self,pathPicture):
		persons=[]
		response = CF.face.detect(pathPicture)
		face_ids = [d['faceId'] for d in response]
		print(face_ids)
		if(len(face_ids) > 0):
			identified_faces = CF.face.identify(face_ids, self.PERSONGROUPID)
			print (identified_faces)
			for identified_face in identified_faces:
				person = {'personId': '' , 'confidence':0}
				if(len(identified_face['candidates']) > 0):
					for candidates in identified_face['candidates']:
						if(candidates['confidence'] > person['confidence']):
							person = candidates
					if person['confidence'] > 0.7:
						#self.__agregarYentrenar(pathPicture,self.PERSONGROUPID,person['personId'])
						result = CF.person.get(self.PERSONGROUPID,person['personId'])
						person['isRecognized'] = True
						person['person'] = result
					else:
						person['isRecognized'] = False
					persons.append(person)
		return persons

	def __agregarYentrenar(self,image,personGroupId,personId):
		"""Agrega la imagen a la persona que pertenece a un grupo de personas y la entrena.
		"""
		faceId = CF.person.add_face(image,personGroupId,personId)
		if(faceId != None):
			CF.person_group.train(personGroupId)
			return True
		else:
			return False

	def newPerson(self,name):
		"""Crea una persona en el grupo determinado
		Args:
			name: Nombre de la persona.
		Returns:
			Una nueva personId.
		"""
		return(CF.person.create(self.PERSONGROUPID,name))
		
	def get_person_lists(self):
		""" Obtiene listado de personas.
		Returns:
				Array of dict: name, personId
				"""
		lists = CF.person.lists(self.PERSONGROUPID)
		persons = []
		for item in lists:
			persons.append({'name':item['name'], 'personId':item['personId']})
		return persons

	def agregar_persona(self, photoUrl, name):
		persons = self.get_person_lists()
		personId = None
		for person in persons:
			if(person['name'].lower() == name.lower()):
				personId = person['personId']
				break
		if(personId == None):
			jsonData = self.newPerson(name)
			personId = jsonData['personId']
		return self.__agregarYentrenar(photoUrl, self.PERSONGROUPID,personId)



