from transformers import AutoTokenizer
import json
import pandas as pd
import numpy as np
from transformers import AutoModelForQuestionAnswering, TrainingArguments, Trainer
from transformers import DefaultDataCollator
import entityRecognizer 
import answer_yes_no
import torch
import questionClassify

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
train=pd.read_csv(r"D:\DZLY6\P2\WEB\dataset\WDPS_TRAIN.CSV")
test=pd.read_csv(r"D:\DZLY6\P2\WEB\dataset\WDPS_TEST.CSV")
model_path = "D:\DZLY6\P2\WEB\model_distilbert_uncased"
model_save_path="D:\DZLY6\P2\WEB\model_save"

class answer_extraction:
    
    def __init__(self,question,raw_answer):
        self.question=question
        self.raw_answer=raw_answer
        self.model_path=model_path
        self.train=train
        self.tokenizer=tokenizer
        self.test=test
        self.model_save_path=model_save_path
        self.load_model(question,raw_answer)
       

    def load_model(self,question,raw_answer):
        print("###Answer Extraction Model Loading...")
        qc=questionClassify.QuestionClassify()
        type=qc.classify_question(question)
        answer=""
        #if it is yes-no question
        if type==0:
            print("###It is yes-no question...")
            # berttokenizer, bert = answer_yes_no.load_bert()
            # answer=answer_yes_no.answer_yes_no_question(question, bert, berttokenizer)
            #check logic
            if self.is_affirmative_answer(raw_answer):
                answer="yes"
            else:
                answer="no"
           
        #if it is entity question
        else:
            print("###It is enetity answer question...")
            
            #try to load model
            try:
                model = AutoModelForQuestionAnswering.from_pretrained(self.model_save_path)
                # check if model is successfully loaded
               
                print("model is successfully loaded.")
                answer=self.load_and_predict(model,question,raw_answer,self.model_save_path)
               
                    
            except Exception as e:
                # if model is not loaded, train and predict
                print("model is training.")
                answer=self.train_and_predict(question,self.model_save_path,raw_answer)
            #double extraction
            entRog=entityRecognizer.EntityRecognizer(question,False,'question--test')
            disambiguationquestion=entRog.return_disambiguated_entities()
            entitiesquestion = [item['entity'] for item in disambiguationquestion]
            enRogAn=entityRecognizer.EntityRecognizer(raw_answer,False,'question--test')
            disambiguationanswer=enRogAn.return_disambiguated_entities()
            entitiesanswer = [item['entity'] for item in disambiguationanswer]
            #check if answer is in question
            answer_in_entities = any(answer.lower() == entity.lower() for entity in entitiesquestion)
        #if model's answer is included in question
            if answer_in_entities:
                answer=entitiesanswer[0]
       
            entitiesanswer_in_entities = any(entitiesanswer[0].lower() == entity.lower() for entity in entitiesquestion)
         #if entity answer is not included in question
            if entitiesanswer_in_entities is False:
                answer=entitiesanswer[0]                                 
        print("Answer is: " + answer)
        print("###Answer Extraction Model Loading Finished...")
                          
        return answer
        
    def load_and_predict(self, model, question, raw_answer, model_save_path):
        tokenizer = tokenizer
        question = question
        context = raw_answer
        inputs = tokenizer.encode_plus(question, context, add_special_tokens=True, return_tensors="pt")
        answer=""
        # predict
        with torch.no_grad():
            outputs = model(**inputs)

    # decode
            start_index = torch.argmax(outputs.start_logits)
            end_index = torch.argmax(outputs.end_logits) + 1
            answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs['input_ids'][0][start_index:end_index]))

        return answer


    def train_and_predict(self,question,model_save_path,raw_answer):
            self.traindata=self.preprocess_function(train)
            self.testdata=self.preprocess_function(test)
        

            self.data_collator = DefaultDataCollator()

            self.train_dataset = [dict(zip(self.traindata,t)) for t in zip(*self.traindata.values())]
            self.test_dataset = [dict(zip(self.testdata,t)) for t in zip(*self.testdata.values())]

            
            self.model = AutoModelForQuestionAnswering.from_pretrained(self.model_path)

            trainer= self.trainmodel(self.model,self.train_dataset,self.test_dataset,self.data_collator)
             # create a dataframe containing a single question
            single_question_df = pd.DataFrame({
                "Question": [question],
                "GenAnswer_raw": [raw_answer],
                "answers": ['{"answer_start": [0], "text": [""]}']  # dummy answers
            })
            preprocessed_testdata = self.preprocess_function(single_question_df)
            test_dataformate = [dict(zip(preprocessed_testdata, t)) for t in zip(*preprocessed_testdata.values())]
            predictions = trainer.predict(test_dataformate)
            answers = self.get_predictions(test_dataformate, predictions)
            
           
        
           
            return answers[0]


    def preprocess_function(self,df):
        questions = [str(q).strip() for q in df["Question"]]
        gen_answers = [str(a) for a in df["GenAnswer_raw"]]

        inputs = tokenizer(
            questions,
            gen_answers,
            max_length=384,
            truncation="only_second",
            return_offsets_mapping=True,
            padding="max_length",
        )
        
        offset_mapping = inputs.pop("offset_mapping")
        start_positions = []
        end_positions = []

        for i, (offset, answer) in enumerate(zip(offset_mapping, df["answers"])):
            try:
                answer = json.loads(answer.replace("'", "\""))
                # answer_start is relative to GenAnswer_raw
                start_char = answer["answer_start"][0] if isinstance(answer["answer_start"], list) else answer["answer_start"]
                end_char = start_char + len(answer["text"])
            except (ValueError, TypeError, KeyError, json.JSONDecodeError):
                start_positions.append(0)
                end_positions.append(0)
                continue

            # Find the token index corresponding to the start and end character positions of the answer
            token_start_index, token_end_index = None, None
            for j, (start, end) in enumerate(offset):
                if (token_start_index is None) and start <= start_char < end:
                    token_start_index = j
                if start < end_char <= end:
                    token_end_index = j
                    break

            # Handle cases where answer is not found in the tokenized context
            if token_start_index is None or token_end_index is None:
                start_positions.append(0)
                end_positions.append(0)
            else:
                start_positions.append(token_start_index)
                end_positions.append(token_end_index)
            #debug
            # print(f"Row{i}  - GenAnswer: {gen_answers[i]}")
            # print(f"Row {i} - Answer: {answer}")
            # print(f"Row {i} - Start char: {start_char}, End char: {end_char}")
            # print(f"Row {i} - Token start: {token_start_index}, Token end: {token_end_index}")

        inputs["start_positions"] = start_positions
        inputs["end_positions"] = end_positions

        return inputs


    def trainmodel(self,model,train_dataset,test_dataset,data_collator):
        training_args = TrainingArguments(
        output_dir="D:\DZLY6\P2\WEB\output" ,
        evaluation_strategy="epoch",
        learning_rate = 2e-5,
        per_device_train_batch_size = 1,
        per_device_eval_batch_size = 1,
        num_train_epochs = 10,
        weight_decay = 0.01,
        report_to =[],
        push_to_hub = False)

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=test_dataset,
            tokenizer=tokenizer,
            data_collator=data_collator,
        )
        training_params = {
            "output_dir": training_args.output_dir,
            "evaluation_strategy": training_args.evaluation_strategy,
            "learning_rate": training_args.learning_rate,
            "train_batch_size": training_args.per_device_train_batch_size,
            "eval_batch_size": training_args.per_device_eval_batch_size,
            "num_train_epochs": training_args.num_train_epochs,
            "weight_decay": training_args.weight_decay
        }
        #record current time
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        training_params["timestamp"] = current_time


        #save training arguments
        with open("training_process.json", "w") as file:
            json.dump(training_params, file, indent=4)

        #print training arguments   
        # print("Training parameters:")
        # print(json.dumps(training_args, indent=4))

        train_output=trainer.train()
        train_results = {
            "total_steps": train_output.global_step,
            "training_loss": train_output.training_loss,
            "metrics": train_output.metrics
        }

        # save training results
        with open("train_process.json", "w") as file:
            json.dump(train_results, file, indent=4)

        # print training results
        print("Training results:")
        print(json.dumps(train_results, indent=4))
        self.model.save_pretrained(self.model_save_path)
        return trainer
  
   



    def get_predictions(self,test_dataset, predictions):
        # get the predicted answer for each sample in the test dataset
        start_logits, end_logits = predictions.predictions

        answers = []
        for i in range(len(test_dataset)):
            # find the tokens with the highest `start` and `end` scores
            start_index = np.argmax(start_logits[i])
            end_index = np.argmax(end_logits[i])
            

            # get the tokens between the `start` and `end` index
            input_ids = test_dataset[i]['input_ids']
            #debug
            # print(f"Start index: {start_index}, End index: {end_index}")
            # print(f"Start token: {tokenizer.decode([input_ids[start_index]])}, End token: {tokenizer.decode([input_ids[end_index]])}")
            answer_tokens = input_ids[start_index:end_index + 1]
            answer = tokenizer.decode(answer_tokens, skip_special_tokens=True)
            answers.append(answer)
        print(answers)
        return answers

   
    
    def is_affirmative_answer(answer):
        affirmative_words = ["yes", "true", "correct", "absolutely", "certainly"]
        return any(word in answer.lower() for word in affirmative_words)



  




#for test
# question = "Is paris the capital of France?"
# answer1="No."
# question = "Where is the capital of Paris?"
# answer1="Managua is the capital city of Paris."
# answer_extraction(question,answer1)

       



    