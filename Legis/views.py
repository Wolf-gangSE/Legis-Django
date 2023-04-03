import json
import spacy
import owlready2 as owl
from owlready2.reasoning import sync_reasoner_pellet
from .ontology import Ontology
from .ner import NER as ner
from django.views.generic.base import TemplateView
from django.views.generic import View
from django.http import JsonResponse
from chatterbot import ChatBot
from chatterbot.ext.django_chatterbot import settings
import shutil
import os

class ChatterBotAppView(TemplateView):
		template_name = 'app.html'


class ChatterBotApiView(View):
		"""
		Provide an API endpoint to interact with ChatterBot.
		"""

		chatterbot = ChatBot(**settings.CHATTERBOT)

		def post(self, request, *args, **kwargs):
				"""
				Return a response to the statement in the posted data.
				* The JSON data should contain a 'text' attribute.
				"""
				input_data = json.loads(request.body.decode('utf-8'))
				print(input_data)

				if 'text' not in input_data:
						return JsonResponse({
								'text': [
										'The attribute "text" is required.'
								]
						}, status=400)

				response = self.chatterbot.get_response(input_data)

				response_data = response.serialize()

				return JsonResponse(response_data, status=200)

		def get(self, request, *args, **kwargs):
				"""
				Return data corresponding to the current conversation.
				"""
				return JsonResponse({
						'name': self.chatterbot.name
				})

class LegisApiView(View):
	def get(self, request, *args, **kwargs):
		return JsonResponse({
			'Legis': 'Legis'
		})

class LegisNerApiView(View):
		def post(self, request, *args, **kwargs):
				'''
				Provide an API that returns NER classification
				'''
				input_data = json.loads(request.body.decode('utf-8'))

				output = ner.ner_spacy(input_data['text'])

				print(output)
				
				return JsonResponse({
						'NER': output
				})

		def get(self, request, *args, **kwargs):
				'''
				Provide an API that returns NER classification
				'''
				input_data = request.GET['text']

				output = dict(ner.ner_spacy(input_data))
				
				return JsonResponse({
						'NER': output
				})
		
