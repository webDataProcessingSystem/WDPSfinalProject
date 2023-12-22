from IOFunc import verbose, pipeline
from entityRecognizer import EntityRecognizer
import requests
from bs4 import BeautifulSoup

wiki_url = "https://en.wikipedia.org/w/api.php"
TOTAL_MATCH = 3
sample_question = [{'q_id': 'question-001', 'question': 'Is Managua the capital of Nicaragua?'}, \
{'q_id': 'question-002', 'question': 'the capital of nicaragua is...'}]

sample_answer = [{'q_id': 'question-001', 'answer': 'Yes, Managua is the capital city of Nicaragua. It is located in the southwestern part of the country and is home to many \
important government buildings and institutions, including the President\'s office and the National Assembly. The city has a population of over one million people \
and is known for its vibrant cultural scene, historic landmarks, and beautiful natural surroundings.'},\
{'q_id':'question-002', 'answer':' "Prior to 1979, Nicaragua was known as the Republic of Nicaragua. It is a republic with a presidential system of government.\
The capital of Nicaragua is Managua.The capital of Nicaragua is Managua.What is the capital of nicar"'}]

q = [{'q_id': 'question-003', 'question': "Where is the capital of Paris?"}]
def main():
    #pipeline(sample_question)、
    """
    entity = 'National Assembly' 
    wiki_candidates = search_wiki(entity+ '+Nicaragua')
    candidates = []
    for cand in wiki_candidates:     
        candidates.append({
            'title': cand['title'], # may contain () as disambiguation
            'pageid': cand['pageid'],
            'score': 1 + TOTAL_MATCH if entity in cand['title'] else 1
        })
    print(candidates)
    """
    for ans in q:
        entRog = EntityRecognizer(ans['question'], False, ans['q_id'])
        #entRog.entity_extraction()
        #entRog.entity_linking()
        disambiguated_entities = entRog.return_disambiguated_entities()
        print(disambiguated_entities)
    
    
def get_wiki_link(pageid: int):
    link = "https://en.wikipedia.org/w/api.php?action=query&pageids=" + str(pageid) + "&format=json&formatversion=2&prop=info|extracts&inprop=url"
    response = requests.Session().get(url = link)
    if response.status_code == 200:
        data = response.json()
        print(data.keys())
        return data['query']['pages'][0]
    return '' 

import time
"""
import multiprocessing
import time
start_time = time.time()
threads = 4

jobs = []
for i in range(threads):
    thread = multiprocessing.Process(target=main())
    jobs.append(thread)

for j in jobs:
    j.start()

for j in jobs:
    j.join()
print("Processess complete." + str(time.time() - start_time))
"""
#print(get_wiki_link(57042))
start_time = time.time()
main()
print("Without Processes complete." + str(time.time() - start_time))
