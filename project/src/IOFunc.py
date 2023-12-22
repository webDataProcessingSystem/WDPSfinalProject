import re
#from entityRecognizer import EntityRecognizer
from ctransformers import AutoModelForCausalLM
from src.answer_extraction import answer_extraction
from src.questionClassify import QuestionClassify
from src.fact_check import verify_answer_with_wikipedia, verify_yes_no_answer_with_wikipedia

repository="./llm/"
model_file="llama-2-7b-chat.Q4_K_M.gguf"  #"llama-2-13b-chat.Q3_K_L.gguf"

default_out = "./test/output.txt"
def verbose(text: str, is_verbosed: bool):
    """
    If is_verbosed is set, print the text in the terminal
    """
    if is_verbosed:
        print(text)


def get_input(input_str: str, is_verbosed: bool) -> list:
    """
    Open the input file and store the q_id & question
        return [{q_id: qestion_id, question: question_text}]
    """
    q_list = []
    with open(input_str, 'r') as file:
        lines = file.readlines()
        for line in lines:
            q_id, question = tuple(re.split(r' {4}|\t', line.strip()))
            pattern = r"Question: "
            matchObj = re.match(pattern, question)
            question = question if matchObj == None else question[10:]
            q_list.append({"q_id": q_id, "question": question})
    verbose("### ------- Opened file " + input_str +" and generated question_list ...", is_verbosed)
    return q_list

def write_ouput(q_id: str, raw_answer: str, answer: str, answer_checked: str, entites: dict,outpath: str):
    """
    raw_answer : R
    entities: E
    answer: A
    answer_checked: C
    """
    with open(outpath, 'a') as file:
        raw_answer = raw_answer.strip().replace('"', "'")
        prefix = q_id + "\t"
        file.write( prefix + "R\"" + raw_answer + "\"\n")
        file.write( prefix + "A\"" + answer + "\"\n")
        file.write( prefix + "C\"" + answer_checked + "\"\n")
        for ent in entites:
            file.write( prefix + "E\"" + ent['entity'] + "\"\t\"" + ent['entity_link'] + "\"\n")


def get_answer_from_llm(question: str, is_verbosed: bool, llm_name: str=model_file, repository_name: str=repository):
    llm = AutoModelForCausalLM.from_pretrained(repository_name+llm_name)
    verbose("### ------- Waiting for the response from LLM of question \""  + question + "\"", is_verbosed)
    completion = llm(question)
    return completion

def pipeline(q_id:str, question: str, is_verbosed: bool, outpath:str = default_out):
    raw_answer = get_answer_from_llm(question, is_verbosed)
   
    verbose("### Raw answer by LLM:\n " + str(raw_answer), is_verbosed)
    verbose("### ------- Start processing " + q_id + ": " + question , is_verbosed)
    ansExt = answer_extraction()  # EntityRecognizer called in answer_extraction
    ans_and_entities = ansExt.load_model(question, raw_answer, is_verbosed)  # return answer and entity list
   
    queClassifier = QuestionClassify()
    queCategory = queClassifier.classify_question(question)
    if queCategory == 0:    # yes/no question
        bool_corretness = verify_yes_no_answer_with_wikipedia(question, ans_and_entities['answer'])
    else:  # non-yes/no question
        bool_corretness = verify_answer_with_wikipedia(question, ans_and_entities['answer'])
    corretness = 'corret' if bool_corretness == True else 'incorrect'

    write_ouput(q_id, raw_answer, ans_and_entities['answer'], corretness, ans_and_entities['entities'], outpath)
