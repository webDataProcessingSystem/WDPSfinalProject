from ctransformers import AutoModelForCausalLM
repository = 'TheBloke/Llama-2-13B-chat-GGUF'
model_file = 'llama-2-13b-chat.Q4_K_M.gguf'
llm = AutoModelForCausalLM.from_pretrained(repository, model_file=model_file, model_type='llama')

def gen_raw_answer(question_id, question):
    raw_answer = llm(question)
    print('Raw Answer: ' + raw_answer)
    # write raw answer
    with open('answer.txt', 'a') as answer_file:
        answer_file.write(question_id + '    R' + '"' + raw_answer + '"' + '\n')
    return raw_answer