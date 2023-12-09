import spacy
import re
# load spacy model
nlp = spacy.load("en_core_web_sm")
import csv
import pandas as pd
from ctransformers import AutoModelForCausalLM 

#read txt file, extract entities from question and answer,save to csv file

def read_txt_file():
    # File paths
    files = [
        r'D:\DZLY6\P2\WEB\dataset\archive\S08_question_answer_pairs.txt',
        r'D:\DZLY6\P2\WEB\dataset\archive\S09_question_answer_pairs.txt',
        r'D:\DZLY6\P2\WEB\dataset\archive\S10_question_answer_pairs.txt'
    ]

    # Using pandas.concat instead of append as per the new recommendation
    combined_df = pd.concat(
        [pd.read_csv(file, sep='\t', usecols=['Question', 'Answer'], encoding='ISO-8859-1') for file in files], 
        ignore_index=True
    )

    # Drop any rows with missing questions or answers
    combined_df.dropna(subset=['Question', 'Answer'], inplace=True)

    # Save to CSV with the updated method
    csv_output_path = r'D:\DZLY6\P2\WEB\dataset\archive\combined_question_answer_pairs_updated.csv'
    combined_df.to_csv(csv_output_path, index=False)




read_txt_file()


# def tokenize(text):
#     # break text into tokens
#     return re.findall(r'\b\w+\b', text.lower())

# def extract_entities_from_json(txt_file,train_file,model_path,tokenizer_path):

#     model = AutoModelForCausalLM.from_pretrained(model_path_or_repo_id=model_path, local_files_only=True, model_type='llama')
   
#     #open output file
#     with open(train_file, 'w', newline='', encoding='utf-8') as out_file:
#         csv_writer = csv.writer(out_file)
#         csv_writer.writerow(['Question', 'Answer',"question_entity","answer_raw","answer_entity"])  # write header row

#         for item in data:
#             question = item['question']
#             answers = item['answer']
#             raw_answer = model(question)
#             print("Question:" + question)
#             print('Raw Answer:' + raw_answer)
#             print('Answers:' )
#             print(answers)
#             print('End')




