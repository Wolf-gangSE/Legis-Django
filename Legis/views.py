import json
import owlready2 as owl
from owlready2.reasoning import sync_reasoner_hermit
from .ontology import Ontology as onto
from django.views.generic.base import TemplateView
from django.views.generic import View
from django.http import JsonResponse
from chatterbot import ChatBot
from chatterbot.ext.django_chatterbot import settings


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
    
    def post(self, request, *args, **kwargs):
        '''
        Provide an API that returns a inference
        '''
        input_data = json.loads(request.body.decode('utf-8'))

        property_ontology = owl.get_ontology("/Users/lucas/IC - Legis/Legis/Legis/static/ontologies/OntoProperty.owl")
        crime_ontology = owl.get_ontology("/Users/lucas/IC - Legis/Legis/Legis/static/ontologies/OntoCrime.owl").load()
        property_ontology.load()

        acao = str(input_data["Action_ans"])
        offender = str(input_data["Actor_ans"])
        victim = str(input_data["Actor_victim_ans"])
        activeAgentAge = int(str(input_data["Actor_age_ans"]))
        if (str(input_data["Actor_disorder_ans"]) == "Sim" or str(input_data["Actor_disorder_ans"]) == "sim"):
            mentalsick = True
        else:
            mentalsick = False
        if (str(input_data["Actor_militia_ans"]) == "Sim" or str(input_data["Actor_militia_ans"]) == "sim"):
            militia = True
        else:
            militia = False
        intention = str(input_data["Actor_intetion_ans"])
        crimeObject = str(input_data["Actor_violation_ans"])
        victimAge = int(str(input_data["Victim_age_ans"]))
        isVictimWoman = None
        isVictimPregnant = None
        isVictimHandcapped = None

        if "Actor_ans" in input_data and "Action_ans" in input_data and "Actor_victim_ans" in input_data:
            if (acao == "Homicídio" or acao == "homicídio" or acao == "Homicidio" or acao == "homicidio"):
                property_ontology["Murder"](f"murder_{offender}_{victim}")
            
            elif (acao == "Subtração" or acao == "subtração" or acao == "Subtraçao" or acao == "subtraçao"):
                property_ontology["Subtraction"](f"subtraction_{offender}_{victim}")
            
            elif (acao == "Agressão" or acao == "Agressao"  or acao == "agressao" or acao ==  "agressão"):
                property_ontology["Agression"](f"agression_{offender}_{victim}")
            
            #Instancia dos agentes
            crime_ontology["ActiveAgent"](offender)
            crime_ontology["PassivePerson"](victim)

            #Características do agressor
            if (activeAgentAge >= 18):
                crime_ontology["Adult"](offender)
            
            else:
                crime_ontology["Underage"](offender)
            

            if (activeAgentAge >= 70):
                crime_ontology["AgentOverSeventy"](offender)
            
            if (activeAgentAge <= 21):
                crime_ontology["AgentUnderTwentyOne"](offender)
            

            if (mentalsick):
                crime_ontology["MentallySick"](offender)
            
            else:
                crime_ontology["MentallyHealthy"](offender)
            
            if (militia):
                crime_ontology["MilitiaMan"](offender)

            #Linkando o agente a ação
            crime_ontology[offender].isAuthorOf.append(property_ontology[onto.getAction(acao, offender, victim)])

            if victimAge <= 14:
                crime_ontology["AgentUnderFourteen"](victim)
            elif victimAge >= 60:
                crime_ontology["AgentOverSixty"](victim)


            #Instancia da intenção
            # {"","Matar", "Roubar", "Não Intencional", "Inutilizar", "Vantagem Econômica" }

            if (intention == "Matar" or intention == "matar"):
                intentionConverted = "death"
            elif (intention == "Não Intencional" or intention == "não intencional" or intention == "nao intencional" or intention == "Nao Intencional" or intention == "Não intencional"):
                intentionConverted = "malPractice"
            elif (intention == "Roubar" or intention == "roubar"):
                intentionConverted = "stealing"
            elif (intention == "Inutilizar" or intention == "inutilizar"):
                intentionConverted = "makeUnusable"
            elif (intention == "Vantagem Econômica" or intention == "vantagem econômica" or intention == "Vantagem Economica" or intention == "vantagem economica" or intention == "Vantagem econômica"):
                intentionConverted = "economicAdvantage"
            else:
                intentionConverted = None

            if (intentionConverted != None):
                crime_ontology["Intention"](property_ontology[intentionConverted])

            #Instância da Situação
            crime_ontology["Situation"](onto.getSituation(offender, victim))

            #Verificar como definir o objeto do crime
            if (acao == "Homicídio") or (acao == "homicídio") or (acao == "homicidio") or (acao == "Homicidio"):
                property_ontology["Life"](crimeObject)
            elif (acao == "Subtração") or (acao == "subtração") or (acao == "subtraçao") or (acao == "Subtraçao"):
                property_ontology["ChattelObject"](crimeObject)
            elif (acao == "Agressão") or (acao == "agressão") or (acao == "Agressao") or (acao == "agressao"):
                if (crimeObject == "Psicológico" or crimeObject == "psicológico" or crime_ontology == "psicologico"):
                    property_ontology["Psychological"](crimeObject)
                elif (crimeObject == "Corpo" or crimeObject == "corpo"):
                    property_ontology["PhysicalBody"](crimeObject)
                else: 
                    return JsonResponse({
                        'text': [
                            'Não foi possível realizar as inferências, pois o objeto do crime informado para agressão não é válido. Tente novamente com "Corpo" (para agressão física) ou "Pscicológico" (para agressão psicicológica). '
                            ]
                    }, status=400)  


            property_ontology[onto.getAction(acao, offender, victim)].violates.append(property_ontology[crimeObject])

            crime_ontology[victim].hasViolatedObject.append(property_ontology[crimeObject])

            if (intentionConverted != None):
                property_ontology[onto.getAction(acao, offender, victim)].causedBy.append(property_ontology[intentionConverted])

            crime_ontology[onto.getSituation(offender, victim)].hasEndurant.append(crime_ontology[victim])

            crime_ontology[onto.getSituation(offender, victim)].hasCriminalAct.append(property_ontology[onto.getAction(acao, offender, victim)])

            sync_reasoner_hermit(infer_property_values = True)

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

            if crime_ontology[onto.getSituation(offender, victim)].isDisallowedBy == []:
                articles = "No entanto, ainda não consegui encontrar artigo no código penal que pode referenciar esse tipo de crime."
            else:
                if len(crime_ontology[onto.getSituation(offender, victim)].isDisallowedBy) == 1:
                    article = crime_ontology[onto.getSituation(offender, victim)].isDisallowedBy[0]
                    articles = "Além disso, consegui identificar que o seguinte artigo do código penal pode ser aplicado à situação:"
                    if article == property_ontology.article155_Law2848_Year1940:
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

                        articles = articles + ". Punição: de " + punMin + " à " + punMax + " meses de reclusão"
                    elif article == property_ontology.article157_Law2848_Year1940:
                        articles = articles + "<br> Artigo 157, Decreto-Lei nº 2.848 de 7 de dezembro de 1940 - <strong>Roubo</strong>"
                    elif article == property_ontology.article157_P3_Law2848_Year1940:
                        articles = articles + "<br> Artigo 157, Paragráfo 3, Decreto-Lei nº 2.848 de 7 de dezembro de 1940 - <strong>Roubo e Assassinato</strong>"
                    elif article == property_ontology.article158_Law2848_Year1940:
                        articles = articles + "<br> Artigo 158, Decreto-Lei nº 2.848 de 07 de Dezembro de 1940 - <strong>Extorção</strong>"
                    elif article == property_ontology.article163_Law2848_Year1940:
                        articles = articles + "<br> Artigo 163, Decreto-Lei nº 2.848 de 7 de dezembro de 1940 - <strong>Dano</strong>"
                else:
                    articles = "Além disso, consegui identificar que os seguintes artigos do código penal podem ser aplicados à situação:"
                    for i in crime_ontology[onto.getSituation(offender, victim)].isDisallowedBy:
                        if i == property_ontology.article155_Law2848_Year1940:
                            articles = articles + "<br> Artigo 155, Decreto-Lei nº 2.848 de 7 de dezembro de 1940 - <strong>Furto</strong>"
                        
                        elif i == property_ontology.article157_Law2848_Year1940:
                            articles = articles + "<br> Artigo 157, Decreto-Lei nº 2.848 de 7 de dezembro de 1940 - <strong>Roubo</strong>"
                        elif i == property_ontology.article157_P3_Law2848_Year1940:
                            articles = articles + "<br> Artigo 157, Paragráfo 3, Decreto-Lei nº 2.848 de 7 de dezembro de 1940 - <strong>Roubo e Assassinato</strong>"
                        elif i == property_ontology.article158_Law2848_Year1940:
                            articles = articles + "<br> Artigo 158, Decreto-Lei nº 2.848 de 07 de Dezembro de 1940 - <strong>Extorção</strong>"
                        elif i == property_ontology.article163_Law2848_Year1940:
                            articles = articles + "<br> Artigo 163, Decreto-Lei nº 2.848 de 7 de dezembro de 1940 - <strong>Dano</strong>"

            resposta = "Com base nos dados que você me passou eu inferi que o autor é " + adulto + " e " + mentalHealthy + ". Portanto, ele " + crimeAuthor + ".<br>" + articles + "."

            return JsonResponse({
            'text': [ resposta ]
            }, status=200)
        else:
           return JsonResponse({
            'text': [
                "Não foi possível registrar o ocorrido."
                ]
            }, status=400)  
