import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
import pickle
import os
import re
from nltk.tokenize import word_tokenize
# 0 = yes/no question
# 1 = non-yes/no question

# disable the SettingWithCopyWarning
pd.options.mode.chained_assignment = None  # default='warn'

Be_words = ["is", "was", "be", "will", "are", "were", "has", "have", "had", "did", "do", "does", "whether", "can", "could", "would", "(y/n)", " (yes/no)"]

class QuestionClassify:
    def __init__(self):
        qn_df = pd.read_csv('../data/WDPS_GENDATASET.csv')
        qn_df = qn_df.iloc[:,:]
        qn_df['Question'] = qn_df['Question'].str[17:]
        self._qn_df_sub = qn_df[['Question', 'Answer']]
        self.train_model()
    
    def generate_category_column(self, row):
        """
        0: for yes/no question
        1: for non-yes/no question
        """
        # remove all unnecessary blanks 
        answer = row['Answer'].replace(" ", "")             
        if answer.lower() == "yes" or answer.lower() == "no":
            return 0
        else:
            return 1
    def generate_prefix_column(self, row):
        tokens = word_tokenize(row['Question']) if 'Question' in row else  word_tokenize(row)
        if len(tokens) >= 1 and tokens[0].lower() in Be_words:
            return 0
        else:
            return 1

    def train_model(self):
        self._qn_df_sub.loc[:, 'Category'] = self._qn_df_sub.apply(self.generate_category_column, axis = 1)
        self._qn_df_sub.loc[:, 'Prefix'] = self._qn_df_sub.apply(self.generate_prefix_column, axis = 1)
        #print(self._qn_df_sub)
        self._qn_df_sub = self._qn_df_sub[self._qn_df_sub['Question'].notnull()]
        self._vect = TfidfVectorizer(ngram_range = (2, 2)).fit(self._qn_df_sub['Question'])
        # Train test split
        X_train, X_test, y_train, y_test = train_test_split(self._qn_df_sub['Question'], self._qn_df_sub['Category'], test_size=0.3, random_state=0)
        train_vector = self._vect.transform(X_train)
        test_vector = self._vect.transform(X_test)

        # SVM
        self._model1 = SVC(kernel='linear', probability = True)
        self._model1.fit(train_vector, y_train)

        pred1 = self._model1.predict(test_vector)
        accuracy_score(pred1, y_test)

        # apply threshold
        max_prob, max_prob_args = [],[]
        prob = self._model1.predict_proba(test_vector)
        for i in range(len(prob)):
            max_prob.append(prob[i].max())
            if prob[i].max() > 0.7:
                max_prob_args.append(prob[i].argmax())
            else:
                max_prob_args.append(-1)

        a = pd.DataFrame(X_test)
        a['pred'] = max_prob_args
        a['actual'] = y_test
        a['max_prob'] = max_prob
        b = a[a['pred'] != -1]
        print(accuracy_score(b['pred'], b['actual']))

    def process_question(self, question: str) -> str:
        result = re.sub(r'[^a-zA-Z]', ' ', question)
        return result.lower()

    def classify_question(self, question: str):
        X = [self.process_question(question)] 
        question_vec = self._vect.transform(X)
        question_pred = self._model1.predict(question_vec)
    
        manual_result = self.generate_prefix_column(question)
        if question_pred[0] == manual_result:
            return question_pred[0]
        else:
            return manual_result  # TODO


"""
sample_question = [{'q_id': 'question-001', 'question': 'Is Managua the capital of Nicaragua?'}, \
{'q_id': 'question-002', 'question': 'the capital of nicaragua is...'}]
qc = QuestionClassify()
q_list = get_input("../test/question.txt", True)
for q in q_list:
    print(qc.classify_question(q['question']))#, qc.generate_prefix_column(q['question'])
"""