import os
from argparse import ArgumentParser
import argparse
from src.IOFunc import get_input, verbose, pipeline
from src.entityRecognizer import EntityRecognizer
from src.answer_extraction import answer_extraction
from src.questionClassify import QuestionClassify
import src.fact_check

if __name__ == "__main__":
    parser = ArgumentParser(
        prog="WDPS Practical Assignment",
        description="Team 11: Work for entity extraction and fact checking..")
    parser.add_argument("-i", "--input", type=str, help="input filename", required=True)
    parser.add_argument("-o", "--output", type=str, default="output.txt", help="input filename")
    parser.add_argument("-v", "--verbose", action="store_true")  # on/off flag

    
    args = parser.parse_args()
    verbose("### 1> Hello, welcome to start our program :)... ", args.verbose)

    q_list = get_input("test/" + args.input, args.verbose) # TODO, default directory set as test

    for q in q_list:
        pipeline(q['q_id'], q['question'], args.verbose)

    #print(q_list)
    
    

    
