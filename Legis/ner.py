import spacy

class NER():
  def ner_spacy(text):
    ner = spacy.load("./Legis/static/ner_model/model-best/")

    doc = ner(text)

    for ent in doc.ents:
      yield ent.text, ent.label_