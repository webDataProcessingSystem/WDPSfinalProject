import spacy
import re
import pandas as pd
import csv
from ctransformers import AutoModelForCausalLM 


#clean question
def dataclean(text):
    #lowercase
    text = text.lower()
    #remove punctuation
    cleaned_text = re.sub(r'question-\d{3}<tab>', '', text)
    cleaned_text = re.sub(r'<newline>', '', cleaned_text)
    cleaned_text = re.sub(r'</newline>', '', cleaned_text)
    #remove common words
    common_words_to_remove = ['the', 'is', 'and', 'a', 'of', 'to', 'in', 'that', 'it', 'on', 'for', 'are', 'was', 'as', 'with', 'be', 'at', 'this', 'have', 'from', 'or', 'an', 'by', 'not', 'but', 'also', 'can', 'which', 'its', 'other', 'all', 'they', 'their', 'has', 'been', 'than', 'these', 'such', 'some', 'there', 'if', 'when', 'what', 'who', 'where', 'how', 'why', 'between', 'over', 'under', 'during', 'before', 'after', 'while', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'just', 'don', 'now', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', 'couldn', 'didn', 'doesn', 'hadn', 'hasn', 'haven', 'isn', 'ma', 'mightn', 'mustn', 'needn', 'shan', 'shouldn', 'wasn', 'weren', 'won', 'wouldn']
    for word in common_words_to_remove:
        regex = r'\b' + word + r'\b' 
        cleaned_text = re.sub(regex, '', cleaned_text)

    return cleaned_text

def generate_answer_and_extract_entities(original_file,train_file,model_path):
    model = AutoModelForCausalLM.from_pretrained(model_path_or_repo_id=model_path, local_files_only=True, model_type='llama')
  
    #open output file
    df = pd.read_csv(original_file)
    answer = df['Answer'].tolist()
    #write to csv file
    with open(train_file, 'w', newline='', encoding='utf-8') as out_file:
        csv_writer = csv.writer(out_file)
        csv_writer.writerow(['Question',"Answer","CleanQuestion","GenAnswer_raw"])  # write header row

        for index, row in df.iterrows():
            question = row['Question']  
            raw_answer = model(question)
            clean_question =dataclean(question)
            # clean_raw_answer=dataclean(raw_answer)    
            original_answer = answer[index] if index < len(answer) else ''       
            #for debug
            # print("Question:" + question)
            # print("CleanQuestion:" + clean_question)
            # print('Raw Answer:' + raw_answer)
            # print('Answers:' )
            # print(original_answer)
            ##print('CleanGenAnswer:' + clean_raw_answer)
            # print('End')
          
            

            csv_writer.writerow([question,original_answer,clean_question,raw_answer])
        
generate_answer_and_extract_entities(r"D:\DZLY6\P2\WEB\dataset\WDPS_DATASET.CSV",r"D:\DZLY6\P2\WEB\dataset\WDPS_GENDATASET.CSV",r"D:\DZLY6\P2\WEB\model_13b\llama-2-13b-chat.Q4_K_M.gguf")