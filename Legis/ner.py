import spacy

class NER():
  def ner_spacy(text):
    ner = spacy.load("./Legis/static/ner_model/model-best/")

    doc = ner(text)

    entities = {}
    for ent in doc.ents:
      entities[ent.label_] = ent.text
      #yield ent.label_, ent.text
    return entities
    
      