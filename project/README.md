# Entity Disambiguation and Fact Checking
This is a pratical assignmnet for Web Data Processing Systems course.
## Brief Descriptions of the assignment
1. Receiving a question and get the answer from a large language model(LLM).
2. Extracting clean answer and identifying the correctness of answer given by LLM.
3. Extracting entities from question and answer, disambiguateing them and giving out their corresponding wiki links.
### Instructions
> You are called to implement a program that receives as input a question (or more in general a text to be completed), which we henceforth call A and returns as output four things: <br />
> 1. The raw text returned by a large language model (that is, what you would get if you query the language model as is). We call it B  <br />
> 2. The answer extracted from B. This answer can be of two types: either yes/no or a Wikipedia entity  <br />
> 3. The correctness of the extracted answer (correct/incorrect)  <br />
> 4. Entities that have been extracted from A and B  <br />
### Format of I/O
> **[Input (A)]**: "is Managua the capital of Nicaragua?" <br />
> **[Text returned by the language model (B) (llama 2, 70B)]**: "Yes, Managua is the capital city of Nicaragua. It is located in the southwestern part of the country and is home to many important government buildings and institutions, including the President's office and the National Assembly. The city has a population of over one million people and is known for its vibrant cultural scene, historic landmarks, and beautiful natural surroundings." <br />
> **[Extracted answer]**: "yes" <br />
> **[Correctness of the answer]**: "correct" <br />
> **[Entities extracted]**: <br />
> Nicaragua<TAB>https://en.wikipedia.org/wiki/Nicaragua <br />
> Managua<TAB>https://en.wikipedia.org/wiki/Managua <br />
> President's office<TAB>https://en.wikipedia.org/wiki/President_of_Nicaragua <br />
> National Assembly<TAB>https://en.wikipedia.org/wiki/National_Assembly_(Nicaragua) <br />
## Usage of this program (with Docker)
### Docker pull
```
docker pull cedar3/wdps:team11
```
### Run docker image
```
docker run -it cedar3/wdps
```
### Copy an input file into the Docker container
```
docker cp <yourinputfile> <container_id>:/wdps2/test/input.txt
```
### After running the docker image, just run
```
python starter.py -i input.txt [-o output.txt] [-v]
```
`-o output.txt` is an optional command to specify the output filename <br />
`-v` is an optional tag to specify whether showing the extra running information in the terminal
## Usage of this program (without Docker)
LLM used is accessible at https://huggingface.co/TheBloke/GEITje-7B-chat-GGUF/blob/main/geitje-7b-chat.Q4_K_M.gguf <br />
Models can be downloaded at https://drive.google.com/file/d/1dBRk3_5WRQmX9AQmOIhiu75xAHuKTZ9v/view?usp=sharing. <br />
After `git clone`, just run
### Installation
```
pip -r requirements.txt
```
### Run program by using the example input file 'question.txt'
using `-v` to show the running information, output is in the test/output.txt if not specified
```
python starter.py -i question.txt [output.txt] -v
```
### If need single test with sample data for a specific python file, run
```
cd src
```
```
python er_test.py
```
## File Structure
----wdps2\ <br />
&emsp;&emsp;|----requirements.txt  
&emsp;&emsp;|----starter.py <br /> 
&emsp;&emsp;|----Dockerfile <br />
&emsp;&emsp;|----README.md <br />
&emsp;&emsp;|----test\ <br />
&emsp;&emsp;|&emsp;&emsp;|----question.txt <br />
&emsp;&emsp;|&emsp;&emsp;|----output.txt <br />
&emsp;&emsp;|----data\ <br />
&emsp;&emsp;|&emsp;&emsp;|----WDPS_GENDATASET.CSV <br />
&emsp;&emsp;|&emsp;&emsp;|----WDPS_TEST.CSV <br />
&emsp;&emsp;|&emsp;&emsp;|----WDPS_TRAIN.CSV <br />
&emsp;&emsp;|----src\ <br />
&emsp;&emsp;|&emsp;&emsp;|----questionClassify.py <br />
&emsp;&emsp;|&emsp;&emsp;|----fact_check.py <br />
&emsp;&emsp;|&emsp;&emsp;|----qc_test.py <br />
&emsp;&emsp;|&emsp;&emsp;|----er_test.py <br />
&emsp;&emsp;|&emsp;&emsp;|----answer_extraction.py <br />
&emsp;&emsp;|&emsp;&emsp;|----IOFunc.py <br />
&emsp;&emsp;|&emsp;&emsp;|----io_test.py <br />
&emsp;&emsp;|&emsp;&emsp;|----entityRecognizer.py <br />
&emsp;&emsp;|----llm\ <br />
&emsp;&emsp;|&emsp;&emsp;|----llama-2-7b-chat.Q4_K_M.gguf <br />
&emsp;&emsp;|----model\ <br />
&emsp;&emsp;|&emsp;&emsp;|----model_qc <br />
&emsp;&emsp;|&emsp;&emsp;|----model_distilbert_uncased <br />
&emsp;&emsp;|&emsp;&emsp;|----mode_answer_ex_save <br />
