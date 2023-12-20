import re
#from ctransformers import AutoModelForCausalLM

# model name and repository set here
repository="TheBloke/Llama-2-7B-GGUF"
model_file="llama-2-7b.Q4_K_M.gguf"

def verbose(text: str, is_verbosed: bool):
    """
    If is_verbosed is set (-v), print the text in the terminal
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
    verbose("### 2> Opened file " + input_str +" and generated question_list ...", is_verbosed)
    return q_list

def write_ouput(outpath: str, q_id: str, raw_answer: str, answer: str, answer_checked: str, entites: dict):
    """
    Get the results and write to the output file
    [Meaning of parameters]
        raw_answer : Raw answer
        entities: Entities
        answer: Answer
        answer_checked: Correctness
    """
    with open(outpath, 'a') as file:
        raw_answer = raw_answer.replace('"', "'")
        prefix = q_id + "\t"
        file.write( prefix + "R\"" + raw_answer + "\"\n")
        file.write( prefix + "A\"" + answer + "\"\n")
        file.write( prefix + "C\"" + answer_checked + "\"\n")
        for ent in entites:
            file.write( prefix + "E\"" + ent['entity'] + "\"\t\"" + ent['wiki_link'] + "\"\n")

    

def get_answer_from_llm(question: str, is_verbosed: bool, llm_name: str=model_file, repository_name: str=repository):
    """
    Receive question and send it to the LLM, get the raw answer from llm
    """
    
    llm = AutoModelForCausalLM.from_pretrained(repository_name, model_file=llm_name, model_type="llama")
    #prompt = input("Type your question (for instance: \"The capital of Italy is \") and type ENTER to finish:\n")
    #print("Computing the answer (can take some time)...")
    completion = llm(question)
    print("COMPLETION: %s" % completion)

    pass
def pipeline(q_id:str, question: str, is_verbosed: bool):
    """
    Pipeline for entities extraction and disambiguate, answer extraction and fact checking
    """
    verbose("### 3> Start processing " + q_id + ": " + question , is_verbosed)
    #get_answer_from_llm(question, is_verbosed)
    
    pass
