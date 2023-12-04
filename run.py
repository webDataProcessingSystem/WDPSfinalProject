import spacy
import json
import re
# load spacy model
nlp = spacy.load("en_core_web_sm")
import json
import csv
from ctransformers import AutoModelForCausalLM
from ner import extract_entities_from_json

#path
model_name_or_path = "model\pytorch_model-00001-of-00015.bin"
llm = AutoModelForCausalLM.from_pretrained(model_path_or_repo_id=model_name_or_path,local_files_only=True,model_type="llama")
json_file = 'D:\DZLY6\P2\WEB\Ass\GrailQA_v1.0\GrailQA_v1.0\grailqa_v1.0_train.json'
tokenizer_name_or_path = r"model\tokenizer.json"
output_file = r'D:\DZLY6\P2\WEB\Ass\train.csv'
extract_entities_from_json(json_file,output_file)