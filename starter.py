from ctransformers import AutoModelForCausalLM
repository = 'TheBloke/Llama-2-13B-chat-GGUF'
model_file = 'llama-2-13b-chat.Q4_K_M.gguf'
llm = AutoModelForCausalLM.from_pretrained(repository, model_file=model_file, model_type='llama')

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
            # generate answer
            raw_answer = llm(question)
            print('Raw Answer: ' + raw_answer)
            # write answer
            with open('answer.txt', 'a') as answer_file:
                answer_file.write(question_id + '    R' + '"' + raw_answer + '"' + '\n')


starter('question.txt')