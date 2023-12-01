import spacy
import json
import re
# load spacy model
nlp = spacy.load("en_core_web_sm")
import json
import csv
from ctransformers import AutoModelForCausalLM
repository = 'TheBloke/Llama-2-13B-chat-GGUF'
model_file = 'llama-2-13b-chat.Q4_K_M.gguf'
llm = AutoModelForCausalLM.from_pretrained(repository, model_file=model_file, model_type='llama')

def tokenize(text):
    # break text into tokens
    return re.findall(r'\b\w+\b', text.lower())

def extract_entities_from_json(json_file,train_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    #open output file
    with open(train_file, 'w', newline='', encoding='utf-8') as out_file:
        csv_writer = csv.writer(out_file)
        csv_writer.writerow(['Question', 'Answer',"question_entity","answer_raw","answer_entity"])  # write header row

        for item in data:
            question = item['question']
            answers = item['answer']
            raw_answer = llm(question)
            # tokenize question
            question_tokens = tokenize(question)
            question_tokens = nlp(question)
            entities = ', '.join([f"{ent.text} ({ent.label_})" for ent in question_tokens.ents])
            answers_tokens=tokenize(raw_answer)
            answers_tokens=nlp(answers_tokens)
            extracted_answer = ', '.join([f"{ent.text} ({ent.label_})" for ent in answers_tokens.ents])
            csv_writer.writerow([question, answers, entities, raw_answer, extracted_answer])





json_file = 'D:\DZLY6\P2\WEB\Ass\GrailQA_v1.0\GrailQA_v1.0\grailqa_v1.0_train.json'
output_file = r'D:\DZLY6\P2\WEB\Ass\train.csv'
extract_entities_from_json(json_file,output_file)


