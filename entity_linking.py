import wikipedia
def entity_linking(question_entities, answer_entities):
    entities = question_entities
    for entity in answer_entities:
        if entity not in entities:
            entities.append(entity)
    print(entities)
    entity_link=[]
    for entity in entities:
        entity_link.append((entity,wikipedia.page(entity).url))
    print(entity_link)

# test
entity_linking(['Managua', 'Nicaragua'],['Managua', 'Nicaragua', 'Lake Managua', 'the Pacific Ocean', 'approximately 1.5 million', 'Nicaragua'])