import re
#from ctransformers import AutoModelForCausalLM

repository="TheBloke/Llama-2-7B-GGUF"
model_file="llama-2-7b.Q4_K_M.gguf"

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
            q_list.append({"q_id": q_id, "question": question})
    verbose("### 2> Opened file " + input_str +" and generated question_list ...", is_verbosed)
    return q_list

def get_answer_from_llm(question: str, is_verbosed: bool, llm_name: str=model_file, repository_name: str=repository):
    llm = AutoModelForCausalLM.from_pretrained(repository_name, model_file=llm_name, model_type="llama")
    #prompt = input("Type your question (for instance: \"The capital of Italy is \") and type ENTER to finish:\n")
    #print("Computing the answer (can take some time)...")
    completion = llm(question)
    print("COMPLETION: %s" % completion)

    pass
def pipeline(q_id:str, question: str, is_verbosed: bool):
    verbose("### 3> Start processing " + q_id + ": " + question , is_verbosed)
    #get_answer_from_llm(question, is_verbosed)
    
    pass
