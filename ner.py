import spacy
import json
import re
# load spacy model
nlp = spacy.load("en_core_web_sm")
import json
import csv

def tokenize(text):
    # break text into tokens
    return re.findall(r'\b\w+\b', text.lower())

def extract_entities_from_json(json_file,train_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    #open output file
    with open(train_file, 'w', newline='', encoding='utf-8') as out_file:
        csv_writer = csv.writer(out_file)
        csv_writer.writerow(['Question', 'Answer'])  # write header row

        for item in data:
            question = item['question']
            answers = item['answer']
            # tokenize question
            question_tokens = tokenize(question)
            question_tokens = nlp(question)
            entities = ', '.join([f"{ent.text} ({ent.label_})" for ent in question_tokens.ents])
            item['entities'] = entities
            print(f"Question: {question}\nEntities: {entities}\n")





json_file = 'D:\DZLY6\P2\WEB\Ass\GrailQA_v1.0\GrailQA_v1.0\grailqa_v1.0_train.json'
output_file = r'D:\DZLY6\P2\WEB\Ass\train.csv'
extract_entities_from_json(json_file,output_file)


