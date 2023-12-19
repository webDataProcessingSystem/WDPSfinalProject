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
## Usage of this problem
### Installation
### How to use in terminal?
```
python starter.py -i input.txt [output.txt] [-v]
```