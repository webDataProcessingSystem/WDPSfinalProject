import wikipedia
def entity_linking(question_entities, answer_entities):
    entities = question_entities
    for entity in answer_entities:
        if entity not in entities:
            entities.append(entity)
    print(entities)
    entity_link=[]
    for entity in entities:
        try:
            wiki_link = wikipedia.page(entity).url
        except:
            wiki_link = 'Page not found'
        entity_link.append((entity, wiki_link))
    print(entity_link)

# test
entity_linking(['Amsterdam', 'Netherlands'], ['Amsterdam', 'Netherlands', 'North Holland', 'over 850,000', 'The Hague', 'Dutch', 'Netherlands', 'Amsterdam'])
# entity_linking(['Managua', 'Nicaragua'],['Managua', 'Nicaragua', 'Lake Managua', 'the Pacific Ocean', 'approximately 1.5 million', 'Nicaragua'])