
class Ontology():
  def getAction(legalact, offender, victim):
    if (legalact == "Homicídio" or legalact == "homicídio" or legalact == "Homicidio" or legalact == "homicidio"):
      return (f"murder_{offender}_{victim}")
    elif (legalact == "Subtração" or legalact == "subtração" or legalact == "Subtraçao" or legalact == "subtraçao"):
      return (f"subtraction_{offender}_{victim}")
    elif (legalact == "Agressão" or legalact == "Agressao"  or legalact == "agressao" or legalact == "agressão"):
      return (f"agression_{offender}_{victim}")
    else:
      return None

  def getSituation(offender, victim):
    return ("situation_" + offender + "_" + victim)