import gen_raw_answer
import spacy_ner
import entity_linking


def starter(file_name):
    # clear answer file
    with open('answer.txt', 'w') as f:
        f.write('')
    # read question file
    with open(file_name, 'r') as f:
        lines = f.readlines()
        for line in lines:
            question_id = line.split('    ')[0]
            question = line.split('    ')[1]
            print(question_id)
            print(question)
            # generate raw answer
            raw_answer = gen_raw_answer(question)
            
            # ----Entity Extraction----
            # extract entities
            entities_answer = spacy_ner.ner(raw_answer)
            entities_question = spacy_ner.ner(question)
            # generate distinct entities
            distinct_entities = entities_question
            for entity in entities_answer:
                if entity not in distinct_entities:
                    distinct_entities.append(entity)
            print(distinct_entities)
            entity_liking(distinct_entities)


starter('question.txt')