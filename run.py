
from ner import extract_entities_from_json


#model and tokenizer path
tokenizer_path=r"D:\DZLY6\P2\WEB\model\tokenizer.json"
model_path = r"D:\DZLY6\P2\WEB\model"


#dataset and extact entities path
json_file = 'D:\DZLY6\P2\WEB\Ass\GrailQA_v1.0\GrailQA_v1.0\grailqa_v1.0_train.json'
output_file = r'D:\DZLY6\P2\WEB\Ass\train.csv'
extract_entities_from_json(json_file,output_file,model_path,tokenizer_path)