class LegisOntologyApiView(View):
		
		def post(self, request, *args, **kwargs):
				'''
				Provide an API that returns a inference
				'''
				input_data = json.loads(request.body.decode('utf-8'))
				print(input_data)

				onto = Ontology()
				

				property_ontology = owl.get_ontology("./Legis/static/ontologies/OntoProperty.owl")
				crime_ontology = owl.get_ontology("./Legis/static/ontologies/OntoCrime.owl").load()
				property_ontology.load()

				# Actor and Victim
				if ("ACTOR" in input_data):
					offender = str(input_data["ACTOR"]).replace(" ", "")
				else:
					return JsonResponse({
						'text': "Desculpe, com as informações que você me passou eu não consegui identificar o agente do crime. Tente novamente, acrescentando mais informações."
					})

				if ("VICTIM" in input_data):
					victim = str(input_data["VICTIM"]).replace(" ", "")
				else:
					return JsonResponse({
						'text': "Desculpe, com as informações que você me passou eu não consegui identificar a vítima do crime. Tente novamente, acrescentando mais informações."
					})

				if ("ACTOR-MENTALLY-SICK" in input_data):
					mentalsick = True
				else:
					mentalsick = False
				
				if ("ACTOR-UNDERAGE" in input_data):
					actorUnderage = True
				else:
					actorUnderage = False

				if ("ACTOR-UNDER-TWENTY-ONE" in input_data):
					actorUnderTwentyOne = True
				else:
					actorUnderTwentyOne = False
				
				if ("ACTOR-OVER-SEVENTY" in input_data):
					actorOverSeventy = True
				else:
					actorOverSeventy = False
				

				# Action 
				if ("CRIME-OBJECT-PSYCHOLOGICAL" in input_data or "CRIME-OBJECT-PHYSICAL-BODY" in input_data or "AGRESSION" in input_data):
					action1 = "SUBTRACTION"
					action2 = "AGGRESSION"

					if ("CRIME-OBJECT-PSYCHOLOGICAL" in input_data):
						crimeObject = "CRIME-OBJECT-PSYCHOLOGICAL"
					elif ("CRIME-OBJECT-PHYSICAL-BODY" in input_data):
						crimeObject = "CRIME-OBJECT-PHYSICAL-BODY"
					else:
						return JsonResponse({
							'text': "Desculpe, com as informações que você me passou eu não consegui identificar o objeto do crime. Tente novamente, acrescentando mais informações."
						})
					
					intention = "STEALING"
					
					onto.carregarSituacao(crime_ontology, property_ontology, action1, offender, victim, actorUnderage, actorUnderTwentyOne, actorOverSeventy, mentalsick, intention, crimeObject)

					onto.carregarSituacao(crime_ontology, property_ontology, action2, offender, victim, actorUnderage, actorUnderTwentyOne, actorOverSeventy, mentalsick, intention, crimeObject)

				elif ("SUBTRACTION" in input_data or "CRIME-OBJECT-CHATTEL-OBJECT" in input_data):

					action = "SUBTRACTION"
					if ("CRIME-OBJECT-CHATTEL-OBJECT" in input_data):
						crimeObject = str(input_data["CRIME-OBJECT-CHATTEL-OBJECT"]).replace(" ", "")
					else:
						return JsonResponse({
							'text': "Desculpe, com as informações que você me passou eu não consegui identificar o objeto do crime. Tente novamente, acrescentando mais informações."
						})
					
					intention = "STEALING"
					
					onto.carregarSituacao(crime_ontology, property_ontology, action, offender, victim, actorUnderage, actorUnderTwentyOne, actorOverSeventy, mentalsick, intention, crimeObject)


				else:
					return JsonResponse({
						'text': "Desculpe, com as informações que você me passou eu não consegui identificar a ação do crime. Tente novamente, acrescentando mais informações."
					})

				if "ACTOR" in input_data and "VICTIM" in input_data:
						
						sync_reasoner_pellet(infer_property_values = True, infer_data_property_values = True, debug=1)

						adulto = ''
						mentalHealthy = ''
						crimeAuthor = ''

						if crime_ontology["Adult"] in crime_ontology.get_parents_of(crime_ontology[offender]):
								adulto = "adulto"
						else:
								adulto = "menor de idade"
						if crime_ontology["MentallyHealthy"] in crime_ontology.get_parents_of(crime_ontology[offender]):
								mentalHealthy = 'mentamente saudável'
						else:
								mentalHealthy = 'mentalmente doente'
						if crime_ontology["CrimeAuthor"] in crime_ontology[offender].is_a:
								crimeAuthor = 'possui responsabilidade criminal'
						else:
								crimeAuthor = 'não possui responsabilidade criminal'

						if crime_ontology[onto.getSituation(offender, victim)].is_a[0].isDisallowedBy == []:
								articles = "No entanto, ainda não consegui encontrar artigo no código penal que pode referenciar esse tipo de crime."
						else:
								if len(crime_ontology[onto.getSituation(offender, victim)].isDisallowedBy) == 1:
										article = crime_ontology[onto.getSituation(offender, victim)].is_a[0].isDisallowedBy[0]
										articles = "Além disso, consegui identificar que o seguinte artigo do código penal pode ser aplicado à situação:"
										if article == property_ontology.ArticleTheft:
												articles = articles + "<br> Artigo 155, Decreto-Lei nº 2.848 de 7 de dezembro de 1940 - <strong>Furto</strong>"
												punMin = "0"
												punMax = "0"
												firstPunish = property_ontology.article155_Law2848_Year1940.hasPunishment[0]
												secondPunish = property_ontology.article155_Law2848_Year1940.hasPunishment[1]
												if firstPunish == property_ontology.max_48M:
														punMax = "48"
												elif firstPunish == property_ontology.max_120M:
														punMax = "120"
												elif firstPunish == property_ontology.max_360M:
														punMax = "360"

												if secondPunish == property_ontology.min_12M:
														punMin = "12"
												elif secondPunish == property_ontology.min_48M:
														punMin = "48"
												elif secondPunish == property_ontology.min_240M:
														punMin = "240"

												articles = articles + ". Punição: de " + punMin + " à " + punMax + " meses de retenção"

										elif article == property_ontology.ArticleRobbery:
												articles = articles + "<br> Artigo 157, Decreto-Lei nº 2.848 de 7 de dezembro de 1940 - <strong>Roubo</strong>"
												punMin = "0"
												punMax = "0"
												firstPunish = property_ontology.article157_Law2848_Year1940.hasPunishment[0]
												secondPunish = property_ontology.article157_Law2848_Year1940.hasPunishment[1]

												if firstPunish == property_ontology.min_12M:
													punMin = "12"
												elif firstPunish == property_ontology.min_48M:
													punMin = "48"
												elif firstPunish == property_ontology.min_240M:
													punMin = "240"

												if secondPunish == property_ontology.max_48M:
													punMax = "48"
												elif secondPunish == property_ontology.max_120M:
													punMax = "120"
												elif secondPunish == property_ontology.max_360M:
													punMax = "360"

												articles = articles + ". Punição: de " + punMin + " à " + punMax + " meses de retenção"

										elif article == property_ontology.ArticleRobberyAMurder:
												articles = articles + "<br> Artigo 157, Paragráfo 3, Decreto-Lei nº 2.848 de 7 de dezembro de 1940 - <strong>Roubo e Assassinato</strong>"
										elif article == property_ontology.ArticleExtortion:
												articles = articles + "<br> Artigo 158, Decreto-Lei nº 2.848 de 07 de Dezembro de 1940 - <strong>Extorção</strong>"
										elif article == property_ontology.ArticleDamage:
												articles = articles + "<br> Artigo 163, Decreto-Lei nº 2.848 de 7 de dezembro de 1940 - <strong>Dano</strong>"
								else:
										articles = "Além disso, consegui identificar que os seguintes artigos do código penal podem ser aplicados à situação:"
										for i in crime_ontology[onto.getSituation(offender, victim)].isDisallowedBy:
												if i == property_ontology.article155_Law2848_Year1940:
														articles = articles + "<br> Artigo 155, Decreto-Lei nº 2.848 de 7 de dezembro de 1940 - <strong>Furto</strong>"
														punMin = "0"
														punMax = "0"
														firstPunish = property_ontology.article155_Law2848_Year1940.hasPunishment[0]
														secondPunish = property_ontology.article155_Law2848_Year1940.hasPunishment[1]
														if firstPunish == property_ontology.max_48M:
																punMax = "48"
														elif firstPunish == property_ontology.max_120M:
																punMax = "120"
														elif firstPunish == property_ontology.max_360M:
																punMax = "360"

														if secondPunish == property_ontology.min_12M:
																punMin = "12"
														elif secondPunish == property_ontology.min_48M:
																punMin = "48"
														elif secondPunish == property_ontology.min_240M:
																punMin = "240"

														articles = articles + ". Punição: de " + punMin + " à " + punMax + " meses de retenção."
												
												elif i == property_ontology.article157_Law2848_Year1940:
														articles = articles + "<br> Artigo 157, Decreto-Lei nº 2.848 de 7 de dezembro de 1940 - <strong>Roubo</strong>"
														punMin = "0"
														punMax = "0"
														firstPunish = property_ontology.article157_Law2848_Year1940.hasPunishment[0]
														secondPunish = property_ontology.article157_Law2848_Year1940.hasPunishment[1]

														if firstPunish == property_ontology.min_12M:
															punMin = "12"
														elif firstPunish == property_ontology.min_48M:
															punMin = "48"
														elif firstPunish == property_ontology.min_240M:
															punMin = "240"

														if secondPunish == property_ontology.max_48M:
															punMax = "48"
														elif secondPunish == property_ontology.max_120M:
															punMax = "120"
														elif secondPunish == property_ontology.max_360M:
															punMax = "360"

														articles = articles + ". Punição: de " + punMin + " à " + punMax + " meses de retenção."
												elif i == property_ontology.article157_P3_Law2848_Year1940:
														articles = articles + "<br> Artigo 157, Paragráfo 3, Decreto-Lei nº 2.848 de 7 de dezembro de 1940 - <strong>Roubo e Assassinato</strong>."
												elif i == property_ontology.article158_Law2848_Year1940:
														articles = articles + "<br> Artigo 158, Decreto-Lei nº 2.848 de 07 de Dezembro de 1940 - <strong>Extorção</strong>."
												elif i == property_ontology.article163_Law2848_Year1940:
														articles = articles + "<br> Artigo 163, Decreto-Lei nº 2.848 de 7 de dezembro de 1940 - <strong>Dano</strong>."

						resposta = "Com base nos dados que você me passou eu inferi que o autor " + input_data["ACTOR"].replace(".", " ") + " é " + adulto + " e " + mentalHealthy + ". Portanto, ele " + crimeAuthor + " pela ação cometida contra " + input_data["VICTIM"].replace(".", " ") + ".<br>" + articles

						return JsonResponse({
						'text': [ resposta ]
						}, status=200)
				else:

					return JsonResponse({
						'text': [
						"Não foi possível registrar o ocorrido."
					]
					}, status=400)  
