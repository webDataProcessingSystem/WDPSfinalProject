import pandas as pd

def read_csv(generate_csv_path):
    df = pd.read_csv(generate_csv_path)
    return df


#function to find answer start
def find_answer_start(context, answer):
    if isinstance(context, str):
        # 如果是字符串，转换为小写
        context = context.lower()
    else:
        # 如果不是字符串（例如 NaN），返回 -1
        return -1

    # 同样确保 answer 是字符串并转为小写
    answer = answer.lower() if isinstance(answer, str) else ''

    # 查找答案的开始位置
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

    # 查看结果
    # print(df[['GenAnswer_raw', 'Answer', 'answers']])
    df.to_csv(index_csv_path, index=False)
    




