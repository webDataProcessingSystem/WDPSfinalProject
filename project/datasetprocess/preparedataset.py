import pandas as pd

def read_csv(generate_csv_path):
    df = pd.read_csv(generate_csv_path)
    return df


#function to find answer start
def find_answer_start(context, answer):
    if isinstance(context, str):
        # if context is a string, make it lowercase
        context = context.lower()
    else:
        # if context is not a string, return -1
        return -1

    # if answer is a string, make it lowercase
    answer = answer.lower() if isinstance(answer, str) else ''

    # look for answer in context
    return context.find(answer)

# function to generate answers
def generate_answers(row):
    context = row['GenAnswer_raw']
    answer = row['Answer']
    answer_start = find_answer_start(context, answer)
    return {'text': [answer], 'answer_start': [answer_start]}

# apply function to generate answers
def call(generate_csv_path,index_csv_path):

    df= read_csv(generate_csv_path)
    df['answers'] = df.apply(generate_answers, axis=1)

    # for debug
    # print(df[['GenAnswer_raw', 'Answer', 'answers']])
    df.to_csv(index_csv_path, index=False)
    




