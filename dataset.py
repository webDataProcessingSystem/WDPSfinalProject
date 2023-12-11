
from clean_trainOWN import generate_answer_and_extract_entities 

# #model and tokenizer path
# tokenizer_path=r"D:\DZLY6\P2\WEB\model\tokenizer.json"
model_path = r"D:\DZLY6\P2\WEB\model_13b\llama-2-13b-chat.Q4_K_M.gguf"
generate_csv_path=r"D:\DZLY6\P2\WEB\dataset\WDPS_GENDATASET.CSV"
original_file=r"D:\DZLY6\P2\WEB\dataset\WDPS_DATASET.CSV"

generate_answer_and_extract_entities(original_file,generate_csv_path,model_path)
