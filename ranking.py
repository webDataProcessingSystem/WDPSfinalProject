import requests
from typing import Dict
import nltk
from nltk.corpus import stopwords
import string
from bs4 import BeautifulSoup

wiki_url = "https://en.wikipedia.org/w/api.php"

# Context-independent features
def cal_popularity(candidate_dict: object) -> dict:
    if candidate_dict is None:
        return None
    
    session = requests.Session()
    res_dict = {}
    max_backlinks = 0
    for entity in candidate_dict.keys():
       
        # set the request parameters
        request_para = {          
            "action"        : "query",
            "format"        : "json",
            "list"          : "backlinks",  # NOTE here
            "bltitle"       : entity, 
            "bllimit"       : 'max',
            "blnamespace"   : 4,
            "blredirect"    : "False"
        }
        response = session.get(url=wiki_url, params=request_para)
        if not response: # if fails, try again
            time.sleep(3)
            response = session.get(url=wiki_url, params=request_para)
            if not response:
                res_dict[entity] = 0
                continue          # go to the next candi if still missing
        
        data = response.json()
        if "query" in data:
            backlinks = data["query"]["backlinks"]
            res_dict[entity] = len(backlinks)

def get_context(text: str, entity: str):
    text_tokens = nltk.word_tokenize(text)
    entity_tokens = nltk.word_tokenize(entity)
    stop_words = set(stopwords.words("english"))

    context = [w for w in text_tokens if w.lower() not in stop_words \
    and w not in string.punctuation \
    and len(w) > 1 \
    and w not in entity_tokens]
    return context

def cal_distance(text: str, entity: str):
    tokens = nltk.word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    filtered_tokens = [t for t in tokens if t.lower() not in stop_words and t not in string.punctuation]

    context = get_context(text, entity)
    entity_index = filtered_tokens.index(entity.split()[0])
    distance_dict = {}

    for index, word in enumerate(filtered_tokens):
        if word != entity:
            distance_dict[word] = abs(index - entity_index)
    
    largest_distance = max(distance_dict.values())

    norm_distance_dict = {}
    for word, distance in distance_dict.items():
        norm_distance_dict[word] = distance/largest_distance
    
    sum_of_distances = sum([d for w, d in norm_distance_dict.items() if w in context])
    # update the distance as weight (sum to 1)
    for word, distance in distance_dict.items():
        norm_distance_dict[word] = norm_distance_dict[word]/sum_of_distances
    return norm_distance_dict

def cal_jaccard(token_list1: list, token_list2: list) -> float:
    if len(token_list1) == 0 or len(token_list2) == 0:
        return 0
    token_set1 = set(token_list1)
    token_set2 = set(token_list2)
    min_value = len(token_set1.intersection(token_set2))
    max_value = len(token_set2.union(token_set2))
    return min_value/max_value
    
def get_wiki_page(url: str):
    response = requests.get(url).text
    soup = BeautifulSoup(response, 'lxml')

    print(soup)
    



text = "Yes, Managua is the capital city of Nicaragua."
entity = "Managua"
url = "http://en.wikipedia.org/wiki/National_Assembly_(Venezuela)"
get_wiki_page(url)
#print(cal_distance(text, entity))
