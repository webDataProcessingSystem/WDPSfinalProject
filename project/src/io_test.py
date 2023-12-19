from IOFunc import write_ouput
question = {'q_id': 'question-001', 'question': 'Is Managua the capital of Nicaragua?',
'raw_answer':'Most people think Managua is the capital of Nicaragua. However, Managua is not the capital of Nicaragua.',
'answer': 'no',
'answer_checked': 'incorrect',
'entities': [{'entity': 'Nicaragua', 'wiki_link':'https://en.wikipedia.org/wiki/Nicaragua'},
{'entity': 'Nicaragua', 'wiki_link':'https://en.wikipedia.org/wiki/Nicaragua'}]
}
write_ouput("../test/output.txt", question['q_id'], question['raw_answer'], question['answer'], question['answer_checked'], question['entities'])