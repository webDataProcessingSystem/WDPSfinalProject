
from clean_trainOWN import generate_answer_and_extract_entities 
from preparedataset import call
from split_dataset import split
#path
model_path = r"D:\DZLY6\P2\WEB\model_13b\llama-2-13b-chat.Q4_K_M.gguf"
generate_csv_path=r"D:\DZLY6\P2\WEB\dataset\WDPS_GENDATASET.CSV"
original_file=r"D:\DZLY6\P2\WEB\dataset\WDPS_DATASET.CSV"
index_csv_path=r"D:\DZLY6\P2\WEB\dataset\WDPS_INDEX.CSV"

#process

#generate_answer_and_extract_entities(original_file,generate_csv_path,model_path)
# call(generate_csv_path,index_csv_path)
split(index_csv_path,r"D:\DZLY6\P2\WEB\dataset\WDPS_TRAIN.CSV",r"D:\DZLY6\P2\WEB\dataset\WDPS_TEST.CSV")