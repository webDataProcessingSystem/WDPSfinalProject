from questionClassify import QuestionClassify
from IOFunc import get_input
#qn_df_sub['Category'] = [0 if qn_df_sub[Answer]]
#qn_df_sub['Answer Vectors'] = pd.factorize(qn_df_sub['Answer'])[0]
#print(qn_df_sub.head())
sample_question = [{'q_id': 'question-001', 'question': 'Is Managua the capital of Nicaragua?'}, \
{'q_id': 'question-002', 'question': 'the capital of nicaragua is...'}]
qc = QuestionClassify()
q_list = get_input("../test/question.txt", True)
for q in q_list:
    print(qc.classify_question(q['question']))#, qc.generate_prefix_column(q['question'])