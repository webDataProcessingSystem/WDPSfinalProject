from IOFunc import verbose, pipeline
from entityRecognizer import EntityRecognizer
import requests

wiki_url = "https://en.wikipedia.org/w/api.php"
TOTAL_MATCH = 3
sample_question = [{'q_id': 'question-001', 'question': 'Is Managua the capital of Nicaragua?'}, \
{'q_id': 'question-002', 'question': 'the capital of nicaragua is...'}]

sample_answer = [{'q_id': 'question-001', 'answer': 'Yes, Managua is the capital city of Nicaragua. It is located in the southwestern part of the country and is home to many \
important government buildings and institutions, including the President\'s office and the National Assembly. The city has a population of over one million people \
and is known for its vibrant cultural scene, historic landmarks, and beautiful natural surroundings.'},\
{'q_id':'question-002', 'answer':' "Prior to 1979, Nicaragua was known as the Republic of Nicaragua. It is a republic with a presidential system of government.\
The capital of Nicaragua is Managua.The capital of Nicaragua is Managua.What is the capital of nicar"'}]

def search_wiki( word: str, limitation: int = 20) -> list:
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'search',
        'srwhat': 'text',
        'srsearch': f'{word}',
        'srlimit': limitation
    }
    response = requests.Session().get(url = wiki_url, params= params)
    if response.status_code == 200:
        data = response.json()
        return data["query"]["search"]
    else:
        priint("failed to access wiki content in search_wiki()...")
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
    for ans in sample_answer[:1]:
        entRog = EntityRecognizer(ans['answer'], True, ans['q_id'])
        entRog.entity_extraction()
        entRog.entity_linking()
    
    

main()