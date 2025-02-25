import spacy

class NERDetector:
    nlp = spacy.load("en_core_web_trf")

    @staticmethod
    def detect(text: str) -> dict:
        doc = NERDetector.nlp(text)
        entities = {
            'names': [ent.text for ent in doc.ents if ent.label_ == 'PERSON'],
            'dates': [ent.text for ent in doc.ents if ent.label_ == 'DATE'],
            'orgs': [ent.text for ent in doc.ents if ent.label_ == 'ORG'],
        }
        return {k: v for k, v in entities.items() if v}
