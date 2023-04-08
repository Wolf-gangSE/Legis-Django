import owlready2

class Ontology():
  def getAction(self, legalact, offender, victim):
    if (legalact == "MURDER"):
      return (f"murder_{offender}_{victim}")
    elif (legalact == "SUBTRACTION"):
      return (f"subtraction_{offender}_{victim}")
    elif (legalact == "AGGRESSION"):
      return (f"agression_{offender}_{victim}")
    elif (legalact == "DAMAGE"):
      return (f"damaging_{offender}_{victim}")
    else:
      return None

  def getSituation(self, offender, victim):
    return ("situation_" + offender + "_" + victim)

  def carregarSituacao(self, onto, onto2, acao, offender, victim, actorUnderage, actorUnderTwentyOne, actorOverSeventy, mentalsick, intention, crimeObject):
    print(onto2)
    if (acao == "MURDER"):
      onto2["Murder"](f"murder_{offender}_{victim}")
      
    elif (acao == "SUBTRACTION"):
      onto2["Subtraction"](f"subtraction_{offender}_{victim}")
      
    elif (acao == "AGGRESSION"):
      onto2["Aggression"](f"agression_{offender}_{victim}")

    elif (acao == "DAMAGE"):
      onto2["Damaging"](f"damaging_{offender}_{victim}")
      
    #Instancia dos agentes
    onto["ActiveAgent"](offender)
    onto["PassivePerson"](victim)

    #Características do agressor
    if (actorUnderage):
      onto["Underage"](offender)
    else:
      onto["Adult"](offender)
      

    if (actorOverSeventy):
      onto["AgentOverSeventy"](offender)
      
    if (actorUnderTwentyOne):
      onto["AgentUnderTwentyOne"](offender)
      

    if (mentalsick):
      onto["MentallySick"](offender)
    else:
      onto["MentallyHealthy"](offender)

    #Linkando o agente a ação
    onto[offender].isAuthorOf.append(onto2[self.getAction(acao, offender, victim)])

    #Instancia da intenção
    # {"","Matar", "Roubar", "Não Intencional", "Inutilizar", "Vantagem Econômica" }
    if (intention == "DEATH"):
        intentionConverted = "death"
    elif (intention == "MALPRACTICE"):
        intentionConverted = "malPractice"
    elif (intention == "STEALING"):
        intentionConverted = "stealing"
    elif (intention == "MAKEUNUSABLE"):
        intentionConverted = "makeUnusable"
    elif (intention == "ECONOMICADVANTAGE"):
        intentionConverted = "economicAdvantage"
    else:
        intentionConverted = None

    if (intentionConverted != None):
      if onto["Intention"] == None:
        onto["Intention"](onto2[intentionConverted])

    #Instância da Situação
    onto["Situation"](self.getSituation(offender, victim))

    #Verificar como definir o objeto do crime
    
    if (acao == "MURDER"):
      onto["Life"](crimeObject)
    elif (acao == "SUBTRACTION"):
      onto2["ChattelObject"](crimeObject)
    elif (acao == "AGGRESSION"):
      if (crimeObject == "CRIME-OBJECT-PSYCHOLOGICAL"):
        onto["Psychological"](crimeObject)
      elif (crimeObject == "CRIME-OBJECT-PHYSICAL-BODY"):
        onto["PhysicalBody"](crimeObject)
    elif (acao == "DAMAGE"):
      onto["MaterialObject"](crimeObject)

    if (acao == "MURDER" or acao == "AGGRESSION" or acao == "DAMAGE"):
      onto2[self.getAction(acao, offender, victim)].violates.append(onto[crimeObject])
    else:
      onto2[self.getAction(acao, offender, victim)].violates.append(onto2[crimeObject])

    if (acao == "MURDER" or acao == "AGGRESSION" or acao == "DAMAGE"):
      onto[victim].hasViolatedObject.append(onto[crimeObject])
    else:
      onto[victim].hasViolatedObject.append(onto2[crimeObject])

    if (intentionConverted != None):
      onto2[self.getAction(acao, offender, victim)].causedBy.append(onto2[intentionConverted])

    onto[self.getSituation(offender, victim)].hasEndurant.append(onto[victim])

    onto[self.getSituation(offender, victim)].hasCriminalAct.append(onto2[self.getAction(acao, offender, victim)])