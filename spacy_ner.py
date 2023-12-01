import spacy
#from spacy import displacy
#from spacy import tokenizer


def ner(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    sentences = list(doc.sents)

    # token -> entity labeling
    # ents = [(e.text, e.label_) for e in doc.ents]
    ents = [e.text for e in doc.ents]
    print(ents)
    return ents

# test
ner('Yes, Managua is the capital and largest city of Nicaragua. It is located in the southwestern part of the country, near Lake Managua and the Pacific Ocean. The city has a population of approximately 1.5 million people and is the political, economic, and cultural center of Nicaragua.')
ner('Is Managua the capital of Nicaragua?')
